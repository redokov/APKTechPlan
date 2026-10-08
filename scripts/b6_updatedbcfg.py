#!/usr/bin/env python3
"""B6: run Designer /UpdateDBCfg for the extension with Cyrillic-safe args.
Prints raw /Out log and exit code."""
import subprocess
import sys

V8 = r"C:\Program Files\1cv8\8.5.4.1683\bin\1cv8.exe"
OUT = r"C:\MyProjects\APKTechPlan\heartbeat\b6_updcfg3.txt"

args = [
    V8,
    "DESIGNER",
    "/S", "localhost/dev_erpapk_demo",
    "/N", "Администратор (ОрловАВ)",
    "/P", "",
    "/UpdateDBCfg",
    "-Extension", "ПланированиеТехникиАПК",
    "/Out", OUT,
    "/DisableStartupDialogs",
]
p = subprocess.run(args, capture_output=True, timeout=800)
print("exit code:", p.returncode)
print("stdout bytes:", len(p.stdout or b""))

with open(OUT, "rb") as f:
    raw = f.read()
for enc in ("utf-8-sig", "utf-16", "cp1251"):
    try:
        t = raw.decode(enc)
        print("--- log (%s) ---" % enc)
        print(t[:2000])
        break
    except Exception:
        continue
