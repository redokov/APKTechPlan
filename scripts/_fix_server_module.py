#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix two compile bugs in Тх_ТехникаСервер/Ext/Module.bsl:
1) line ~302: РазностьДат() is a QUERY-language function, not BSL -> date arithmetic.
2) line ~931: 'РегистрСведений.' typo (singular) in BSL code -> 'РегистрыСведений.'.
Then scan all module code for remaining singular occurrences outside string literals.
CRLF+BOM safe.
"""
import io
import os
import re

PATH = r"src/cfe/ПланированиеТехникиАПК/CommonModules/Тх_ТехникаСервер/Ext/Module.bsl"

raw = open(PATH, "rb").read()
text = raw.decode("utf-8-sig")

# 1) РазностьДат -> arithmetic (dates in 1C: difference is seconds)
old1 = "\tДней = РазностьДат(НачалоДня(НачалоПериода), НачалоДня(ОкончаниеПериода), \"ДЕНЬ\") + 1;"
new1 = "\tДней = (НачалоДня(ОкончаниеПериода) - НачалоДня(НачалоПериода)) / 86400 + 1;"
assert old1 in text, "old1 not found"
text = text.replace(old1, new1, 1)

# 2) singular typo in BSL code (line 931); the query-string occurrence stays.
old2 = "НаборЗаписей = РегистрСведений.Тх_КоэффициентыПересчетаРабот.СоздатьНаборЗаписей();"
new2 = "НаборЗаписей = РегистрыСведений.Тх_КоэффициентыПересчетаРабот.СоздатьНаборЗаписей();"
assert text.count(old2) == 1, "old2 count != 1: %d" % text.count(old2)
text = text.replace(old2, new2, 1)

with io.open(PATH, "wb") as f:
    f.write(b"\xef\xbb\xbf" + text.encode("utf-8"))
print("fixed: РазностьДат->arithmetic; РегистрСведений->РегистрыСведений (code)")

# verification scan: singular 'РегистрСведений.' in code lines outside string literals
print("--- residual scan (code, non-query lines):")
hits = 0
for root, dirs, files in os.walk(r"src/cfe/ПланированиеТехникиАПК"):
    for fn in files:
        if not fn.endswith(".bsl"):
            continue
        p = os.path.join(root, fn)
        for i, l in enumerate(open(p, encoding="utf-8-sig").read().splitlines()):
            s = l.strip()
            if s.startswith("|") or s.startswith("//"):
                continue
            code = re.sub(r'"[^"]*"', '""', l)
            if re.search(r"РегистрСведений\.", code):
                print("  HIT:", p, i + 1, s[:60])
                hits += 1
print("residual hits:", hits)
