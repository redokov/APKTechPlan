#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cyrillic-safe wrapper for PiPack skill scripts (cfe-init etc.)."""
import subprocess, sys

SKILL = r'C:\MyProjects\PiPack\skills\1c'

def run(script, *args):
    r = subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                       '-File', script] + list(args), capture_output=True, timeout=900)
    out = r.stdout.decode('utf-8', errors='replace')
    err = r.stderr.decode('utf-8', errors='replace')
    return r.returncode, out, err

if __name__ == '__main__':
    script = sys.argv[1]
    rc, out, err = run(script, *sys.argv[2:])
    sys.stdout.write(out)
    sys.stderr.write(err[-2000:])
    sys.exit(rc)
