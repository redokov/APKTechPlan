#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run a designer-shell command via SSH to Designer AgentMode.

Cyrillic-safe: command text comes from a file (argv[1]) or a UTF-8 script file,
never from bash argv inline. Sends command, waits for 'designer> ' prompt,
prints raw output to stdout and to heartbeat/agent_last_out.txt.
"""
import io
import os
import sys
import time

import paramiko

HOST = "127.0.0.1"
PORT = 1543
ADMIN_ORLOV = "\u0410\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0430\u0442\u043e\u0440" \
              " (\u041e\u0440\u043b\u043e\u0432\u0410\u0412)"
OUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                        "heartbeat", "agent_last_out.txt")
PROMPT = b"designer> "
CMD_TIMEOUT = int(os.environ.get("AGENT_CMD_TIMEOUT", "900"))


def run_commands(commands):
    t = paramiko.Transport((HOST, PORT))
    t.start_client(timeout=30)
    t.auth_password(ADMIN_ORLOV, "")
    chan = t.open_session()
    chan.invoke_shell()
    # drain banner
    _pump(chan, 4)
    outputs = []
    for cmd in commands:
        chan.sendall(cmd.encode("utf-8") + b"\n")
        out = _pump(chan, CMD_TIMEOUT, wait_prompt=True)
        outputs.append((cmd, out))
    chan.close()
    t.close()
    return outputs


def _pump(chan, seconds, wait_prompt=False):
    out = b""
    deadline = time.time() + seconds
    while time.time() < deadline:
        if chan.recv_ready():
            out += chan.recv(65536)
            if wait_prompt and out.rstrip().endswith(PROMPT.strip()):
                # small grace period for trailing output
                t2 = time.time() + 2
                while time.time() < t2:
                    if chan.recv_ready():
                        out += chan.recv(65536)
                    else:
                        time.sleep(0.1)
                return out
        else:
            time.sleep(0.15)
    return out


def main():
    path = sys.argv[1]
    with io.open(path, encoding="utf-8-sig") as f:
        commands = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    outs = run_commands(commands)
    report = []
    for cmd, outb in outs:
        text = outb.decode("utf-8", errors="replace")
        # strip echoed command line if present
        report.append("$ %s\n%s" % (cmd, text))
    full = "\n".join(report)
    with io.open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(full)
    sys.stdout.write(full)


if __name__ == "__main__":
    main()
