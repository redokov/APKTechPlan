#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SRV-02 hotfix 3: МАКСИМУМ(Дата) over an empty set returns one row with
NULL, so ВыборкаДаты.Следующий() = Истина and ДатаСреза = NULL ->
СрезПоследних(&ДатаСреза) fails "Несоответствие типов (параметр 1)".
Add a post-fetch ЗначениеЗаполнено guard (covers NULL row and no-row).
"""
import io
import sys

SERVER = "src/cfe/ПланированиеТехникиАПК/CommonModules/Тх_ТехникаСервер/Ext/Module.bsl"

with io.open(SERVER, "r", encoding="utf-8") as f:
    src = f.read()

# anchor: the Иначе-branch tail from hotfix2: "\t\t\tДата(1, 1, 1);\n\t\tКонецЕсли;"
old = (
    "\t\t\t\u0414\u0430\u0442\u0430\u0421\u0440\u0435\u0437\u0430 = \u0414\u0430\u0442\u0430(1, 1, 1);\n"
    "\t\t\u041a\u043e\u043d\u0435\u0446\u0415\u0441\u043b\u0438;"
)
new = (
    "\t\t\t\u0414\u0430\u0442\u0430\u0421\u0440\u0435\u0437\u0430 = \u0414\u0430\u0442\u0430(1, 1, 1);\n"
    "\t\t\u041a\u043e\u043d\u0435\u0446\u0415\u0441\u043b\u0438;\n"
    "\t\t\u0415\u0441\u043b\u0438 \u041d\u0415 \u0417\u043d\u0430\u0447\u0435\u043d\u0438\u0435\u0417\u0430\u043f\u043e\u043b\u043d\u0435\u043d\u043e(\u0414\u0430\u0442\u0430\u0421\u0440\u0435\u0437\u0430) \u0422\u043e\u0433\u0434\u0430\n"
    "\t\t\t// \u041c\u0410\u041a\u0421\u0418\u041c\u0423\u041c \u043f\u043e \u043f\u0443\u0441\u0442\u043e\u043c\u0443 \u043c\u043d\u043e\u0436\u0435\u0441\u0442\u0432\u0443 \u0434\u0430\u0451\u0442 \u0441\u0442\u0440\u043e\u043a\u0443 \u0441 NULL:\n"
    "\t\t\t// \u0421\u043b\u0435\u0434\u0443\u044e\u0449\u0438\u0439() = \u0418\u0441\u0442\u0438\u043d\u0430, \u043d\u043e \u0437\u043d\u0430\u0447\u0435\u043d\u0438\u0435 - NULL. \u041f\u0443\u043b \u0422\u0421\n"
    "\t\t\t// \u0432 \u044d\u0442\u043e\u043c \u0441\u043b\u0443\u0447\u0430\u0435 \u043f\u0443\u0441\u0442, \u0434\u0430\u0442\u0430 \u043d\u0430 \u0440\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442 \u043d\u0435 \u0432\u043b\u0438\u044f\u0435\u0442,\n"
    "\t\t\t// \u043d\u043e \u0442\u0438\u043f \u0414\u0430\u0442\u0430 \u043e\u0431\u044f\u0437\u0430\u0442\u0435\u043b\u0435\u043d \u0434\u043b\u044f \u0441\u0440\u0435\u0437\u0430.\n"
    "\t\t\t\u0414\u0430\u0442\u0430\u0421\u0440\u0435\u0437\u0430 = \u0414\u0430\u0442\u0430(1, 1, 1);\n"
    "\t\t\u041a\u043e\u043d\u0435\u0446\u0415\u0441\u043b\u0438;"
)
n = src.count(old)
if n != 1:
    print("FAIL anchor: found %d occurrences" % n)
    sys.exit(1)
src = src.replace(old, new)
with io.open(SERVER, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("OK: NULL-guard for ДатаСреза added")
