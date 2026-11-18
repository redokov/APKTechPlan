#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Locate Sonar worklist issues in the CURRENT file version.

Line numbers in the offline worklist refer to the analysis revision (== git
HEAD). After edits they shift, so this script maps every issue to the nearest
current line that still carries the same source text.

Usage:
  python scripts/wl_locate.py <worklist.md> <source.bsl> [--from N] [--to N]
                              [--rules R1,R2] [--pending]

Output (descending line order, ready for bottom-up batching):
  L<cur> | <rule> | <severity> | <message> | <source>
Issues whose original text is no longer present are reported as GONE (already
edited) and omitted.
"""
import argparse
import os
import re
import subprocess
import sys

RE_ITEM = re.compile(r"^- L(\d+) \| ([A-Za-z]+) \| ([A-Z]+) \| (.*)$")


def norm(s):
    return re.sub(r"\s+", " ", s.strip())


def baseline_lines(path):
    """Text of the file at git HEAD."""
    repo = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                          capture_output=True, text=True).stdout.strip()
    rel = os.path.relpath(os.path.abspath(path), repo).replace("\\", "/")
    out = subprocess.run(["git", "show", "HEAD:%s" % rel],
                         capture_output=True)
    raw = out.stdout
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    return raw.decode("utf-8").replace("\r\n", "\n").split("\n")


def current_lines(path):
    raw = open(path, "rb").read()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    return raw.decode("utf-8").replace("\r\n", "\n").split("\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("worklist")
    ap.add_argument("source")
    ap.add_argument("--from", dest="lo", type=int, default=0)
    ap.add_argument("--to", dest="hi", type=int, default=10 ** 9)
    ap.add_argument("--rules", default="")
    ap.add_argument("--asc", action="store_true")
    a = ap.parse_args()

    rules = set(x.strip() for x in a.rules.split(",") if x.strip())
    base = baseline_lines(a.source)
    cur = current_lines(a.source)
    index = {}
    for i, text in enumerate(cur, 1):
        index.setdefault(norm(text), []).append(i)

    items, gone = [], 0
    with open(a.worklist, encoding="utf-8") as fh:
        for raw in fh:
            m = RE_ITEM.match(raw.rstrip("\n"))
            if not m:
                continue
            line, rule, sev, msg = int(m.group(1)), m.group(2), int(0), m.group(4)
            sev = m.group(3)
            if not (a.lo <= line <= a.hi):
                continue
            if rules and rule not in rules:
                continue
            src = norm(base[line - 1]) if line - 1 < len(base) else ""
            cands = index.get(src) or []
            if not cands:
                gone += 1
                continue
            cur_line = min(cands, key=lambda c: abs(c - line))
            items.append((cur_line, line, rule, sev, msg, cur[cur_line - 1].strip()))

    items.sort(key=lambda r: (r[0], r[2]), reverse=not a.asc)
    print("BATCH %s issues=%d already-fixed/gone=%d"
          % (os.path.basename(a.source), len(items), gone))
    for cur_line, orig_line, rule, sev, msg, text in items:
        print("L%-6d | %-34s | %-8s | %s | %s"
              % (cur_line, rule, sev, msg[:110], text[:120]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
