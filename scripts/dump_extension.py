#!/usr/bin/env python3
"""B4 round-trip: dump extension from dev_erpapk_demo into a NEW temp dir."""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v8conf

PS_SCRIPT = r"C:/MyProjects/PiPack/skills/1c/db-dump-xml/scripts/db-dump-xml.ps1"
DUMP_DIR = os.path.join(os.environ.get("TEMP", "/tmp"), "rt_dump_apktechplan")

# Platform bin dir: --v8path > APK_V8_PATH > autodetect (scripts/v8conf.py).
V8_BIN = v8conf.resolve_v8path(v8conf.cli_v8path(prune=True))
print("[dump] platform bin: %s" % V8_BIN)

cmd = [
    "powershell.exe", "-NoProfile", "-File", PS_SCRIPT,
    "-V8Path", V8_BIN,
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
