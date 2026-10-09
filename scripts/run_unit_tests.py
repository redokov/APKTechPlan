#!/usr/bin/env python3
"""B5: run unit tests headless via V83.COMConnector.

Connects to dev_erpapk_demo, creates Tkh_RannnerTestov data processor,
calls VypolnitTesty() (COM: Latin-safe transliteration is NOT used - COM
dispatch resolves Cyrillic method names fine from python string literals).
Prints per-test results and a summary. Exit 0 iff all 20 tests report
Passed=True (SKIPs are reported by the runner as True per A11 design).
"""
import sys
import time

import win32com.client

CONN_STRING = (
    "Srvr='localhost';Ref='dev_erpapk_demo';"
    "Usr='Администратор (ОрловАВ)';Pwd='';"
)

def main():
    print("[com] connecting...")
    connector = win32com.client.Dispatch("V85.COMConnector")
    try:
        agent = connector.Connect(CONN_STRING)
    except Exception as e:
        print("[com] CONNECT FAILED: %s" % e)
        return 2
    print("[com] connected")
    try:
        runner = agent.Обработки.Тх_РаннерТестов.Создать()
        t0 = time.time()
        results = runner.ВыполнитьТесты()
        elapsed = time.time() - t0
    except Exception as e:
        print("[com] RUN FAILED: %s" % e)
        return 2

    # user messages (SKIP/ПРОВАЛ diagnostics) from the external connection buffer
    try:
        msgs = agent.ПолучитьСообщенияПользователю()
        if msgs is not None:
            for m in msgs:
                print("[msg] " + m.Текст)
    except Exception as e:
        print("[msg] messages unavailable: %r" % (e,))

    passed = failed = total = 0
    print("\n%-58s %-8s %s" % ("TEST", "RESULT", "MS"))
    for item in results:
        total += 1
        name = item.Имя
        ok = bool(item.Прошёл)
        ms = item.ДлительностьМс
        if ok:
            passed += 1
        else:
            failed += 1
        details = ""
        try:
            details = item.Детали
        except Exception:
            pass
        line = "%-58s %-8s %s" % (name, "PASS" if ok else "FAIL", ms)
        print(line)
        if details:
            for dl in str(details).splitlines():
                print("    | " + dl)
    print("\n[summary] total=%d passed=%d failed=%d wall=%.1fs"
          % (total, passed, failed, elapsed))
    if total != 20:
        print("UNEXPECTED: expected 13 tests, got %d" % total)
        return 1
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
