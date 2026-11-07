#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""List extensions in dev_erpapk_demo using the TESTED db-cfe-admin tool.

Cyrillic user name is a Python literal here (never inline in a shell string),
and the subprocess is run with a ready-made list -> the tool itself builds the
Windows command line (see db-cfe-admin.py run_v8: on nt it joins args into one
string, because list2cmdline would escape the quotes 1C needs).
"""
import subprocess
import sys

TOOL = r"C:\MyProjects\PiPack\skills\1c\db-cfe-admin\scripts\db-cfe-admin.py"
V8 = r"C:\Program Files\1cv8\8.5.4.1683\bin"
USER = "\u0410\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0430\u0442\u043e\u0440 (\u041e\u0440\u043b\u043e\u0432\u0410\u0412)"


def main():
    cmd = [sys.executable, TOOL, "-Command", "list",
           "-V8Path", V8,
           "-InfoBaseServer", "localhost",
           "-InfoBaseRef", "dev_erpapk_demo",
           "-UserName", USER,
           "-Password", ""]
    p = subprocess.run(cmd, capture_output=True, timeout=600)
    out = (p.stdout or b"").decode("utf-8", errors="replace")
    err = (p.stderr or b"").decode("utf-8", errors="replace")
    print("rc=%s" % p.returncode)
    print(out[-4000:])
    if err.strip():
        print("STDERR: " + err[-2000:])
    return p.returncode


if __name__ == "__main__":
    sys.exit(main())
