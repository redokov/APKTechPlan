# -*- coding: utf-8 -*-
# Pre-load validation of CFE XML sources before loading into DB.
# Adapted from 1cDevTry/scripts/pre_load_validate.py (same 4 checks),
# target dir taken from argv (default: this project's extension).
#
# Checks all XML under src/cfe/<ext>/:
#   1. <v8:NumberQualifiers> contains <v8:Digits>, not <v8:Precision>
#   2. <EventSubscription><Source> non-empty when event is object-type
#   3. Every <Resource>/<Attribute>/<Dimension> has <Name> in <Properties>
#      (plus <TabularSection> and document <Attribute> of ChildObjects forms)
#   4. XML well-formedness (ET.parse covers it)

import os
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_BASE = os.path.join(ROOT, 'src', 'cfe', u'\u041f\u043b\u0430\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435\u0422\u0435\u0445\u043d\u0438\u043a\u0438\u0410\u041f\u041a')

MD = '{http://v8.1c.ru/8.3/MDClasses}'
V8 = '{http://v8.1c.ru/8.1/data/core}'

errors = []


def check(path):
    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        errors.append('%s: XML parse error: %s' % (path, e))
        return
    root = tree.getroot()

    # 1. NumberQualifiers
    for q in root.iter(V8 + 'NumberQualifiers'):
        children = [c.tag for c in q]
        if V8 + 'Digits' not in children:
            errors.append('%s: NumberQualifiers without v8:Digits' % path)
        if V8 + 'Precision' in children:
            errors.append('%s: NumberQualifiers uses v8:Precision' % path)

    # 2. EventSubscription Source
    es = root.find(MD + 'EventSubscription')
    if es is not None:
        props = es.find(MD + 'Properties')
        if props is not None:
            source = props.find(MD + 'Source')
            types = [t.text for t in source.iter(V8 + 'Type') if t.text] if source is not None else []
            event = props.find(MD + 'Event')
            event_text = event.text if event is not None and event.text else ''
            object_type_events = ('BeforeWrite', 'AfterWrite', 'OnWrite', 'BeforeDelete')
            if event_text in object_type_events and not types:
                errors.append('%s: object-type event without Source types' % path)

    # 3. Resource/Attribute/Dimension/TabularSection have Name
    for kind in ('Resource', 'Attribute', 'Dimension', 'TabularSection'):
        for obj in root.iter(MD + kind):
            props = obj.find(MD + 'Properties')
            if props is None:
                errors.append('%s: %s without Properties' % (path, kind))
                continue
            name = props.find(MD + 'Name')
            if name is None or not name.text:
                errors.append('%s: %s without Name' % (path, kind))


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASE
    if not os.path.isabs(base):
        base = os.path.normpath(os.path.join(ROOT, base))
    if not os.path.isdir(base):
        print('CFE base dir not found: %s' % base)
        sys.exit(1)
    n = 0
    for dirpath, _dirnames, filenames in os.walk(base):
        for fn in filenames:
            if fn.endswith('.xml'):
                full = os.path.join(dirpath, fn)
                check(full)
                n += 1
    if errors:
        for e in errors:
            print('ERROR: %s' % e)
        sys.exit(1)
    print('All CFE XML validated OK (%d files under %s)' % (n, base))
    sys.exit(0)


if __name__ == '__main__':
    main()
