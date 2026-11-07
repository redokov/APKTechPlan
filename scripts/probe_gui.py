#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Can a 1C GUI client actually start in this session?

Starts 1cv8c.exe ENTERPRISE against dev_erpapk_demo, waits, then reports
whether the process exists and whether it owns a visible window with a title.
That decides GUI vs headless for Vanessa (TestManager/TestClient need a
desktop).

Args in the connection string use the glued form  /N"user"  (no space between
key and value) - 1C's parser rejects /N "user".
"""
import subprocess
import sys
import time

V8C = r"C:\Program Files\1cv8\8.5.4.1683\bin\1cv8c.exe"
USER = "\u0410\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0430\u0442\u043e\u0440 (\u041e\u0440\u043b\u043e\u0432\u0410\u0412)"
BASE = "localhost\\dev_erpapk_demo"


def ps(script):
    p = subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
         "-Command", script],
        capture_output=True, timeout=120)
    return (p.stdout or b"").decode("utf-8", errors="replace")


def main():
    cmdline = '"%s" ENTERPRISE /S"%s" /N"%s" /DisableStartupDialogs /DisableStartupMessages' % (
        V8C, BASE, USER)
    print("launch: %s" % cmdline.replace(USER, "<user>"))
    proc = subprocess.Popen(cmdline)
    time.sleep(45)

    alive = proc.poll() is None
    print("process alive after 45s: %s (pid=%s)" % (alive, proc.pid))

    out = ps(
        "Get-Process -Name 1cv8c -ErrorAction SilentlyContinue | "
        "Select-Object Id,MainWindowTitle,Responding | Format-Table -AutoSize | Out-String -Width 200"
    )
    print("--- 1cv8c processes ---")
    print(out.strip() or "(none)")

    sess = ps("(Get-Process -Id $PID).SessionId")
    print("session id of powershell: %s" % sess.strip())
    interactive = ps("[Environment]::UserInteractive")
    print("UserInteractive: %s" % interactive.strip())

    subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                   capture_output=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
