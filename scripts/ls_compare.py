# -*- coding: utf-8 -*-
"""Compare two bsl-ls JSON reports by (file, rule) counts.

Paths in the reports pass through a throwaway temp dir, so the file key is the
tail of the path after the last CommonModules/ DataProcessors/ Reports/ etc.

Usage:
  python scripts/ls_compare.py <baseline.json> <current.json>
Exit code 1 if any rule count increased for a file.
"""
import collections
import io
import json
import sys

ANCHORS = ('/CommonModules/', '/DataProcessors/', '/Reports/',
           '/InformationRegisters/', '/Constants/', '/Enums/')


def load(path):
    data = json.load(io.open(path, encoding='utf-8'))
    if not (data.get('fileinfos') or []):
        raise SystemExit('FATAL: 0 files analyzed in %s = check NOT performed'
                         % path)
    out = collections.Counter()
    for fi in data['fileinfos']:
        p = (fi.get('path') or '').replace('\\', '/')
        key = p
        for a in ANCHORS:
            if a in p:
                key = p.split(a, 1)[1]
                key = a.strip('/') + '/' + key
                break
        for d in fi.get('diagnostics') or []:
            out[(key, (d.get('code') or '').split(':')[-1])] += 1
    return out


def main():
    base, now = load(sys.argv[1]), load(sys.argv[2])
    grew, shrank = [], []
    for key in sorted(set(base) | set(now)):
        b, n = base[key], now[key]
        if b == n:
            continue
        (grew if n > b else shrank).append((key, b, n))
    print('=== SHRANK (%d) ===' % len(shrank))
    for (f, r), b, n in shrank:
        print('  %-52s %-34s %4d -> %4d  (%+d)' % (f, r, b, n, n - b))
    print('=== GREW (%d) ===' % len(grew))
    for (f, r), b, n in grew:
        print('  %-52s %-34s %4d -> %4d  (%+d)' % (f, r, b, n, n - b))
    print('=== totals: base=%d now=%d (delta %+d) ==='
          % (sum(base.values()), sum(now.values()),
             sum(now.values()) - sum(base.values())))
    per_rule_base = collections.Counter()
    per_rule_now = collections.Counter()
    for (f, r), n in base.items():
        per_rule_base[r] += n
    for (f, r), n in now.items():
        per_rule_now[r] += n
    print('=== per rule ===')
    for r in sorted(set(per_rule_base) | set(per_rule_now)):
        b, n = per_rule_base[r], per_rule_now[r]
        if b != n:
            print('  %-36s %4d -> %4d  (%+d)' % (r, b, n, n - b))
    return 1 if grew else 0


if __name__ == '__main__':
    sys.exit(main())
