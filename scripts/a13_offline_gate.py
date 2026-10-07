#!/usr/bin/env python3
"""A13 final offline gate for the CFE source tree.

Checks:
 1. ChildObjects of Configuration.xml == object directories (no orphans, no missing).
 2. SKD report query contains no references to main-configuration objects ("Apk" == 0).
 3. Rights.xml of every role grants rights ONLY on Tkh_ objects (NFR-004).
 4. Reports have no Ext/ObjectModule.bsl leftovers.
 5. NStr literals: odd double-quote count on NStr lines; "'')," pattern absent.
Exit 0 iff all checks pass.
(Run bsl_ls_fulltree.py and pre_load_validate.py separately - see docs.)
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

BASE = os.path.join("src", "cfe", "ПланированиеТехникиАПК")

KIND_TAGS = {
    "CommonModules": "CommonModule",
    "DataProcessors": "DataProcessor",
    "Documents": "Document",
    "Enums": "Enum",
    "InformationRegisters": "InformationRegister",
    "Reports": "Report",
    "Roles": "Role",
    "Subsystems": "Subsystem",
    "Languages": "Language",
}

failures = []


def ok(msg):
    print("  PASS " + msg)


def fail(msg):
    print("  FAIL " + msg)
    failures.append(msg)


def check_childobjects():
    cfg = io.open(os.path.join(BASE, "Configuration.xml"), encoding="utf-8-sig").read()
    listed = set(re.findall(r"<(\w+)>([^<]+)</\1>", cfg[cfg.find("<ChildObjects>"):]))
    # dirs or top-level metadata xml files on disk
    on_disk = set()
    for kind_dir, tag in KIND_TAGS.items():
        d = os.path.join(BASE, kind_dir)
        if not os.path.isdir(d):
            continue
        for entry in os.listdir(d):
            full = os.path.join(d, entry)
            if os.path.isdir(full):
                on_disk.add((tag, entry))
            elif entry.endswith(".xml"):
                on_disk.add((tag, entry[:-4]))  # object without directory (e.g. bare register, language)
    missing = on_disk - listed   # orphans on disk (won't load)
    extra = []
    for tag, name in (listed - on_disk):
        if tag in KIND_TAGS.values():
            extra.append((tag, name))
    if missing:
        fail("objects on disk missing from ChildObjects (orphans): %s" % sorted(missing))
    else:
        ok("every object directory is listed in ChildObjects (%d objects)" % len(on_disk))
    if extra:
        fail("ChildObjects entries without directory: %s" % sorted(extra))
    else:
        ok("every ChildObjects entry has a directory")


def check_skd_no_apk():
    hits = []
    for root, dirs, files in os.walk(os.path.join(BASE, "Reports")):
        for f in files:
            if f.endswith(".xml"):
                t = io.open(os.path.join(root, f), encoding="utf-8-sig").read()
                for m in re.findall(r"[Аа]пк\w*", t):
                    hits.append(os.path.join(root, f) + ": " + m)
    if hits:
        fail("SKD/report XML references main-config objects: %s" % hits)
    else:
        ok("no 'Apk' references in report XML (TD-003)")


def check_rights():
    bad = []
    roles = 0
    d = os.path.join(BASE, "Roles")
    for entry in os.listdir(d):
        p = os.path.join(d, entry)
        if not os.path.isdir(p):
            continue
        roles += 1
        rights = os.path.join(p, "Rights.xml") if os.path.isdir(p) else p
        # Designer layout: Rights.xml inside Ext/
        if not os.path.isfile(rights):
            rights = os.path.join(p, "Ext", "Rights.xml")
        if not os.path.isfile(rights):
            continue
        t = io.open(rights, encoding="utf-8-sig").read()
        for m in re.findall(r'Object\.(.+?)[.<"\s]', t):
            if not m.startswith("Тх_"):
                bad.append(entry + ": " + m)
    if bad:
        fail("roles grant rights to non-Tkh_ objects: %s" % sorted(set(bad)))
    else:
        ok("roles grant rights only to Tkh_ objects (%d roles)" % roles)


def check_reports_no_objectmodule():
    leftovers = []
    d = os.path.join(BASE, "Reports")
    for root, dirs, files in os.walk(d):
        for f in files:
            if f == "ObjectModule.bsl":
                leftovers.append(os.path.join(root, f))
    if leftovers:
        fail("reports must not have Ext/ObjectModule.bsl: %s" % leftovers)
    else:
        ok("no ObjectModule.bsl under Reports")


def check_nstr_literals():
    bad = []
    for root, dirs, files in os.walk(BASE):
        for f in files:
            if not f.endswith(".bsl"):
                continue
            p = os.path.join(root, f)
            lines = io.open(p, encoding="utf-8-sig").readlines()
            for i, line in enumerate(lines, 1):
                if "'')," in line:
                    bad.append("%s:%d glm quote bug pattern '(''," % (p, i))
            # multi-line-aware quote balance: walk statements with NStr
            j = 0
            while j < len(lines):
                if "НСтр" in lines[j] and '"' in lines[j]:
                    k = j
                    quotes = 0
                    while k < len(lines):
                        quotes += lines[k].count('"')
                        if quotes % 2 == 0 and quotes > 0:
                            break
                        k += 1
                    if k >= len(lines) or quotes % 2 != 0:
                        bad.append("%s:%d unbalanced quotes in NStr statement" % (p, j + 1))
                    j = k + 1
                else:
                    j += 1
    if bad:
        fail("NStr literal problems: %s" % bad)
    else:
        ok("NStr literals sane (no odd quotes, no '('', bug)")


def main():
    print("[A13 offline gate] tree: " + BASE)
    check_childobjects()
    check_skd_no_apk()
    check_rights()
    check_reports_no_objectmodule()
    check_nstr_literals()
    if failures:
        print("GATE FAILED (%d)" % len(failures))
        return 1
    print("GATE PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
