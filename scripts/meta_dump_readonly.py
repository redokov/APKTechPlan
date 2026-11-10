#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only metadata dumper over the main-configuration XML dump (APKModSrc).

Usage (paths relative to APKModSrc or absolute):
  PYTHONIOENCODING=utf-8 python scripts/meta_dump_readonly.py <relpath> [<relpath> ...]

Prints: object kind/name, selected properties, dimensions/resources/attributes,
tabular sections with their attributes and types. Nothing is written anywhere.
"""
import sys
import os
import xml.etree.ElementTree as ET

NS = {"m": "http://v8.1c.ru/8.3/MDClasses"}
ROOT = os.environ.get("APK_SRC_ROOT", r"C:\MyProjects\APKModSrc")

SKIP_PROPS = {
    "Name", "Synonym", "Comment", "ToolTip", "InputHint", "Explanation",
    "AuxiliaryRecordForm", "AuxiliaryListForm", "AuxiliaryObjectForm",
    "AuxiliaryChoiceForm", "StandardAttributes", "Numerator", "Characteristics",
    "BasedOn", "InputByString", "RegisterRecords", "DataLockFields",
    "RecordPresentation", "ExtendedRecordPresentation", "ListPresentation",
    "ExtendedListPresentation", "ObjectPresentation", "ExtendedObjectPresentation",
}

KINDS = (
    "InformationRegister", "AccumulationRegister", "Document", "Catalog",
    "Enum", "DataProcessor", "Report", "Constant", "CommonModule",
    "CalculationRegister", "AccountingRegister", "BusinessProcess", "Task",
)


def local(tag):
    return tag.split("}")[-1]


def type_names(el):
    """Collect textual type names from a Type element subtree."""
    names = []
    if el is None:
        return names
    for node in el.iter():
        ln = local(node.tag)
        if ln in ("Type", "TypeSet") and node.text and node.text.strip():
            names.append(node.text.strip())
    return names


def print_props(obj, limit=40):
    props = obj.find("m:Properties", NS)
    if props is None:
        return
    shown = 0
    for ch in props:
        tag = local(ch.tag)
        if tag in SKIP_PROPS:
            continue
        txt = (ch.text or "").strip()
        if not txt:
            continue
        if len(txt) > 70:
            txt = txt[:70] + "..."
        print("  P %-34s = %s" % (tag, txt))
        shown += 1
        if shown >= limit:
            return


def print_children(container, kind_label):
    if container is None:
        return
    for el in container:
        if local(el.tag) != kind_label:
            continue
        nm = el.find("m:Properties/m:Name", NS)
        ty = el.find("m:Properties/m:Type", NS)
        extra = ""
        if kind_label == "TabularSection":
            extra = ""
        print("  %-18s %-34s %s" % (kind_label, nm.text if nm is not None else "?",
                                    ("types=" + ",".join(type_names(ty))) if ty is not None else ""))
        if kind_label == "TabularSection":
            print_children(el.find("m:ChildObjects", NS), "Attribute")


def dump(path):
    full = path if os.path.isabs(path) else os.path.join(ROOT, path)
    root = ET.parse(full).getroot()
    for kind in KINDS:
        obj = root.find(".//m:" + kind, NS)
        if obj is None:
            continue
        nm = obj.find("m:Properties/m:Name", NS)
        print("===== %s :: %s (%s)" % (kind, nm.text if nm is not None else "?", os.path.basename(full)))
        print_props(obj)
        kids = obj.find("m:ChildObjects", NS)
        for label in ("Dimension", "Resource", "Attribute", "TabularSection", "Column", "EnumValue"):
            print_children(kids, label)
        return
    print("===== UNKNOWN KIND:", path)


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    for p in args:
        dump(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
