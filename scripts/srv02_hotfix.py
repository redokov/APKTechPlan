#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SRV-02 hotfix: two fixes in uncommitted working tree.

Fix 1 (server module): ВыполнитьЗапросАПК error handler called
ЗаписьЖурналаРегистрации with 6 args - the СтрШаблон template went into
param 5 (Комментарий) and ОписаниеОшибки() into param 6 (РежимТранзакции,
expects enum) -> runtime "Несоответствие типов (параметр номер 6)".
Merge into a single comment arg; normalize indentation of the block.

Fix 2 (test module): fixture ЗаписатьПрипискуТС wrote
Запись.ЭксплуатирующеПодразделение (single 'е', 27 chars) but the real
register field is ЭксплуатирующееПодразделение (double 'е', 28 chars).
Fix bytes exactly.

Both edits are located by unique byte anchors; script fails loudly if an
anchor is not found exactly once. Writes files back in UTF-8 (no BOM),
LF/CR? -> preserves original newline style.
"""
import io
import sys

SERVER = "src/cfe/ПланированиеТехникиАПК/CommonModules/Тх_ТехникаСервер/Ext/Module.bsl"
TESTS = "src/cfe/ПланированиеТехникиАПК/CommonModules/Тх_Тесты/Ext/Module.bsl"

def load(path):
    with io.open(path, "r", encoding="utf-8") as f:
        return f.read()

def save(path, text):
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)

def replace_once(text, old, new, what):
    n = text.count(old)
    if n != 1:
        print("FAIL anchor %s: found %d occurrences" % (what, n))
        sys.exit(1)
    return text.replace(old, new)

# ---- Fix 1: server module journal call ----
src = load(SERVER)

# build anchors from template strings (UTF-8 source, safe here)
old_journal = (
    "\t\t\t\t\u0423\u0440\u043e\u0432\u0435\u043d\u044c\u0416\u0443\u0440\u043d\u0430\u043b\u0430\u0420\u0435\u0433\u0438\u0441\u0442\u0440\u0430\u0446\u0438\u0438.\u041e\u0448\u0438\u0431\u043a\u0430,,,\n"
    "\t\t\t\t\t\u041d\u0421\u0442\u0440(\"ru = '\u0422\u0435\u043a\u0441\u0442: %1'\"), \u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435\u041e\u0448\u0438\u0431\u043a\u0438());"
)
new_journal = (
    "\t\t\t\t\u0423\u0440\u043e\u0432\u0435\u043d\u044c\u0416\u0443\u0440\u043d\u0430\u043b\u0430\u0420\u0435\u0433\u0438\u0441\u0442\u0440\u0430\u0446\u0438\u0438.\u041e\u0448\u0438\u0431\u043a\u0430,,,\n"
    "\t\t\t\t\t\u0421\u0442\u0440\u0428\u0430\u0431\u043b\u043e\u043d(\u041d\u0421\u0442\u0440(\"ru = '\u0422\u0435\u043a\u0441\u0442: %1'\"), \u0422\u0435\u043a\u0441\u0442\u041e\u0448\u0438\u0431\u043a\u0438));"
)
src = replace_once(src, old_journal, new_journal, "journal-6args")

# reuse captured ТекстОшибки instead of second ОписаниеОшибки() (re-raise text)
old_raise2 = (
    "\t\t\t\t\u0412\u044b\u0437\u0432\u0430\u0442\u044c\u0418\u0441\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u0435 \u0421\u0442\u0440\u0428\u0430\u0431\u043b\u043e\u043d(\n"
    "\t\t\t\t\t\u041d\u0421\u0442\u0440(\"ru = '\u041e\u0448\u0438\u0431\u043a\u0430 \u0432\u044b\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u044f \u0437\u0430\u043f\u0440\u043e\u0441\u0430 \u0410\u041f\u041a: %1'\"),\n"
    "\t\t\t\t\t\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435\u041e\u0448\u0438\u0431\u043a\u0438());"
)
new_raise2 = (
    "\t\t\t\t\u0412\u044b\u0437\u0432\u0430\u0442\u044c\u0418\u0441\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u0435 \u0421\u0442\u0440\u0428\u0430\u0431\u043b\u043e\u043d(\n"
    "\t\t\t\t\t\u041d\u0421\u0442\u0440(\"ru = '\u041e\u0448\u0438\u0431\u043a\u0430 \u0432\u044b\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u044f \u0437\u0430\u043f\u0440\u043e\u0441\u0430 \u0410\u041f\u041a: %1'\"),\n"
    "\t\t\t\t\t\u0422\u0435\u043a\u0441\u0442\u041e\u0448\u0438\u0431\u043a\u0438);"
)
src = replace_once(src, old_raise2, new_raise2, "raise-query")

# level-1 branch: reuse ТекстОшибки in journal + raise (two ОписаниеОшибки() kept only first)
old_j1 = (
    "\t\t\t\t\t\u0423\u0440\u043e\u0432\u0435\u043d\u044c\u0416\u0443\u0440\u043d\u0430\u043b\u0430\u0420\u0435\u0433\u0438\u0441\u0442\u0440\u0430\u0446\u0438\u0438.\u041e\u0448\u0438\u0431\u043a\u0430,,, \u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435\u041e\u0448\u0438\u0431\u043a\u0438());"
)
new_j1 = (
    "\t\t\t\t\t\u0423\u0440\u043e\u0432\u0435\u043d\u044c\u0416\u0443\u0440\u043d\u0430\u043b\u0430\u0420\u0435\u0433\u0438\u0441\u0442\u0440\u0430\u0446\u0438\u0438.\u041e\u0448\u0438\u0431\u043a\u0430,,, \u0422\u0435\u043a\u0441\u0442\u041e\u0448\u0438\u0431\u043a\u0438);"
)
src = replace_once(src, old_j1, new_j1, "journal-disabled")

old_r1 = (
    "\t\t\t\t\t\u041d\u0421\u0442\u0440(\"ru = '\u041c\u043e\u0434\u0443\u043b\u044c \u0410\u041f\u041a \u043e\u0442\u043a\u043b\u044e\u0447\u0451\u043d, \u0440\u0430\u0441\u0447\u0451\u0442 \u043d\u0435\u0432\u043e\u0437\u043c\u043e\u0436\u0435\u043d: %1'\"),\n"
    "\t\t\t\t\t\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435\u041e\u0448\u0438\u0431\u043a\u0438());"
)
new_r1 = (
    "\t\t\t\t\t\u041d\u0421\u0442\u0440(\"ru = '\u041c\u043e\u0434\u0443\u043b\u044c \u0410\u041f\u041a \u043e\u0442\u043a\u043b\u044e\u0447\u0451\u043d, \u0440\u0430\u0441\u0447\u0451\u0442 \u043d\u0435\u0432\u043e\u0437\u043c\u043e\u0436\u0435\u043d: %1'\"),\n"
    "\t\t\t\t\t\u0422\u0435\u043a\u0441\u0442\u041e\u0448\u0438\u0431\u043a\u0438);"
)
src = replace_once(src, old_r1, new_r1, "raise-disabled")

save(SERVER, src)
print("OK server module: journal args fixed, ТекстОшибки reused")

# ---- Fix 2: test module fixture field name ----
tst = load(TESTS)
bad = "\u042d\u043a\u0441\u043f\u043b\u0443\u0430\u0442\u0438\u0440\u0443\u044e\u0449\u0435\u041f\u043e\u0434\u0440\u0430\u0437\u0434\u0435\u043b\u0435\u043d\u0438\u0435"  # single е + П
good = "\u042d\u043a\u0441\u043f\u043b\u0443\u0430\u0442\u0438\u0440\u0443\u044e\u0449\u0435\u0435\u041f\u043e\u0434\u0440\u0430\u0437\u0434\u0435\u043b\u0435\u043d\u0438\u0435"  # ее + П
n = tst.count(bad)
if n < 1:
    print("FAIL: no misspelled field name found in test module")
    sys.exit(1)
tst = tst.replace(bad, good)
save(TESTS, tst)
print("OK test module: %d field-name occurrences fixed (е->ее)" % n)
