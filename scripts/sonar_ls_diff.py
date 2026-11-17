# -*- coding: utf-8 -*-
"""Diff two bsl-ls JSON reports: baseline (HEAD) vs working tree.

Prints per-file, per-rule delta for the rules that Sonar counted as
"new code" violations, and flags any rule whose count went UP.
"""
import collections
import json
import sys

BASE = 'tmp/night/lsbase/bsl-json.json'
NOW = 'tmp/night/lsreport/bsl-json.json'
SEP = 'ПланированиеТехникиАПК/'


def load(path):
    rep = json.load(open(path, encoding='utf-8'))
    out = collections.Counter()
    infos = rep.get('fileinfos') or rep.get('files') or []
    for fi in infos:
        p = (fi.get('path') or fi.get('file') or '').replace(chr(92), '/')
        short = p.split(SEP)[-1] if SEP in p else p
        for d in fi.get('diagnostics') or []:
            code = (d.get('code') or '').split(':')[-1]
            out[(short, code)] += 1
    return out


def main():
    base = load(BASE)
    now = load(NOW)
    keys = sorted(set(base) | set(now))
    went_up = []
    sys.stdout.write('%-58s %-34s %5s %5s %6s\n' % ('file', 'rule', 'base', 'now', 'delta'))
    for key in keys:
        b, n = base.get(key, 0), now.get(key, 0)
        if b == n:
            continue
        if n > b:
            went_up.append((key, b, n))
        sys.stdout.write('%-58s %-34s %5d %5d %+6d\n' % (key[0][-58:], key[1], b, n, n - b))
    sys.stdout.write('\n=== totals: base=%d now=%d ===\n' % (sum(base.values()), sum(now.values())))
    if went_up:
        sys.stdout.write('\n!! rule counts that INCREASED (%d) !!\n' % len(went_up))
        for key, b, n in went_up:
            sys.stdout.write('   %s %s: %d -> %d\n' % (key[0], key[1], b, n))
    else:
        sys.stdout.write('\nOK: no rule count increased anywhere.\n')


main()
