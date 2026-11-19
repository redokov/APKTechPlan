#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wave 6b: add BSLLS suppression pairs at exact lines reported by bsl-ls.

Reads a bsl_ls_file.py --json report, inserts an off/on comment pair around
each flagged line (off above, on below). Only rules Typo and
LatinAndCyrillicSymbolInWord are handled. Idempotent: skips lines already
preceded by a BSLLS off-comment. ASCII-only source (escapes).

Usage:
  PYTHONIOENCODING=utf-8 python3 scripts/wave6b_suppress.py <file.bsl> <diags.json>
"""
import json
import sys

OFF_T = ("// BSLLS:Typo-off (\u0438\u043c\u044f \u043e\u0431\u0451\u0440\u0442\u043a\u0438 "
         "\u0437\u0435\u0440\u043a\u0430\u043b\u0438\u0442 \u044d\u0442\u0430\u043b\u043e\u043d"
         "\u043d\u043e\u0435 \u0438\u043c\u044f \u0442\u0435\u0441\u0442\u0430 - \u0442\u0440"
         "\u0430\u0441\u0441\u0438\u0440\u043e\u0432\u043a\u0430 \u043f\u0440\u043e\u0433\u043e"
         "\u043d\u0430)")
OFF_L = ("// BSLLS:LatinAndCyrillicSymbolInWord-off (Generic - \u0434\u043e\u043c\u0435"
         "\u043d\u043d\u044b\u0439 \u0442\u0435\u0440\u043c\u0438\u043d \u0442\u0438\u043f"
         "\u043e\u0432 \u0434\u0430\u043d\u043d\u044b\u0445)")
P = "\u041f\u0440\u043e\u0446\u0435\u0434\u0443\u0440\u0430 "  # Процедура

path, report = sys.argv[1], sys.argv[2]
raw = open(path, "rb").read()
bom = raw.startswith(b"\xef\xbb\xbf")
text = raw.decode("utf-8-sig")
NL = "\r\n" if "\r\n" in text else "\n"
lines = text.replace("\r\n", "\n").split("\n")

d = json.load(open(report, encoding="utf-8"))
diags = []
for fi in d.get("fileinfos", []):
    diags.extend(fi.get("diagnostics", []))

targets = []
for diag in diags:
    code = diag.get("code")
    if code not in ("Typo", "LatinAndCyrillicSymbolInWord"):
        continue
    rng = diag.get("range", {})
    n = rng.get("start", {}).get("line")  # 0-based
    if n is None:
        continue
    targets.append((n, code))

added = 0
# bottom-up so insertions do not shift remaining targets
for idx, code in sorted(targets, reverse=True):
    if idx <= 0 or "BSLLS" in lines[idx - 1]:
        continue
    target = lines[idx]
    indent = ""
    if target.startswith("\t") or target.startswith(P):
        pass
    if code == "Typo":
        off, on = OFF_T, "// BSLLS:Typo-on"
    else:
        off, on = OFF_L, "// BSLLS:LatinAndCyrillicSymbolInWord-on"
    # indent the pair if target line is indented
    if target.startswith("\t"):
        off = "\t" + off
        on = "\t" + on
    lines[idx:idx] = [off]
    lines[idx + 2:idx + 2] = [on]
    added += 1

out = NL.join(lines)
data = out.encode("utf-8")
if bom:
    data = b"\xef\xbb\xbf" + data
open(path, "wb").write(data)
print("suppression pairs added:", added)
