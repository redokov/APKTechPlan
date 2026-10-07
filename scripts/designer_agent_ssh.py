#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SSH client to 1C Designer AgentMode. Discovers auth, then runs designer shell commands."""
import socket
import sys

import paramiko

HOST = "127.0.0.1"
PORT = 1543
ADMIN_ORLOV = "\u0410\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0430\u0442\u043e\u0440" \
              " (\u041e\u0440\u043b\u043e\u0432\u0410\u0412)"


def probe():
    t = paramiko.Transport((HOST, PORT))
    t.start_client(timeout=20)
    print("banner:", t.remote_version)
    try:
        allowed = t.auth_none(ADMIN_ORLOV)
        print("auth_none ->", allowed)
    except paramiko.BadAuthenticationType as e:
        print("allowed auth types:", e.allowed_types)
    t.close()


if __name__ == "__main__":
    try:
        probe()
    except (socket.error, paramiko.SSHException) as e:
        print("probe failed:", repr(e))
