#!/bin/bash
cd /c/MyProjects/APKTechPlan
export PYTHONIOENCODING=utf-8 PYTHONUTF8=1
for f in 01-zameshchenie-po-shirine 02-zameshchenie-po-moshchnosti 03-plan-tehresursov-prinyatye-tc 04-preduprezhdenie-ts-dva-podrazdeleniya 05-raschet-deficita-i-filtry-otcheta 06-otchet-tolko-defitsitnye-stroki 07-pometka-koeffitsient-ne-zadan 09-prava-agronom; do
  echo "=== START $f $(date +%H:%M:%S)"
  python3 scripts/run_va_feature.py "C:/MyProjects/APKTechPlan/tests/vanessa/$f.feature" 900 2>&1 | grep -E "^\[va\]|PASS|FAIL|Traceback" | tail -3
  echo "=== END $f $(date +%H:%M:%S) rc=$?"
done
echo "ALL DONE"
