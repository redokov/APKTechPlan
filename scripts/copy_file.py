#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Copy a generated artifact from a Latin-named .build path to its final
(Cyrillic-named) destination inside the project.

Cyrillic paths must never travel through bash argv (transport mangling);
they live only inside the job JSON written by the agent's write tool.

Job JSON: {"src": "<latin path>", "dst": "<final path>"}
Relative paths resolve against the project root. Parent dirs are created.

Usage: python scripts/copy_file.py <job.json>
"""
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resolve(p):
    p = str(p)
    return p if os.path.isabs(p) else os.path.normpath(os.path.join(ROOT, p))


def main():
    if len(sys.argv) != 2:
        print('Usage: copy_file.py <job.json>', file=sys.stderr)
        sys.exit(2)
    with open(sys.argv[1], 'r', encoding='utf-8-sig') as f:
        job = json.load(f)
    src = resolve(job['src'])
    dst = resolve(job['dst'])
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)
    print('copied: %s -> %s' % (src, dst))


if __name__ == '__main__':
    main()
