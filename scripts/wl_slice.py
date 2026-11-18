#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Slice a Sonar WONTFIX worklist together with the current source text.

Usage:
  python scripts/wl_slice.py <worklist.md> <source.bsl> [--from N] [--to N] [--rules R1,R2]

Prints one line per issue:
  L<line> | <rule> | <message> | <source line>
Sorted DESCENDING by line number so that batches can be applied bottom-up
(edits then never invalidate the line numbers of not-yet-processed batches).
"""
import argparse
import os
import re
import sys

RE_ITEM = re.compile(r"^- L(\d+) \| ([A-Za-z]+) \| ([A-Z]+) \| (.*)$")


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
    items = []
    with open(a.worklist, encoding="utf-8") as fh:
        for raw in fh:
            m = RE_ITEM.match(raw.rstrip("\n"))
            if not m:
                continue
            line, rule, sev, msg = int(m.group(1)), m.group(2), m.group(3), m.group(4)
            if not (a.lo <= line <= a.hi):
                continue
            if rules and rule not in rules:
                continue
            items.append((line, rule, sev, msg))

    src = {}
    with open(a.source, encoding="utf-8-sig") as fh:
        for i, text in enumerate(fh.read().split("\n"), 1):
            src[i] = text

    items.sort(key=lambda r: (r[0], r[1]), reverse=not a.asc)
    print("BATCH %s lines %d..%d rules=%s issues=%d"
          % (os.path.basename(a.source), a.lo, a.hi, ",".join(sorted(rules)) or "*", len(items)))
    for line, rule, sev, msg in items:
        text = src.get(line, "<NO SUCH LINE>").strip()
        print("L%-6d | %-34s | %-8s | %s | %s"
              % (line, rule, sev, msg[:120], text[:130]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
