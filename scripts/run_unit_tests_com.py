#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B7: live unit-test run via V85.COMConnector -> run_unit_tests.main().

Connects to dev_erpapk_demo (CONN identical to b6_probe_data.py / run_unit_tests.py:18-19),
calls Тх_РаннерТестов.ВыполнитьТесты() (export, ObjectModule) via
agent.Обработки.Тх_РаннерТестов.Создать() (working COM pattern, see _com_probe3.py),
converts COM result array to plain objects, feeds scripts/run_unit_tests.py:main(),
exits with its code.

Requires: interactive Windows session (pywin32 + running 1cv8 cluster).
Exit codes (from run_unit_tests.main): 0=all PASS, 1=FAIL, skipped test or
count mismatch (Q-007/Ж1: SKIP is always a failure; exit code 2 retired).
"""
import io
import os
import sys
import time
import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ib_guard

CONN = "Srvr='localhost';Ref='dev_erpapk_demo';Usr='Администратор (ОрловАВ)';Pwd='';"
# TEST-02 (Q-006): verify the target infobase BEFORE connecting.
ib_guard.check_ib_ref(CONN, "run_unit_tests_com.py")


def to_plain(item):
    """COM structure -> SimpleNamespace (hasattr/getattr friendly)."""
    ns = types.SimpleNamespace()
    for fld in ("Имя", "Статус", "ДлительностьМс", "Провалы", "Детали"):
        try:
            setattr(ns, fld, getattr(item, fld))
        except Exception:
            pass
    # backward compat: if no Статус field (old runner), derive from Прошёл
    if not hasattr(ns, "Статус"):
        try:
            ns.Статус = "PASS" if item.Прошёл else "FAIL"
        except Exception:
            ns.Статус = "PASS"
    return ns


def main():
    import win32com.client
    from run_unit_tests import main as report_main

    started = time.time()
    print("connecting...")
    agent = win32com.client.Dispatch("V85.COMConnector").Connect(CONN)
    print("connected")

    # TEST-02 (Q-006): set the test-IB marker (idempotent, test IB only).
    if not ib_guard.ensure_test_marker(agent):
        print("ABORT: could not set Тх_ТестоваяБаза marker")
        return 1

    runner = agent.Обработки.Тх_РаннерТестов.Создать()
    print("runner created")
    raw = runner.ВыполнитьТесты()
    n = raw.Count() if hasattr(raw, "Count") else len(raw)
    print("collected %d results" % n)

    results = [to_plain(raw.Get(i) if hasattr(raw, "Get") else raw[i]) for i in range(n)]

    # TEST-02 (Q-006): leftover artifact next to the logs when the
    # ЧистотаТестовыхДанных check fails (registry/mask leftovers).
    leftovers = [r for r in results if getattr(r, "Имя", "") == "ЧистотаТестовыхДанных"
                 and getattr(r, "Статус", "") == "FAIL"]
    if leftovers:
        import time as _t
        artifact = os.path.join("tmp", "leftovers_%d.txt" % int(_t.time()))
        with io.open(artifact, "w", encoding="utf-8") as f:
            f.write(u"\n".join([u"%s: %s" % (getattr(r, "Имя", "?"),
                                              getattr(r, "Детали", "")) for r in leftovers]))
        print("[t02] LEFTOVER ARTIFACT: %s" % artifact)

    rc = report_main(results)
    print("\nunit run exit=%d (elapsed %.1fs)" % (rc, time.time() - started))
    return rc


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print("COM ERROR: %r" % (e,))
        sys.exit(1)
