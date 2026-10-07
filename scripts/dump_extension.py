#!/usr/bin/env python3
"""B4 round-trip: dump extension from dev_erpapk_demo into a NEW temp dir."""
import os
import subprocess
import sys

PS_SCRIPT = r"C:/MyProjects/PiPack/skills/1c/db-dump-xml/scripts/db-dump-xml.ps1"
DUMP_DIR = os.path.join(os.environ.get("TEMP", "/tmp"), "rt_dump_apktechplan")

cmd = [
    "powershell.exe", "-NoProfile", "-File", PS_SCRIPT,
    "-V8Path", r"C:\Program Files\1cv8\8.5.4.1683\bin",
    "-InfoBaseServer", "localhost",
    "-InfoBaseRef", "dev_erpapk_demo",
    "-UserName", "Администратор (ОрловАВ)",
    "-Password", "",
    "-ConfigDir", DUMP_DIR,
    "-Mode", "Full",
    "-Extension", "ПланированиеТехникиАПК",
]
print("[dump] -> " + DUMP_DIR)
sys.stdout.flush()
proc = subprocess.run(cmd, capture_output=True, text=True,
                      encoding="utf-8", errors="replace", timeout=2700)
out = (proc.stdout or "") + "\n" + (proc.stderr or "")
print(out[-3500:])
print("[dump] exit=%d" % proc.returncode)
sys.exit(proc.returncode)
