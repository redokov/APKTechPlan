#!/usr/bin/env python3
"""Dump DB config of extension to temp dir; grep FillValue in the plan document XML."""
import subprocess, os, shutil, glob

V8 = r"C:\Program Files\1cv8\8.5.4.1683\bin\1cv8.exe"
TMP = r"C:\MyProjects\APKTechPlan\heartbeat\_dumpcfg_check"
OUT = TMP + ".out"
shutil.rmtree(TMP, ignore_errors=True)
pass
if os.path.exists(OUT):
    os.remove(OUT)
args = [
    V8, "DESIGNER",
    "/S", "localhost/dev_erpapk_demo",
    "/N", "Администратор (ОрловАВ)",
    "/P", "",
    "/DumpCfg", TMP,
    "-Extension", "ПланированиеТехникиАПК",
    "/Out", OUT,
    "/DisableStartupDialogs",
]
p = subprocess.run(args, capture_output=True, timeout=800)
print("exit:", p.returncode)
try:
    print(open(OUT, "rb").read().decode("utf-16", "replace")[:500])
except Exception as e:
    print("out read fail", e)
hits = []
for f in glob.glob(TMP + "/**/*.xml", recursive=True):
    with open(f, "r", encoding="utf-8-sig", errors="replace") as fh:
        t = fh.read()
    if "FillValue" in t:
        hits.append(f)
print("files with FillValue:", len(hits))
for h in hits:
    print(h.replace(TMP, ""))
