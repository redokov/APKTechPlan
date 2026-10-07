#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B3: delete TestKrossSsylok extension from dev_erpapk_demo.
Batch key per 1c-cli-ops skill: /DeleteCfg -Extension <Имя>
(NOT /DeleteExtension - no such batch key, opens interactive configurator).
Cyrillic name built from unicode escapes (never inline in argv)."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from db_cfe_list import run_designer, ADMIN_ORLOV

NAME = "\u0422\u0435\u0441\u0442\u041a\u0440\u043e\u0441\u0441\u0421\u0441\u044b\u043b\u043e\u043a"  # ТестКроссСсылок

rc, out = run_designer(["/DeleteCfg", "-Extension", NAME], user=ADMIN_ORLOV, timeout=600)
print("rc=%s" % rc)
print(out)

# verify: list extensions again
rc2, out2 = run_designer(["/ListExtensions"], user=ADMIN_ORLOV, timeout=600)
print("--- after ---")
print(out2)
