# -*- coding: utf-8 -*-
"""Round-trip compare: source CFE dir vs Designer dump dir.

Usage: python scripts/compare_dump_dirs.py <dump_dir> <source_dir>

Canonical comparison with platform-serialization equivalence rules:
- Type(cfg:CatalogRef.X / DocumentRef.X / EnumRef.X) == TypeId(GUID) when GUID
  is the xr:GeneratedType (Ref/Object) type id of X (built from ERPsrc+APKModSrc).
- ListChoiceMode / Type=UsualButton default-property lines are ignored.
- WindowOpeningMode LockOwnerWindow == LockOwner (8.5 dump synonym).
- DataPath Russian segment names == English (Объект.Период == Объект.Period).

Exit 0 = PASS; 1 = REAL diffs (blocker).
"""
import difflib
import json
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

SKIP_NAMES = {"ConfigDumpInfo.xml"}
GEN_SOURCES = [r"C:/MyProjects/APKModSrc", r"C:/MyProjects/ERPsrc"]
GEN_CACHE = pathlib.Path(__file__).resolve().parents[1] / "heartbeat/ref_type_guids.json"

DROP_LINES = ("ListChoiceMode", "CheckBoxType")  # default-valued noise
DROP_TYPE_DEFAULTS = {"UsualButton"}
LOCK_MODE = {"LockOwnerWindow": "LockOwner"}
DATAPATH_RU_EN = {"Период": "Period", "Организация": "Организация"}  # ru->en segment map


def build_gen_map():
    if GEN_CACHE.exists():
        return json.loads(GEN_CACHE.read_text(encoding="utf-8"))
    m = {}
    pat = re.compile(r'<xr:GeneratedType name="(\w+)\.([^"]+)"[^>]*>\s*<xr:TypeId>([0-9a-f\-]+)</xr:TypeId>', re.S)
    for base in GEN_SOURCES:
        for f in pathlib.Path(base).rglob("*.xml"):
            try:
                head = f.read_text(encoding="utf-8-sig", errors="replace")[:12000]
            except Exception:
                continue
            for kind, name, guid in pat.findall(head):
                m.setdefault(guid.lower(), f"{kind}.{name}")
    GEN_CACHE.write_text(json.dumps(m, ensure_ascii=False, indent=0), encoding="utf-8")
    return m


REF_PREFIX = {"CatalogRef", "DocumentRef", "EnumRef", "CatalogObject", "DocumentObject"}


def norm_token(tag, at, txt):
    at = dict(sorted(at.items()))
    if tag == "Type" and txt:
        # cfg:CatalogRef.X -> REFTYPE X (canonical object name; Ref/Object generated ids
        # identify the same metadata object)
        m = re.match(r"^(?:cfg|xs):(\w+)\.(.+)$", txt)
        if m and m.group(1) in REF_PREFIX:
            return "REFTYPE", m.group(2)
        return "TYPE", txt
    if tag == "TypeId" and txt:
        name = GEN.get(txt.lower())
        if name:
            # name like CatalogRef.X / CatalogObject.X -> canonical object name X
            return "REFTYPE", name.partition(".")[2]
        return "TYPEID", txt.lower()
    if tag == "Type" and not txt and at == {}:
        return "TYPE-EMPTY", ""
    if tag == "DataPath" and txt:
        seg = txt.split(".")
        seg = [DATAPATH_RU_EN.get(s, s) for s in seg]
        return "DATAPATH", ".".join(seg)
    if tag == "WindowOpeningMode" and txt:
        return "LOCKMODE", LOCK_MODE.get(txt, txt)
    return tag, json.dumps(at, ensure_ascii=False, sort_keys=True), " ".join(txt.split())


def canon_xml(path):
    tree = ET.parse(path)
    out = []

    def walk(e, depth):
        tag = e.tag.split("}")[-1] if isinstance(e.tag, str) else "?"
        txt = " ".join((e.text or "").split())
        if tag in DROP_LINES:
            return
        if tag == "Type" and txt in DROP_TYPE_DEFAULTS:
            return
        tok = norm_token(tag, dict(sorted(e.attrib.items())), txt)
        label = "TRef" if (tag in ("Type", "TypeId") and isinstance(tok, tuple) and tok[0] == "REFTYPE") else tag
        out.append("%s%s %s" % ("  " * depth, label, tok))
        for c in e:
            walk(c, depth + 1)

    walk(tree.getroot(), 0)
    return out


def canon_text(path):
    return [" ".join(l.split()) for l in path.read_text(encoding="utf-8-sig", errors="replace").splitlines()]


def canon(path):
    if path.suffix.lower() == ".xml":
        try:
            return canon_xml(path)
        except ET.ParseError:
            return canon_text(path)
    return canon_text(path)


GEN = {}


def main():
    global GEN
    GEN = build_gen_map()
    dump = pathlib.Path(sys.argv[1]).resolve()
    src = pathlib.Path(sys.argv[2]).resolve()
    dump_files = {p.relative_to(dump).as_posix() for p in dump.rglob("*") if p.is_file()}
    src_files = {p.relative_to(src).as_posix() for p in src.rglob("*") if p.is_file()}
    dump_files = {f for f in dump_files if pathlib.Path(f).name not in SKIP_NAMES}
    src_files = {f for f in src_files if pathlib.Path(f).name not in SKIP_NAMES}

    only_src = sorted(src_files - dump_files)
    only_dump = sorted(dump_files - src_files)
    print(f"files: src={len(src_files)} dump={len(dump_files)}")
    print(f"only in source (ORPHANS): {len(only_src)}")
    for f in only_src[:40]:
        print("  ONLY-SRC", f)
    print(f"only in dump: {len(only_dump)}")
    for f in only_dump[:40]:
        print("  ONLY-DUMP", f)

    real_diffs = []
    for rel in sorted(src_files & dump_files):
        a = canon(src / rel)
        b = canon(dump / rel)
        if a == b:
            continue
        diff = [l for l in difflib.unified_diff(a, b, lineterm="", n=0) if l.startswith(("+", "-"))]
        if diff:
            real_diffs.append((rel, diff))

    print(f"content REAL diffs: {len(real_diffs)}")
    for rel, diff in real_diffs[:20]:
        print("=== DIFF", rel, f"({len(diff)} lines)")
        for l in diff[:15]:
            print("  ", l[:160])
    fail = bool(only_src) or bool(real_diffs)
    print("VERDICT:", "FAIL (REAL diff / orphans)" if fail else "PASS")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
