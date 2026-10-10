#!/usr/bin/env python3
"""B6: run one Vanessa Automation feature file via TestManager + TestClient.

Pattern from the vanessa-automation skill:
  - 1cv8c (thin client) ENTERPRISE /TESTMANAGER
  - /S localhost\\dev_erpapk_demo, user with empty password (/P "")
  - /Execute vanessa-automation-single.epf
  - /CStartFeaturePlayer;VAParams=<json>   (VAParams generated per run)
  - verdict is read from the 1C /Out log line
    "Выполнение сценариев закончено. Ошибок не было." / "... БЫЛИ ОШИБКИ."
  - process exit code is NOT a verdict (always 0)

Usage: python scripts/run_va_feature.py <feature-file> [timeout_sec]
"""
import io
import json
import os
import subprocess
import sys
import time

V8C = r"C:\Program Files\1cv8\8.5.4.1683\bin\1cv8c.exe"
EPF = r"C:\MyProjects\APKTechPlan\tests\vanessa\vanessa-automation-single.epf"
USER = "Администратор (ОрловАВ)"
BASE = r"localhost\dev_erpapk_demo"
LOGDIR = r"C:\MyProjects\APKTechPlan\heartbeat"

PASS_LINE = "Выполнение сценариев закончено. Ошибок не было"
FAIL_LINE = "Выполнение сценариев закончено. БЫЛИ ОШИБКИ"

ROLES_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "va_assign_roles_direct.py")


def ensure_roles():
    """BSP access-management periodically rewrites IB-user roles from access
    groups and wipes manually assigned Tх_ roles (B6 finding: profile roles
    reference the extension-identifiers catalog which is never populated in
    this demo base). Restore the roles right before each run (idempotent)."""
    print("[va] ensuring Tх_ roles on IB user")
    p = subprocess.run(
        [sys.executable, ROLES_SCRIPT, USER, "add"],
        capture_output=True, timeout=300)
    tail = (p.stdout or b"")[-200:].decode("utf-8", errors="replace")
    print("[va] ensure_roles rc=%s %s" % (p.returncode, tail.strip()))
    return p.returncode == 0


def main():
    feature = os.path.abspath(sys.argv[1])
    timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 600
    # argv[3] (optional): test-client user override. TestManager stays under
    # USER (admin); only КлиентыТестирования connects as the override user.
    # Role ensure (admin's Tх_ roles) is skipped for override runs: the
    # override user's roles are managed by the caller (T12 stages).
    tc_user = sys.argv[3] if len(sys.argv) > 3 else None
    if tc_user is None:
        if not ensure_roles():
            print("[va] ABORT: could not ensure roles")
            return 2
    else:
        print("[va] test-client user override: " + tc_user)
    stem = os.path.splitext(os.path.basename(feature))[0]
    vap_path = os.path.join(LOGDIR, "vap_%s.json" % stem)
    onec_log = os.path.join(LOGDIR, "va_1c_%s.log" % stem)
    run_log = os.path.join(LOGDIR, "va_run_%s.log" % stem)
    for p in (onec_log, run_log):
        if os.path.exists(p):
            os.remove(p)

    vap = {
        "ИмяСборки": "B6 " + stem,
        "ВерсияПлатформы": "8.5.4",
        "КаталогПоискаВерсииПлатформы": r"C:\Program Files\1cv8",
        "СтрокаПодключенияКБазе": (
            'ENTERPRISE /S "%s" /N "%s" /P ""' % (BASE, USER)
        ),
        "ПутьКVanessaAutomation": EPF,
        "КаталогФич": feature.replace("\\", "/"),
        "КаталогиБиблиотек": [],
        "КлиентыТестирования": [
            {
                "Имя": "Основной",
                "ПутьКИнфобазе": '/S "%s" /N "%s" /P ""' % (
                    BASE, tc_user if tc_user is not None else USER),
                "ДопПараметры": (
                    "/DisableStartupMessages /DisableStartupDialogs"
                ),
                "ТипКлиента": "Тонкий",
                "ИмяКомпьютера": "localhost",
                "ПортЗапускаТестКлиента": "1538",
            }
        ],
        "ВыполнитьСценарии": "Истина",
        "ЗавершитьРаботуСистемы": "Истина",
        "ЗакрытьTestClientПослеЗапускаСценариев": "Истина",
        "ДелатьЛогВыполненияСценариевВТекстовыйФайл": "Истина",
        "ИмяФайлаЛогВыполненияСценариев": run_log.replace("\\", "/"),
        "ВыгружатьСтатусВыполненияСценариевВФайл": "Истина",
        "ПутьКФайлуДляВыгрузкиСтатусаВыполненияСценариев": (
            os.path.join(LOGDIR, "va_status_%s.log" % stem).replace("\\", "/")
        ),
        "ТаймаутЗапуска1С": "600",
    }
    with io.open(vap_path, "w", encoding="utf-8") as f:
        json.dump(vap, f, ensure_ascii=False)

    cmd = [
        V8C, "ENTERPRISE", "/TESTMANAGER",
        "/S", BASE,
        "/N", USER, "/P", "",
        "/Execute", EPF,
        "/CStartFeaturePlayer;VAParams=" + vap_path.replace("\\", "/"),
        "/DisableStartupDialogs", "/DisableStartupMessages",
        "/Out", onec_log,
    ]
    print("[va] launching TestManager for %s" % os.path.basename(feature))
    proc = subprocess.Popen(cmd)
    rc = None
    try:
        rc = proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                       capture_output=True)
        print("[va] TIMEOUT after %ds, killed" % timeout)
        return 124

    time.sleep(2)
    verdict = "UNKNOWN"
    if os.path.exists(onec_log):
        with io.open(onec_log, "r", encoding="utf-8-sig", errors="replace") as f:
            txt = f.read()
        if PASS_LINE in txt:
            verdict = "PASS"
        elif FAIL_LINE in txt:
            verdict = "FAIL"
        elif "Ошибок не было" in txt:
            verdict = "PASS"
        elif "БЫЛИ ОШИБКИ" in txt:
            verdict = "FAIL"
    print("[va] %s: %s (rc=%s)" % (os.path.basename(feature), verdict, rc))
    print("[va] 1C log: %s" % onec_log)
    print("[va] run log: %s" % run_log)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
