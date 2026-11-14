# -*- coding: utf-8 -*-
"""TEST-02 (Q-006): infobase-reference guard + test-IB marker setup.

Shared by the launch scripts (run_unit_tests_com.py, run_va_feature.py,
va_assign_roles_direct.py). The target infobase reference is verified
BEFORE anything is launched or connected; the Тх_ТестоваяБаза marker
constant is set (idempotently) only after the reference check passes,
so the marker can only ever be installed in a sanctioned test IB.
"""
import re

# The sanctioned test infobase(s). Anything else -> refuse before connect.
ALLOWED_IB_REFS = ("dev_erpapk_demo",)


def check_ib_ref(conn_string, label="launch script"):
    """Fail fast unless the connection string targets a sanctioned test IB.

    Returns the extracted Ref value on success; raises SystemExit with a
    clear message otherwise (TEST-02 checklist item 2: launch scripts
    verify the target infobase reference before running anything).
    """
    m = re.search(r"Ref='([^']+)'", conn_string)
    if not m:
        raise SystemExit(
            "[ib-guard] ABORT: no Ref=... in connection string (%s); "
            "refusing to run" % label)
    ref = m.group(1)
    if ref not in ALLOWED_IB_REFS:
        raise SystemExit(
            "[ib-guard] ABORT: infobase '%s' is not a sanctioned test IB "
            "(allowed: %s); refusing to run (Q-006/TEST-02)" % (
                ref, ", ".join(ALLOWED_IB_REFS)))
    return ref


def ensure_test_marker(agent):
    """Idempotently set the Тх_ТестоваяБаза constant to True (test IB only;
    call check_ib_ref() first). Returns True on success."""
    consts = agent.Константы
    if consts.Тх_ТестоваяБаза.Получить():
        return True
    consts.Тх_ТестоваяБаза.Установить(True)
    print("[ib-guard] Тх_ТестоваяБаза marker set to True")
    return bool(consts.Тх_ТестоваяБаза.Получить())
