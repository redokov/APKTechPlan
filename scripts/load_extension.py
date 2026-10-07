#!/usr/bin/env python3
"""B2: load CFE 'ПланированиеТехникиАПК' into dev_erpapk_demo via db-load-xml.ps1.

Cyrillic args (user name, extension name, paths) live HERE as python literals,
never inline in bash argv. Handles the 'extension already exists' case:
retry without -UpdateDB, then re-run with -UpdateDB (per db-cfe-admin skill).
"""
import subprocess
import sys

PS_SCRIPT = r"C:/MyProjects/PiPack/skills/1c/db-load-xml/scripts/db-load-xml.ps1"

ARGS_BASE = [
    "-NoProfile", "-File", PS_SCRIPT,
    "-V8Path", r"C:\Program Files\1cv8\8.5.4.1683\bin",
    "-InfoBaseServer", "localhost",
    "-InfoBaseRef", "dev_erpapk_demo",
    "-UserName", "Администратор (ОрловАВ)",
    "-Password", "",
    "-ConfigDir", r"C:\MyProjects\APKTechPlan\src\cfe\ПланированиеТехникиАПК",
    "-Mode", "Full",
    "-Extension", "ПланированиеТехникиАПК",
]

ALREADY_EXISTS_MARKERS = [
    "уже существует",
    "already exists",
]


def run(extra_args, tag):
    cmd = ["powershell.exe"] + ARGS_BASE + extra_args
    print("[run:%s] %s" % (tag, " ".join(a if not any(ord(c) > 127 for c in a)
                                         else "<cyrillic>" for a in cmd[2:])))
    sys.stdout.flush()
    proc = subprocess.run(cmd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=2700)
    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    print(out[-4000:])
    print("[run:%s] exit=%d" % (tag, proc.returncode))
    return proc.returncode, out


def main():
    rc, out = run(["-UpdateDB"], "with-update")
    if rc == 0:
        print("OK: loaded + UpdateDBCfg")
        return 0
    if any(m in out for m in ALREADY_EXISTS_MARKERS):
        print("[retry] extension exists -> load WITHOUT -UpdateDB, then WITH")
        rc1, _ = run([], "no-update")
        if rc1 != 0:
            print("FAILED at no-update step")
            return 1
        rc2, _ = run(["-UpdateDB"], "with-update-2")
        return 0 if rc2 == 0 else 1
    print("FAILED (see output above)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
