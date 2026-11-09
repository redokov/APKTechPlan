#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Запуск модульных тестов Тх_Тесты из расширения ПланированиеТехникиАПК.

Статус каждого результата валидируется строго: распознаются только
PASS / FAIL / SKIP. Любое нераспознанное значение (в т.ч. отсутствующее
поле Статус) считается FAIL (fail-closed) и печатается явно — «молчаливый
PASS» для мусорного статуса больше невозможен.

Политика SKIP не меняется (spec-003 Q-007 остаётся открытой):
SKIP — явный, отдельный счётчик, exit-код 2, это не провал.
Exit-код 2 означает «SKIP-only» (без FAIL) — как задокументировано
в run_unit_tests_com.py; при одновременных FAIL и SKIP доминирует
FAIL (exit 1, fail-closed: провал не маскируется сигналом SKIP).

Offline self-test (без COM / ИБ / 1С):
  python scripts/run_unit_tests.py --selftest
"""
import io
import sys
import time
from contextlib import redirect_stdout

VALID_STATUSES = ("PASS", "FAIL", "SKIP")
EXPECTED_TOTAL = 20


def _get(obj, name, default=None):
    """Attribute access that tolerates COM/SimpleNamespace wrappers."""
    try:
        return getattr(obj, name)
    except Exception:
        return default


def summarize(results):
    """Strict per-item verdict classification. Returns (rows, counters).

    rows: list of (name, status_display, ms, details, invalid_raw)
    counters: dict with total/passed/skipped/failed
    """
    rows = []
    counters = {"total": 0, "passed": 0, "skipped": 0, "failed": 0}
    for item in results:
        counters["total"] += 1
        name = _get(item, "Имя", "<unnamed>")
        raw_status = _get(item, "Статус")
        status_txt = str(raw_status).strip() if raw_status is not None else ""
        invalid_raw = None
        if status_txt == "SKIP":
            counters["skipped"] += 1
            display = "SKIP"
        elif status_txt == "FAIL":
            counters["failed"] += 1
            display = "FAIL"
        elif status_txt == "PASS":
            counters["passed"] += 1
            display = "PASS"
        else:
            # Strict fail-closed: unrecognized/missing status is NOT a pass.
            counters["failed"] += 1
            display = "FAIL"
            invalid_raw = raw_status if raw_status is not None else "<missing Статус>"
        ms = _get(item, "ДлительностьМс", "")
        details = _get(item, "Детали", "")
        rows.append((name, display, ms, details, invalid_raw))
    return rows, counters


def exit_code(counters):
    """Exit-code policy: 0 PASS, 1 FAIL (dominates), 2 SKIP-only, 1 on count mismatch.

    2 is reserved for SKIP-only runs (documented contract in
    run_unit_tests_com.py: "0=PASS, 1=FAIL, 2=SKIP-only"); a FAIL is never
    masked by a concurrent SKIP. Whether SKIP itself is a CI failure stays
    undecided (spec-003 Q-007) and is NOT changed here.
    """
    if counters["total"] != EXPECTED_TOTAL:
        return 1
    if counters["failed"] > 0:
        return 1
    if counters["skipped"] > 0:
        return 2
    return 0


def main(results):
    started = time.time()
    rows, counters = summarize(results)
    print("\n%-58s %-8s %s" % ("TEST", "RESULT", "MS"))
    for name, display, ms, details, invalid_raw in rows:
        print("%-58s %-8s %s" % (name, display, ms))
        if invalid_raw is not None:
            print("    | INVALID STATUS: %r counted as FAIL (fail-closed)" % (invalid_raw,))
        if details:
            for dl in str(details).splitlines():
                print("    | " + dl)
    elapsed = time.time() - started
    print("\n[summary] total=%d passed=%d skipped=%d failed=%d wall=%.1fs"
          % (counters["total"], counters["passed"], counters["skipped"],
             counters["failed"], elapsed))
    if counters["total"] != EXPECTED_TOTAL:
        print("UNEXPECTED: expected %d tests, got %d" % (EXPECTED_TOTAL, counters["total"]))
        return 1
    if counters["failed"] > 0:
        if counters["skipped"] > 0:
            print("[skip] %d test(s) skipped (exit 1: failures dominate, skip signal does not mask FAIL)"
                  % counters["skipped"])
        return 1
    if counters["skipped"] > 0:
        print("[skip] %d test(s) skipped (exit code 2, not a failure)" % counters["skipped"])
        return 2
    return 0


# ---------------------------------------------------------------------------
# Offline fixtures / self-test.
# ---------------------------------------------------------------------------

class _Item(object):
    """Fixture result item (SimpleNamespace-compatible shape)."""

    def __init__(self, name, status=None, ms=10, details="", include_status=True):
        self.Имя = name
        if include_status:
            self.Статус = status
        self.ДлительностьМс = ms
        self.Детали = details


def _selftest():
    def run(counters_expect, code_expect, items):
        rows, c = summarize(items)
        code = exit_code(c)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(list(items))
        ok_c = all(c[k] == v for k, v in counters_expect.items())
        ok_code = code == code_expect and rc == code_expect
        ok_print = ("[summary]" in buf.getvalue())
        return ok_c and ok_code and ok_print, c, code, rc, buf.getvalue()

    cases = []
    p = lambda i: _Item("t%02d_pass" % i, "PASS")  # noqa: E731
    cases.append(("20x PASS -> 0", {"total": 20, "passed": 20, "skipped": 0, "failed": 0}, 0,
                  [p(i) for i in range(20)]))
    cases.append(("19 PASS + 1 FAIL -> 1", {"total": 20, "passed": 19, "skipped": 0, "failed": 1}, 1,
                  [p(i) for i in range(19)] + [_Item("t_fail", "FAIL")]))
    cases.append(("19 PASS + 1 SKIP -> 2 (SKIP preserved, not a failure)",
                  {"total": 20, "passed": 19, "skipped": 1, "failed": 0}, 2,
                  [p(i) for i in range(19)] + [_Item("t_skip", "SKIP")]))
    cases.append(("unknown status ERROR -> fail-closed 1",
                  {"total": 20, "passed": 19, "skipped": 0, "failed": 1}, 1,
                  [p(i) for i in range(19)] + [_Item("t_bad", "ERROR")]))
    cases.append(("missing Статус attribute -> fail-closed 1",
                  {"total": 20, "passed": 19, "skipped": 0, "failed": 1}, 1,
                  [p(i) for i in range(19)] + [_Item("t_nostatus", include_status=False)]))
    cases.append(("status with spaces ' PASS ' -> recognized",
                  {"total": 20, "passed": 20, "skipped": 0, "failed": 0}, 0,
                  [p(i) for i in range(19)] + [_Item("t_ws", " PASS ")]))
    cases.append(("total 19 -> 1 (count mismatch)", {"total": 19, "passed": 19, "skipped": 0, "failed": 0}, 1,
                  [p(i) for i in range(19)]))
    cases.append(("SKIP + FAIL -> 1 (FAIL dominates; 2 is SKIP-only per contract)",
                  {"total": 20, "passed": 18, "skipped": 1, "failed": 1}, 1,
                  [p(i) for i in range(18)] + [_Item("t_skip", "SKIP"), _Item("t_fail", "FAIL")]))

    failures = []
    for name, expect_c, expect_code, items in cases:
        ok, c, code, rc, out = run(expect_c, expect_code, items)
        marker = "ok" if ok else "FAIL"
        print("  [%s] %-52s counters=%s code=%d rc=%d" % (marker, name, c, code, rc))
        if not ok:
            failures.append(name)
            print("    want counters=%s code=%d" % (expect_c, expect_code))
            print("    output tail: %s" % out.strip().splitlines()[-1] if out.strip() else "")

    total = len(cases)
    print("[selftest] run_unit_tests strict status parsing: %d/%d ok" % (total - len(failures), total))
    if failures:
        print("[selftest] FAILURES: %s" % ", ".join(failures))
        return 1
    print("[selftest] PASS (offline fixtures only; no COM/IB launched)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        sys.exit(_selftest())
    # Live runs go through run_unit_tests_com.py, which imports main(results).
    print("usage: run_unit_tests.py --selftest   (offline verdict parsing check)\n"
          "       import run_unit_tests; run_unit_tests.main(results)  (live run)")
    sys.exit(2)
