#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OCR презентационных скриншотов через WinRT (img-ocr skill script)."""
import subprocess, os, sys

OCR = r'C:\MyProjects\PiPack\skills\core\img-ocr\scripts\ocr.ps1'
DIR = r'C:\MyProjects\MyTasks\out\TechPlanning'
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs', 'screenshots-ocr.txt')

def main():
    out = []
    for f in ['s01', 's02', 's03', 's04', 's05']:
        p = os.path.join(DIR, f + '.png')
        r = subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                            '-File', OCR, p, 'ru-RU', 'raw'],
                           capture_output=True, timeout=90)
        out.append('=== ' + f + ' === ' + p)
        out.append(r.stdout.decode('utf-8', errors='replace'))
        if r.returncode != 0:
            out.append('STDERR: ' + r.stderr.decode('utf-8', errors='replace')[:300])
        out.append('-----')
    open(OUT, 'w', encoding='utf-8').write('\n'.join(out))
    print('written:', OUT, 'bytes:', sum(len(o) for o in out))

if __name__ == '__main__':
    main()
