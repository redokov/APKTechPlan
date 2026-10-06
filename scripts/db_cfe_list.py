#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Byte-safe 1C designer batch runner for this project (Cyrillic-safe).
Builds Cyrillic args in Python and calls CreateProcess directly."""
import subprocess, sys, os, tempfile, time

V8 = r'C:\Program Files\1cv8\8.5.4.1683\bin\1cv8.exe'
SERVER = 'localhost'
REF = 'dev_erpapk_demo'
# user candidates: built from unicode escapes, no inline Cyrillic needed
ADMIN = '\u0410\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0430\u0442\u043e\u0440'  # Администратор
ADMIN_ORLOV = ADMIN + ' (\u041e\u0440\u043b\u043e\u0432\u0410\u0412)'


def run_designer(args, user=ADMIN_ORLOV, timeout=600, out_to=None):
    """Run 1cv8 DESIGNER batch command, return (rc, stdout_text)."""
    tmp = out_to or os.path.join(tempfile.gettempdir(), f'apkplan_{int(time.time())}.txt')
    cmd = [V8, 'DESIGNER', f'/S', f'{SERVER}\\{REF}', f'/N{user}', '/DisableStartupDialogs']
    # NOTE: /P with empty password would swallow the next arg -> interactive login hang.
    # Omit /P entirely when password is empty.
    if out_to is None:
        cmd += ['/Out', tmp]
    cmd += args
    p = subprocess.run(cmd, capture_output=True, timeout=timeout)
    if p.returncode not in (0,) or p.stderr:
        sys.stderr.write(f'designer rc={p.returncode} stderr={p.stderr[:500]}\n')
    out = ''
    if os.path.exists(tmp):
        raw = open(tmp, 'rb').read()
        for enc in ('utf-8', 'cp1251'):
            try:
                out = raw.decode(enc)
                break
            except UnicodeDecodeError:
                continue
    return p.returncode, out


def try_users():
    for u in (ADMIN, ADMIN_ORLOV):
        rc, out = run_designer(['/DumpDBCfgList', '-AllExtensions'], user=u)
        ok = 'не идентифицирован' not in out
        print(f'user={u!r} rc={rc} auth_ok={ok}')
        print(out[:2000])
        if ok:
            return u
    return None


if __name__ == '__main__':
    u = try_users()
    print('WORKING USER:', repr(u))
