# -*- coding: utf-8 -*-
"""Compare bsl-ls JSON report against the Sonar 52-issue target set."""
import collections
import json
import sys

REP = 'tmp/night/lsreport/bsl-json.json'

SONAR_FILES = {
    'CommonModules/Тх_ТехникаСервер/Ext/Module.bsl',
    'CommonModules/Тх_Тесты/Ext/Module.bsl',
    'DataProcessors/Тх_ЗапускVanessa/Ext/ObjectModule.bsl',
    'DataProcessors/Тх_РаннерТестов/Ext/ObjectModule.bsl',
    'DataProcessors/Тх_ПодготовкаТестовыхДанных/Ext/ObjectModule.bsl',
    'DataProcessors/Тх_ФормированиеПланаРаботТехники/Forms/Форма/Ext/Form/Module.bsl',
    'Reports/Тх_ДефицитТехники/Ext/ObjectModule.bsl',
}

# rule name -> how many of them Sonar reported (52 total)
TARGET = {
    'UsageWriteLogEvent': 4,
    'QueryParseError': 4,
    'NestedFunctionInParameters': 2,
    'CognitiveComplexity': 4,
    'CyclomaticComplexity': 2,
    'NestedStatements': 1,
    'LineLength': 2,
    'JoinWithVirtualTable': 1,
    'MagicNumber': 14,
    'Typo': 6,
    'DeprecatedMethodCall': 8,   # bsl-ls name of DeprecatedMethods8317
    'DeprecatedFind': 1,
    'NumberOfValuesInStructureConstructor': 1,
    'CodeOutOfRegion': 1,
    'StyleElementConstructors': 1,
}

SEP = 'ПланированиеТехникиАПК/'


def norm(path):
    p = path.replace(chr(92), '/')
    return p.split(SEP)[-1] if SEP in p else p


def main():
    rep = json.load(open(REP, encoding='utf-8'))
    infos = rep.get('fileinfos') or rep.get('files') or []
    rows = []
    for fi in infos:
        path = norm(fi.get('path') or fi.get('file') or '')
        for d in fi.get('diagnostics') or []:
            code = (d.get('code') or '').split(':')[-1]
            rng = (d.get('range') or {}).get('start') or {}
            line = rng.get('line', 0) + 1
            rows.append((path, code, d.get('severity'), line, (d.get('message') or '')[:80]))
    sys.stdout.write('total diagnostics: %d\n' % len(rows))

    cnt = collections.Counter()
    sys.stdout.write('\n=== target-rule leftovers in the 7 Sonar files ===\n')
    for path, code, sev, line, msg in rows:
        if path in SONAR_FILES and code in TARGET:
            cnt[(path, code)] += 1
            sys.stdout.write('  %-32s %s:%d  %s\n' % (code, path, line, msg))

    sys.stdout.write('\n=== leftovers by rule (was -> now) ===\n')
    now = collections.Counter(c for (p, c) in cnt.elements())
    for rule in sorted(TARGET):
        sys.stdout.write('  %-34s %2d -> %2d\n' % (rule, TARGET[rule], now.get(rule, 0)))
    sys.stdout.write('\nTOTAL target issues: %d -> %d\n'
                     % (sum(TARGET.values()), sum(now.values())))


main()
