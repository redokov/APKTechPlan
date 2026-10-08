# -*- coding: utf-8 -*-
"""Inventory of extension attributes: object -> attribute -> types.

Namespace-agnostic. Usage: python scripts/inventory_extension.py
Output: heartbeat/ext_inventory.txt (read with the read tool).
"""
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "src/cfe/ПланированиеТехникиАПК"
OBJ_TAGS = {"Document", "InformationRegister", "Report", "DataProcessor", "Catalog", "Enum"}


def loc(el):
    return el.tag.split("}", 1)[-1] if isinstance(el.tag, str) else ""


def child(el, name):
    for c in el:
        if loc(c) == name:
            return c
    return None


def children(el, name):
    return [c for c in el if loc(c) == name]


def text_of(el, name):
    c = child(el, name)
    return (c.text or "").strip() if c is not None and c.text else ""


def synonym(el):
    c = child(el, "Synonym")
    if c is None:
        return ""
    parts = []
    for item in c:
        t = child(item, "v8Item" ) or child(item, "item")
        if t is not None:
            parts.append("".join(t.itertext()).strip())
    # fallback: full itertext minus empty
    if not parts:
        parts = [x.strip() for x in c.itertext() if x.strip()]
    return " | ".join(parts)


def types_of(attr):
    t_el = child(attr, "Type")
    if t_el is None:
        return ["(no Type)"]
    res = []
    for c in t_el.iter():
        if loc(c) in ("Type", "TypeSet", "TypeRestricted", "TypeMaxExclusive"):
            if c.attrib:
                res.append(list(c.attrib.values())[0])
    return res or ["(empty Type)"]


def attr_info(el):
    props = child(el, "Properties")
    if props is None:
        props = el
    return text_of(props, "Name"), synonym(props), ", ".join(types_of(props))


def walk_attrs(container, out, indent):
    for attr in container:
        t = loc(attr)
        if t in ("Attribute", "Dimension", "Resource"):
            n, s, ty = attr_info(attr)
            out.append(f"{indent}{t}: {n} | syn: {s} | types: {ty}")
        elif t == "TabularSection":
            n, _, _ = attr_info(attr)
            out.append(f"{indent}TS: {n}")
            walk_attrs(attr, out, indent + "  ")


def dump_object(path, out):
    try:
        root = ET.parse(path).getroot()
    except Exception as e:
        out.append(f"!! parse error {path.name}: {e}")
        return
    obj = None
    for c in root.iter():
        if loc(c) in OBJ_TAGS:
            obj = c
            break
    if obj is None:
        return
    props = child(obj, "Properties") or obj
    out.append(f"=== {path.parent.name}/{path.name}")
    out.append(f"  name: {text_of(props, 'Name')} | syn: {synonym(props)}")
    for holder in obj.iter():
        if loc(holder) == "ChildObjects":
            walk_attrs(holder, out, "  ")


def main():
    out = []
    for sub in ("Documents", "InformationRegisters", "Reports", "DataProcessors", "Enums", "Catalogs"):
        d = ROOT / sub
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.xml")):
            dump_object(p, out)
    dest = Path(__file__).resolve().parents[1] / "heartbeat/ext_inventory.txt"
    dest.write_text("\n".join(out), encoding="utf-8")
    print(f"written {dest} ({len(out)} lines)")


if __name__ == "__main__":
    main()
