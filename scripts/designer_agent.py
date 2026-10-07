#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Launch 1C Designer in AgentMode (SSH server) for dev_erpapk_demo.
Prints startup output (to discover SSH port) and keeps the process running.
Usage:
  python scripts/designer_agent.py start   # launch in background, save PID+log
  python scripts/designer_agent.py stop    # kill saved PID
"""
import os
import subprocess
import sys
import time

V8 = r"C:\Program Files\1cv8\8.5.4.1683\bin\1cv8.exe"
SERVER = "localhost"
REF = "dev_erpapk_demo"
ADMIN_ORLOV = "\u0410\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0430\u0442\u043e\u0440" \
              " (\u041e\u0440\u043b\u043e\u0432\u0410\u0412)"  # Администратор (ОрловАВ)
PID_FILE = os.path.join(os.path.dirname(__file__), "..", "heartbeat", "designer_agent.pid")
LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "heartbeat", "designer_agent.log")


OUT = os.path.join(os.path.dirname(__file__), "..", "heartbeat", "designer_agent_out.txt")

def start():
    cmd = [V8, "DESIGNER", f"/S", f"{SERVER}\\{REF}", f"/N{ADMIN_ORLOV}",
           "/AgentMode", "/AgentSSHHostKeyAuto",
           "/DisableStartupDialogs", "/Out", OUT]
    log = open(LOG_FILE, "wb")
    p = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT)
    with open(PID_FILE, "w") as f:
        f.write(str(p.pid))
    print("launched pid=%d, log=%s" % (p.pid, os.path.abspath(LOG_FILE)))
    # watch the log for the port line
    deadline = time.time() + 90
    seen = b""
    while time.time() < deadline:
        if p.poll() is not None:
            print("PROCESS EXITED rc=%s" % p.poll())
            break
        with open(LOG_FILE, "rb") as f:
            seen = f.read()
        if seen:
            sys.stdout.write(seen.decode("utf-8", errors="replace") + "\n")
        if b"port" in seen.lower() or b"ssh" in seen.lower():
            break
        time.sleep(3)
    print("--- log tail after wait ---")
    with open(LOG_FILE, "rb") as f:
        print(f.read().decode("utf-8", errors="replace"))


def stop():
    with open(PID_FILE) as f:
        pid = int(f.read().strip())
    subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"])
    print("killed", pid)


if __name__ == "__main__":
    {"start": start, "stop": stop}[sys.argv[1]]()
