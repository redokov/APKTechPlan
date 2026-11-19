#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Map Sonar worklist (build #15, pre-wave6 revision) issues to CURRENT lines.

For each issue: take text of the flagged line at revision R15 (default
9555f0d), find occurrences of the same normalized text in the current file,
pick the one closest to the original line number.

Usage:
  PYTHONIOENCODING=utf-8 python3 scripts/wave6b_locate.py <file-substr> [--rules R1,R2] [--rev 9555f0d]
"""
import argparse
import json
import os
import re
import subprocess
import sys

REPO = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                      capture_output=True, text=True).stdout.strip()
WORKLIST = os.path.join(REPO, "tmp/wave6/sonar_open_worklist.json")


def norm(s):
    return re.sub(r"\s+", " ", s.strip())


def rev_lines(rev, rel):
    out = subprocess.run(["git", "show", "%s:%s" % (rev, rel)],
                         capture_output=True)
    raw = out.stdout
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    return raw.decode("utf-8").replace("\r\n", "\n").split("\n")


def cur_lines(path):
    raw = open(path, "rb").read()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    return raw.decode("utf-8").replace("\r\n", "\n").split("\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("substr")
    ap.add_argument("--rules", default="")
    ap.add_argument("--rev", default="9555f0d")
    a = ap.parse_args()
    rules = set(x.strip() for x in a.rules.split(",") if x.strip())

    d = json.load(open(WORKLIST, encoding="utf-8"))
    items = d if isinstance(d, list) else d.get("issues", d)

    groups = {}
    for i in items:
        comp = i.get("component", "")
        if a.substr not in comp:
            continue
        rule = (i.get("rule") or "").split(":")[-1]
        if rules and rule not in rules:
            continue
        groups.setdefault(comp, []).append(i)

    for comp, iss in sorted(groups.items()):
        rel = "src/cfe/\u041f\u043b\u0430\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435"
        # component like: APKTechPlan:src/cfe/ПланированиеТехникиАПК/CommonModules/...
        idx = comp.find("src/cfe/")
        rel = comp[idx:] if idx >= 0 else comp
        rel = rel.split(":", 1)[0]
        path = os.path.join(REPO, rel)
        if not os.path.exists(path):
            print("SKIP missing %s" % rel)
            continue
        try:
            base = rev_lines(a.rev, rel)
        except Exception as e:
            print("ERR rev_lines %s: %s" % (rel, e))
            continue
        cur = cur_lines(path)
        index = {}
        for n, t in enumerate(cur, 1):
            index.setdefault(norm(t), []).append(n)
        print("== %s  (issues=%d)" % (rel, len(iss)))
        out_rows = []
        gone = 0
        for i in iss:
            line = i.get("line") or 0
            rule = (i.get("rule") or "").split(":")[-1]
            msg = (i.get("message") or "").replace("\n", " ")
            if line and line - 1 < len(base):
                src = norm(base[line - 1])
            else:
                src = ""
            cands = index.get(src, []) if src else []
            if cands:
                cl = min(cands, key=lambda c: abs(c - line))
                out_rows.append((cl, line, rule, msg, cur[cl - 1].strip()))
            else:
                gone += 1
                out_rows.append((0, line, rule, msg, src or "?"))
        for cl, line, rule, msg, text in sorted(out_rows):
            tag = "L%-5d" % cl if cl else "GONE  "
            print("%s <-L%-5d | %-30s | %s | %s" % (tag, line, rule, msg[:100], text[:100]))
        print("   gone/unmapped: %d" % gone)


if __name__ == "__main__":
    sys.exit(main())
