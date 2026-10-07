import subprocess, sys, os, tempfile, time, io
sys.stdout.reconfigure(encoding='utf-8')

V8 = r'C:\Program Files\1cv8\8.5.4.1683\bin\1cv8.exe'
ADMIN_ORLOV = 'Администратор (ОрловАВ)'

def designer(args, timeout=900):
    tmp = os.path.join(tempfile.gettempdir(), 'apkplan_cfe_%d.txt' % int(time.time()))
    cmd = [V8, 'DESIGNER', '/S', 'localhost\\dev_erpapk_demo',
           '/N' + ADMIN_ORLOV, '/DisableStartupDialogs', '/Out', tmp] + args
    p = subprocess.run(cmd, capture_output=True, timeout=timeout)
    log = ''
    if os.path.isfile(tmp):
        log = io.open(tmp, 'rb').read().decode('utf-8', errors='replace')
        os.remove(tmp)
    return p.returncode, log

if __name__ == '__main__':
    rc, log = designer(['/DumpDBCfgList', '-AllExtensions'])
    print('exit', rc)
    print('--- log ---')
    print(log)
