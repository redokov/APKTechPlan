#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unicode-safe wrappers for PiPack 1C generator skills.
Usage:
  python scripts/compile_meta.py <json> [outdir]
  python scripts/compile_form.py <json> [outdir]
  python scripts/compile_skd.py  <json> [outdir]
Default outdir = src/cfe/ПланированиеТехникиАПК (project extension)."""
import subprocess, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = r'C:\MyProjects\PiPack\skills\1c'
DEFAULT_OUT = os.path.join(ROOT, 'src', 'cfe', 'ПланированиеТехникиАПК')

TOOLS = {
    'meta': os.path.join(SKILLS, 'meta-compile', 'scripts', 'meta-compile.ps1'),
    'form': os.path.join(SKILLS, 'form-compile', 'scripts', 'form-compile.ps1'),
    'skd': os.path.join(SKILLS, 'skd-compile', 'scripts', 'skd-compile.ps1'),
    'mxl': os.path.join(SKILLS, 'mxl-compile', 'scripts', 'mxl-compile.ps1'),
}


def run_tool(kind, json_path, outdir):
    script = TOOLS[kind]
    args = ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass',
            '-File', script, '-JsonPath', json_path, '-OutputDir', outdir]
    r = subprocess.run(args, capture_output=True, timeout=600)
    out = r.stdout.decode('utf-8', errors='replace')
    err = r.stderr.decode('utf-8', errors='replace')
    return r.returncode, out, err


if __name__ == '__main__':
    kind = sys.argv[1]
    json_path = os.path.abspath(sys.argv[2])
    outdir = os.path.abspath(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_OUT
    rc, out, err = run_tool(kind, json_path, outdir)
    sys.stdout.write(out[-2500:])
    if rc != 0:
        sys.stderr.write('STDERR tail: ' + err[-1500:])
    sys.exit(rc)
