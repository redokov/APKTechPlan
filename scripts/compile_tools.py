#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unicode-safe wrappers for PiPack 1C generator skills.

All Cyrillic values (object names, paths with Cyrillic dirs) must come from
UTF-8 JSON job files written by the agent's write tool, never from bash argv.

Usage (all job paths are Latin-named files, usually under .build/):

  python scripts/compile_tools.py meta <def.json> [outdir]
        meta-compile: -JsonPath <def.json> -OutputDir <outdir|default>

  python scripts/compile_tools.py form <job.json>
        form-compile: job = {"json": "<def.json>", "outputPath": "<Form.xml>"}

  python scripts/compile_tools.py subsystem <def.json>
        subsystem-compile: -DefinitionFile <def.json> -OutputDir <default>
        (def.json may carry a "parent" key -> -Parent)

  python scripts/compile_tools.py subsystemedit <job.json>
        subsystem-edit: job = {"subsystemPath": "<xml>",
                               "operations": [{"operation": "...", "value": "..."}]}
        (operations JSON is dumped to a temp file -> -DefinitionFile)

  python scripts/compile_tools.py formadd <job.json>
        form-add: job = {"objectPath": "<xml>", "formName": "...",
                         "purpose": "List|Record|...", "setDefault": true|false,
                         "synonym": "..."}

  python scripts/compile_tools.py bsl <job.json>
        copy BSL source with UTF-8 BOM: job = {"src": "<file>", "dst": "<file>"}
        (dst written under project root; src read as UTF-8)

Relative paths in job files resolve against the project root.
Default outdir = src/cfe/ПланированиеТехникиАПК (project extension)."""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = r'C:\MyProjects\PiPack\skills\1c'
DEFAULT_OUT = os.path.join(ROOT, 'src', 'cfe', 'ПланированиеТехникиАПК')


def tool_path(skill, script):
    return os.path.join(SKILLS, skill, 'scripts', script)


def abspath_rel_root(p):
    p = str(p)
    return p if os.path.isabs(p) else os.path.normpath(os.path.join(ROOT, p))


def run_ps1(script, args):
    cmd = ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass',
           '-File', script] + args
    r = subprocess.run(cmd, capture_output=True, timeout=600)
    out = r.stdout.decode('utf-8', errors='replace')
    err = r.stderr.decode('utf-8', errors='replace')
    return r.returncode, out, err


def load_job(path):
    with open(path, 'r', encoding='utf-8-sig') as f:
        return json.load(f)


def dispatch(kind, argv):
    if kind == 'meta':
        def_json = os.path.abspath(argv[0])
        outdir = os.path.abspath(argv[1]) if len(argv) > 1 else DEFAULT_OUT
        return run_ps1(tool_path('meta-compile', 'meta-compile.ps1'),
                       ['-JsonPath', def_json, '-OutputDir', outdir])

    if kind == 'form':
        job = load_job(argv[0])
        def_json = abspath_rel_root(job['json'])
        out_path = abspath_rel_root(job['outputPath'])
        return run_ps1(tool_path('form-compile', 'form-compile.ps1'),
                       ['-JsonPath', def_json, '-OutputPath', out_path])

    if kind == 'subsystem':
        def_json = os.path.abspath(argv[0])
        args = ['-DefinitionFile', def_json, '-OutputDir', DEFAULT_OUT]
        job = load_job(def_json)
        if job.get('parent'):
            args += ['-Parent', abspath_rel_root(job['parent'])]
        return run_ps1(tool_path('subsystem-compile', 'subsystem-compile.ps1'), args)

    if kind == 'subsystemedit':
        job = load_job(argv[0])
        ops_file = os.path.join(tempfile.gettempdir(), 'subsystem_edit_ops.json')
        with open(ops_file, 'w', encoding='utf-8') as f:
            json.dump(job['operations'], f, ensure_ascii=False)
        return run_ps1(tool_path('subsystem-edit', 'subsystem-edit.ps1'),
                       ['-SubsystemPath', abspath_rel_root(job['subsystemPath']),
                        '-DefinitionFile', ops_file])

    if kind == 'formadd':
        job = load_job(argv[0])
        args = ['-ObjectPath', abspath_rel_root(job['objectPath']),
                '-FormName', str(job['formName'])]
        if job.get('purpose'):
            args += ['-Purpose', str(job['purpose'])]
        if job.get('synonym'):
            args += ['-Synonym', str(job['synonym'])]
        if job.get('setDefault'):
            args += ['-SetDefault']
        return run_ps1(tool_path('form-add', 'form-add.ps1'), args)

    if kind == 'bsl':
        job = load_job(argv[0])
        src = abspath_rel_root(job['src'])
        dst = abspath_rel_root(job['dst'])
        with open(src, 'rb') as f:
            data = f.read()
        text = data.decode('utf-8-sig')
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, 'wb') as f:
            f.write(b'\xef\xbb\xbf' + text.replace('\r\n', '\n').replace('\n', '\r\n').encode('utf-8'))
        print('BSL written (UTF-8 BOM, CRLF): ' + dst)
        return 0, '', ''

    print('Unknown kind: ' + kind, file=sys.stderr)
    return 2, '', ''


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: compile_tools.py <meta|form|subsystem|subsystemedit|formadd|bsl> <json|def> [outdir]',
              file=sys.stderr)
        sys.exit(2)
    rc, out, err = dispatch(sys.argv[1], sys.argv[2:])
    sys.stdout.write(out[-2500:])
    if rc != 0:
        sys.stderr.write('STDERR tail: ' + err[-1500:])
    sys.exit(rc)
