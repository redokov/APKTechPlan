#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Estimate the SonarQube-side MagicNumber count for a .bsl file.

Sonar's bsl-language-server build flags numeric literals almost anywhere in an
expression (including the parts of a date constructor), but not numbers that a
variable is initialised with (`X = 12;`) and not 0/1/-1.

Usage:
  python scripts/magic_est.py <file.bsl> [--list]
  git show HEAD:path | python scripts/magic_est.py - [--list]
"""
import argparse
import re
import sys

NUM = re.compile(r"(?<![\w.])-?\d+(?:\.\d+)?(?![\w.])")
ASSIGN = re.compile(r"^\s*[^\W\d]\w*\s*=\s*-?\d+(?:\.\d+)?\s*;\s*$")
EXEMPT = {"0", "1", "-1"}


def strip_code(line):
    """Remove the comment tail and the string literals from a code line."""
    out, i, in_str, n = [], 0, False, len(line)
    while i < n:
        ch = line[i]
        if in_str:
            if ch == '"':
                if i + 1 < n and line[i + 1] == '"':
                    i += 2
                    continue
                in_str = False
            i += 1
            continue
        if ch == '"':
            in_str = True
            i += 1
            continue
        if ch == "/" and i + 1 < n and line[i + 1] == "/":
            break
        out.append(ch)
        i += 1
    return "".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.path == "-":
        raw = sys.stdin.buffer.read()
    else:
        raw = open(a.path, "rb").read()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    lines = raw.decode("utf-8").replace("\r\n", "\n").split("\n")

    total = 0
    for no, line in enumerate(lines, 1):
        code = strip_code(line)
        if not code.strip():
            continue
        if ASSIGN.match(code):
            continue
        hits = [m.group(0) for m in NUM.finditer(code) if m.group(0) not in EXEMPT]
        if hits:
            total += len(hits)
            if a.list:
                print("L%-6d %-30s | %s" % (no, ",".join(hits), code.strip()[:100]))
    print("MagicNumber estimate: %d" % total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
