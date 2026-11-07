#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cyrillic-safe batch DESIGNER runner (raw command line).

WHY THIS SHAPE
--------------
1C parses the raw Windows command line itself. It needs keys glued to their
values:  /N"user"  /S"localhost/base"  /Out"file". Python's subprocess(list)
passes the list through list2cmdline(), which ESCAPES those inner quotes into
/N\"user\" and 1C then reports
    "Пользователь ИБ не идентифицирован"  (bad user)
    "Ошибка в параметрах командной строки" (bad /N with space, spaced form)
So on Windows the command line must be handed over READY-MADE as one string.
Same conclusion as db-cfe-admin.py:run_v8 (os.name == "nt" branch).

ALSO: /DisableStartupDialogs is mandatory. Without it designer opens a modal
dialog, the process never exits and the caller hangs (this is what burned the
previous night run).

USAGE
    from designer_ps import designer
    rc, log = designer(["/CheckModules", "-Extension", "ПланированиеТехникиАПК"])
"""
import os
import subprocess
import tempfile
import time

V8 = r"C:\Program Files\1cv8\8.5.4.1683\bin\1cv8.exe"
SERVER = "localhost"
REF = "dev_erpapk_demo"
USER = "\u0410\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0430\u0442\u043e\u0440 (\u041e\u0440\u043b\u043e\u0432\u0410\u0412)"


def designer(args, timeout=900, user=USER):
    """Run `1cv8 DESIGNER <args>`. Returns (rc, log_text). Quoted args must
    already carry their own inner quotes (e.g. '/Extension', '"Имя"')."""
    work = tempfile.mkdtemp(prefix="designer_cl_")
    log = os.path.join(work, "out.txt")

    parts = [
        '"%s"' % V8,
        "DESIGNER",
        '/S"%s/%s"' % (SERVER, REF),
        '/N"%s"' % user,
    ]
    parts += list(args)
    parts += ['/Out"%s"' % log, "/DisableStartupDialogs"]
    cmdline = " ".join(parts)

    shown = cmdline.replace(USER, "<user>")
    print("[designer] %s" % shown)

    t0 = time.time()
    try:
        p = subprocess.run(cmdline, capture_output=True, timeout=timeout)
        rc = p.returncode
        stderr = (p.stderr or b"")[:400]
    except subprocess.TimeoutExpired:
        print("[designer] TIMEOUT %.0fs" % (time.time() - t0))
        return None, ""

    txt = ""
    if os.path.exists(log):
        raw = open(log, "rb").read()
        for enc in ("utf-8-sig", "utf-8", "cp1251"):
            try:
                txt = raw.decode(enc)
                break
            except UnicodeDecodeError:
                continue
    print("[designer] rc=%s %.1fs log=%d bytes" % (rc, time.time() - t0, len(txt)))
    if stderr.strip():
        print("[designer] stderr: %r" % stderr)
    return rc, txt


if __name__ == "__main__":
    import sys

    EXT = "\u041f\u043b\u0430\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435\u0422\u0435\u0445\u043d\u0438\u043a\u0438\u0410\u041f\u041a"

    if len(sys.argv) > 1 and sys.argv[1] == "list":
        rc, log = designer(["/DumpDBCfgList", "-AllExtensions"], timeout=300)
        print("--- extensions ---")
        print(log.strip() or "(empty)")
    else:
        rc, log = designer(["/CheckModules", "-Extension", '"%s"' % EXT],
                           timeout=1800)
        print("--- CheckModules ---")
        print(log.strip()[:6000] or "(empty)")
