#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CheckModules for the extension in ExternalConnection context (B5 diagnosis)."""
import subprocess
import sys

PS = r"C:/MyProjects/PiPack/skills/1c/db-cfe-admin/scripts/db-cfe-admin.ps1"

cmd = [
    "powershell.exe", "-NoProfile", "-File", PS,
    "-Command", "check",
    "-V8Path", r"C:\Program Files\1cv8\8.5.4.1683\bin",
    "-InfoBaseServer", "localhost",
    "-InfoBaseRef", "dev_erpapk_demo",
    "-UserName", "Администратор (ОрловАВ)",
    "-Password", "",
    "-Name", "ПланированиеТехникиАПК",
    "-Checks", "modules",
    "-Context", "ExternalConnection",
]
print("[check] contexts=ExternalConnection")
p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                  errors="replace", timeout=2700)
out = (p.stdout or "") + (p.stderr or "")
sys.stdout.write(out[-6000:])
print("[check] exit=%d" % p.returncode)
