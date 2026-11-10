#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sequential VA suite run for the TEST-01 closeout protocol:
features 01-08 via run_va_feature.py, feature 09 via the t12 roles driver.
Strict verdicts only (status artifacts), no guessed PASS."""
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from run_all_va import verdict_of  # noqa: E402

FEAT = os.path.join(ROOT, "tests", "vanessa")
HB = os.path.join(ROOT, "heartbeat")

STEMS = [
    "01-zameshchenie-po-shirine",
    "02-zameshchenie-po-moshchnosti",
    "03-plan-tehresursov-prinyatye-tc",
    "04-preduprezhdenie-ts-dva-podrazdeleniya",
    "05-raschet-deficita-i-filtry-otcheta",
    "06-otchet-tolko-defitsitnye-stroki",
    "07-pometka-koeffitsient-ne-zadan",
    "08-formirovanie-plana-rabot-tekhniki",
]


def main():
    results = []
    t_all = time.time()
    for stem in STEMS:
        path = os.path.join(FEAT, stem + ".feature")
        for tpl in ("va_1c_%s.log", "va_run_%s.log", "va_status_%s.log"):
            p = os.path.join(HB, tpl % stem)
            if os.path.exists(p):
                os.remove(p)
        t0 = time.time()
        print("[%s] start" % stem, flush=True)
        try:
            subprocess.run([sys.executable, os.path.join(ROOT, "scripts",
                           "run_va_feature.py"), path, "900"],
                           cwd=ROOT, timeout=1080)
        except subprocess.TimeoutExpired:
            print("[%s] runner timeout" % stem, flush=True)
        status, detail = verdict_of(stem)
        results.append((stem, status, detail))
        print("[%s] -> %s (%.0fs) %s" % (stem, status, time.time() - t0, detail),
              flush=True)

    # 09 via the roles driver
    t0 = time.time()
    print("[09-prava-agronom] start (t12 driver)", flush=True)
    try:
        rc = subprocess.run([sys.executable, os.path.join(ROOT, "scripts",
                             "run_t12_roles.py")], cwd=ROOT, timeout=2400).returncode
    except subprocess.TimeoutExpired:
        rc = -1
        print("[09-prava-agronom] driver timeout", flush=True)
    ok9 = (rc == 0)
    results.append(("09-prava-agronom",
                     "PASS" if ok9 else "FAIL",
                     "driver rc=%s" % rc))
    print("[09-prava-agronom] -> %s (%.0fs) rc=%s" %
          ("PASS" if ok9 else "FAIL", time.time() - t0, rc), flush=True)

    print("=" * 60, flush=True)
    bad = [r for r in results if r[1] != "PASS"]
    print("SUITE: %d/%d PASS, total %.1f min" %
          (len(results) - len(bad), len(results), (time.time() - t_all) / 60.0),
          flush=True)
    for stem, status, detail in bad:
        print("  FAIL %s %s" % (stem, detail), flush=True)
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
