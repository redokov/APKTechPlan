# -*- coding: utf-8 -*-
"""Cross-check the Sonar WONTFIX worklist against current bsl-ls diagnostics.

For each file: run bsl-ls (via scripts/bsl_ls_file.py --json), then report
every current diagnostic whose (rule, normalized line text) also appears in the
worklist (worklist line texts are taken from git HEAD).

Usage:
  python scripts/wl_check.py <object-name> <relative-path-under-cfe>
"""
import collections
import io
import json
import os
import re
import subprocess
import sys

CFE = 'src/cfe/ПланированиеТехникиАПК'
TMP = 'tmp/wlcheck'
RE_ITEM = re.compile(r"^- L(\d+) \| ([A-Za-z]+) \| ([A-Z]+) \| (.*)$", re.M)


def norm(s):
    return re.sub(r"\s+", " ", s.strip())


def main():
    name, rel = sys.argv[1], sys.argv[2]
    path = os.path.join(CFE, rel).replace('\\', '/')
    os.makedirs(TMP, exist_ok=True)
    js = os.path.join(TMP, name + '.json')
    subprocess.run([sys.executable, 'scripts/bsl_ls_file.py', path,
                    '--json', js], capture_output=True, text=True)

    head = subprocess.run(['git', 'show', 'HEAD:' + path],
                          capture_output=True).stdout
    if head[:3] == b'\xef\xbb\xbf':
        head = head[3:]
    head = head.decode('utf-8').replace('\r\n', '\n').split('\n')
    raw = io.open(path, 'rb').read()
    if raw[:3] == b'\xef\xbb\xbf':
        raw = raw[3:]
    cur = raw.decode('utf-8').replace('\r\n', '\n').split('\n')

    wl = io.open('tmp/sonar-2026-11-18/wontfix_%s.md' % name,
                 encoding='utf-8').read()
    sig = collections.Counter()
    total = collections.Counter()
    for m in RE_ITEM.finditer(wl):
        total[m.group(2)] += 1
        sig[(m.group(2), norm(head[int(m.group(1)) - 1]))] += 1

    data = json.load(io.open(js, encoding='utf-8'))
    diags = []
    for fi in data.get('fileinfos') or []:
        for x in fi.get('diagnostics') or []:
            diags.append(((x.get('code') or '').split(':')[-1],
                          x['range']['start']['line'] + 1,
                          x.get('severity', '')))
    local = collections.Counter(r for r, _, _ in diags)

    left = []
    for rule, line, sev in diags:
        if line - 1 < len(cur) and sig.get((rule, norm(cur[line - 1])), 0) > 0:
            left.append((rule, line, sev))
    print('=== %s (%s)' % (name, rel))
    print('worklist: %d  |  bsl-ls now: %d  |  still-matching targets: %d'
          % (sum(total.values()), len(diags), len(left)))
    for rule, line, sev in sorted(left, key=lambda r: (r[1], r[0])):
        print('  L%-6d %-34s %-8s | %s'
              % (line, rule, sev, cur[line - 1].strip()[:95]))
    if left:
        print('  rules left: %s' % dict(collections.Counter(r for r, _, _ in left)))
    print('  local rules: %s' % dict(local.most_common()))
    return 0


if __name__ == '__main__':
    sys.exit(main())
