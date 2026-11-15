#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Align working-tree file encodings with the HEAD blob (rake #1 of this project).

Why: a python edit that writes with `encoding="utf-8"` drops the BOM, and one
that writes CRLF where HEAD stores LF turns a 3-line change into a full-file
diff. This helper rewrites the working file to the EOL style and BOM state of
its HEAD version, preserving the actual content lines.

Usage (paths relative to the repo root, any number):
    python scripts/normalize_eol_to_head.py <path> [<path> ...]
    python scripts/normalize_eol_to_head.py --staged    # every staged M file
"""
import subprocess
import sys

ROOT = None


def head_blob(rel):
    out = subprocess.run(['git', '-c', 'core.quotepath=false', 'show', 'HEAD:' + rel],
                         capture_output=True, cwd=ROOT)
    return out.stdout if out.returncode == 0 else b''


def norm(rel):
    head = head_blob(rel)
    if not head:
        return None
    import os
    path = os.path.join(ROOT, rel) if ROOT else rel
    with open(path, 'rb') as f:
        cur = f.read()
    head_crlf = head.count(b'\r\n')
    head_style = 'crlf' if head_crlf > (head.count(b'\n') - head_crlf) else 'lf'
    head_bom = head.startswith(b'\xef\xbb\xbf')

    body = cur
    if body.startswith(b'\xef\xbb\xbf'):
        body = body[3:]
    body = body.replace(b'\r\n', b'\n')
    if head_style == 'crlf':
        body = body.replace(b'\n', b'\r\n')
    out = (b'\xef\xbb\xbf' if head_bom else b'') + body
    if out == cur:
        return None
    with open(path, 'wb') as f:
        f.write(out)
    return (head_style, 'bom' if head_bom else 'no-bom')


def main(argv):
    global ROOT
    ROOT = subprocess.run(['git', 'rev-parse', '--show-toplevel'],
                          capture_output=True, text=True).stdout.strip()
    paths = argv[1:]
    if paths == ['--staged']:
        paths = []
        for st in ('M', 'A'):
            out = subprocess.run(['git', '-c', 'core.quotepath=false', 'diff', '--cached',
                                  '--name-only', '--diff-filter=' + st],
                                 capture_output=True, text=True, encoding='utf-8', cwd=ROOT).stdout
            paths += [p for p in out.split('\n') if p.strip()]
    changed = 0
    for rel in paths:
        res = norm(rel)
        if res:
            changed += 1
            print('выровнено: %-12s %-6s %s' % (res[0], res[1], rel))
    print('файлов изменено: %d' % changed)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
