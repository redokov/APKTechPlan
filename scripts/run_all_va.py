#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run ALL Vanessa features sequentially and print a verdict table.

Sequential is mandatory: Vanessa single manages one TestClient on a shared
port (48000), so parallel runs clobber each other.

Verdict sources (strict, machine-readable first; see run_va_feature.py):
  1) va_status_<stem>.log -- VA status artifact (BOM + error count, "0"=PASS)
  2) va_1c_<stem>.log    -- 1C /Out verdict line (line-scoped exact sentence)
Inconclusive or contradictory artifacts -> UNKNOWN (never a guessed PASS).
(process exit code is always 0 and proves nothing)

The per-feature verdict artifacts (va_1c_/va_run_/va_status_) are removed
before each run so a stale artifact can never fabricate a verdict.

Offline self-test (no COM/Vanessa/IB is launched):
  python scripts/run_all_va.py --selftest

Usage: python scripts/run_all_va.py [timeout_per_feature]
"""
import glob
import os
import subprocess
import sys
import tempfile
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEATURES_DIR = os.path.join(ROOT, "tests", "vanessa")
HEARTBEAT = os.path.join(ROOT, "heartbeat")
RUNNER = os.path.join(ROOT, "scripts", "run_va_feature.py")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_va_feature import verdict_from_files  # noqa: E402  (shared strict parser)

ARTIFACTS = ("va_1c_%s.log", "va_run_%s.log", "va_status_%s.log")


def verdict_of(stem, heartbeat=HEARTBEAT):
    """Strict verdict for one feature stem. Returns (status, detail)."""
    onec_log = os.path.join(heartbeat, "va_1c_%s.log" % stem)
    status_log = os.path.join(heartbeat, "va_status_%s.log" % stem)
    if not os.path.exists(onec_log) and not os.path.exists(status_log):
        return "NO-LOG", ""
    verdict, _source, note = verdict_from_files(onec_log, status_log)
    if verdict == "PASS":
        return "PASS", ""
    if verdict == "FAIL":
        raw = open(onec_log, "rb").read() if os.path.exists(onec_log) else b""
        first = ""
        if raw:
            from run_va_feature import decode_artifact
            txt, _enc = decode_artifact(raw)
            for line in txt.splitlines():
                if u"не выполнен" in line or u"Ошибка" in line:
                    first = line.strip()[:180]
                    break
        return "FAIL", first or note
    # UNKNOWN: show the parser note (or first log line) as detail
    return "UNKNOWN", note


def _selftest():
    tmp = tempfile.mkdtemp(prefix="va_all_verdict_")
    cases = [
        # (stem-suffix, status_bytes, log_lines, expected, has_detail)
        ("pass", b"\xef\xbb\xbf0",
         [u"07.11.2026 10:00:00 Выполнение сценариев закончено. Ошибок не было."],
         "PASS", False),
        ("fail", b"\xef\xbb\xbf3",
         [u"07.11.2026 10:00:00 Выполнение сценариев закончено. БЫЛИ ОШИБКИ.",
          u"07.11.2026 10:00:01 Сценарий не выполнен: шаг упал"],
         "FAIL", True),
        ("unknown_fragment", None,
         [u"07.11.2026 10:00:00 ... Ошибок не было"],
         "UNKNOWN", True),
        ("no_log", None, None, "NO-LOG", False),
        ("conflict", b"\xef\xbb\xbf0",
         [u"07.11.2026 10:00:00 Выполнение сценариев закончено. БЫЛИ ОШИБКИ."],
         "UNKNOWN", True),
    ]
    failures = []
    try:
        for suffix, st_bytes, log_lines, expected, want_detail in cases:
            stem = "selftest_" + suffix
            if st_bytes is not None:
                with open(os.path.join(tmp, "va_status_%s.log" % stem), "wb") as f:
                    f.write(st_bytes)
            if log_lines is not None:
                with open(os.path.join(tmp, "va_1c_%s.log" % stem), "wb") as f:
                    f.write(("\r\n".join(log_lines)).encode("utf-8-sig"))
            status, detail = verdict_of(stem, heartbeat=tmp)
            ok = status == expected and bool(detail) == want_detail
            print("  [%s] %-18s -> %s detail=%r (want %s, detail=%s)"
                  % ("ok" if ok else "FAIL", suffix, status, detail[:60] if detail else "",
                     expected, want_detail))
            if not ok:
                failures.append(suffix)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    total = len(cases)
    print("[selftest] run_all_va verdict_of: %d/%d ok" % (total - len(failures), total))
    if failures:
        print("[selftest] FAILURES: %s" % ", ".join(failures))
        return 1
    print("[selftest] PASS (offline fixtures only; no COM/Vanessa/IB launched)")
    return 0


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        return _selftest()
    timeout = int(sys.argv[1]) if len(sys.argv) > 1 else 900
    features = sorted(glob.glob(os.path.join(FEATURES_DIR, "*.feature")))
    results = []
    import time
    t_all = time.time()
    for i, path in enumerate(features, 1):
        stem = os.path.splitext(os.path.basename(path))[0]
        print("\n[%d/%d] %s" % (i, len(features), stem), flush=True)
        for tpl in ARTIFACTS:
            p = os.path.join(HEARTBEAT, tpl % stem)
            if os.path.exists(p):
                os.remove(p)
        t0 = time.time()
        try:
            subprocess.run([sys.executable, RUNNER, path, str(timeout)],
                           cwd=ROOT, timeout=timeout + 180)
        except subprocess.TimeoutExpired:
            print("  runner timeout", flush=True)
        status, detail = verdict_of(stem)
        dt = time.time() - t0
        results.append((stem, status, detail, dt))
        print("  -> %s (%.0fs)%s" % (status, dt, ("  " + detail) if detail else ""), flush=True)

    print("\n" + "=" * 78)
    print("%-45s %-8s %8s" % ("feature", "verdict", "time"))
    print("-" * 78)
    for stem, status, _d, dt in results:
        print("%-45s %-8s %7.0fs" % (stem, status, dt))
    print("-" * 78)
    passed = sum(1 for r in results if r[1] == "PASS")
    print("PASS %d / %d   total %.1f min"
          % (passed, len(results), (time.time() - t_all) / 60.0))
    # Non-PASS (FAIL/UNKNOWN/NO-LOG) is reported as failure: no verdict is
    # guessed. A SKIP terminal policy is NOT introduced here (spec-003
    # Q-007 remains open); these VA artifacts carry no SKIP token.
    failed = [r for r in results if r[1] != "PASS"]
    if failed:
        print("\nFailures:")
        for stem, status, detail, _dt in failed:
            print("  %s: %s" % (stem, status))
            if detail:
                print("    %s" % detail)
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
