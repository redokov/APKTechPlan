#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run ALL Vanessa features sequentially and print a verdict table.

Sequential is mandatory: Vanessa single manages one TestClient on a shared
port (48000), so parallel runs clobber each other.

Verdict source: the 1C /Out log line
  "Выполнение сценариев закончено. Ошибок не было."  -> PASS
  "Выполнение сценариев закончено. БЫЛИ ОШИБКИ."     -> FAIL
(process exit code is always 0 and proves nothing)

Usage: python scripts/run_all_va.py [timeout_per_feature]
"""
import glob
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEATURES_DIR = os.path.join(ROOT, "tests", "vanessa")
HEARTBEAT = os.path.join(ROOT, "heartbeat")
RUNNER = os.path.join(ROOT, "scripts", "run_va_feature.py")

PASS_LINE = "Ошибок не было"
FAIL_LINE = "БЫЛИ ОШИБКИ"


def verdict_of(stem):
    log = os.path.join(HEARTBEAT, "va_1c_%s.log" % stem)
    if not os.path.exists(log):
        return "NO-LOG", ""
    raw = open(log, "rb").read()
    for enc in ("utf-8-sig", "utf-8", "cp1251"):
        try:
            txt = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        txt = raw.decode("utf-8", errors="replace")
    if FAIL_LINE in txt:
        first = ""
        for line in txt.splitlines():
            if "не выполнен" in line or "Ошибка" in line:
                first = line.strip()[:180]
                break
        return "FAIL", first
    if PASS_LINE in txt:
        return "PASS", ""
    return "UNKNOWN", txt.strip().splitlines()[0][:180] if txt.strip() else ""


def main():
    timeout = int(sys.argv[1]) if len(sys.argv) > 1 else 900
    features = sorted(glob.glob(os.path.join(FEATURES_DIR, "*.feature")))
    results = []
    t_all = time.time()
    for i, path in enumerate(features, 1):
        stem = os.path.splitext(os.path.basename(path))[0]
        print("\n[%d/%d] %s" % (i, len(features), stem), flush=True)
        for f in ("va_1c_%s.log" % stem, "va_run_%s.log" % stem):
            p = os.path.join(HEARTBEAT, f)
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
