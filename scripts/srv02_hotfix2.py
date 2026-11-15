#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SRV-02 hotfix 2: ДатаСреза must always be a Date for
СрезПоследних(&ДатаСреза) in ЗапросДоступности.

When neither Параметры.ДатаСреза nor any posted plan doc of the scenario
exists, ДатаСреза stayed Неопределено -> query crash
"Несоответствие типов (Параметр номер 1)". In that case the pool of
physical ТС is empty anyway, so any valid Date is semantically neutral:
use Дата(1, 1, 1).
"""
import io
import sys

SERVER = "src/cfe/ПланированиеТехникиАПК/CommonModules/Тх_ТехникаСервер/Ext/Module.bsl"

with io.open(SERVER, "r", encoding="utf-8") as f:
    src = f.read()

# anchors (unicode escapes, no inline cyrillic in argv-sensitive contexts)
# Если ВыборкаДаты.Следующий() Тогда / ДатаСреза = ВыборкаДаты.ДатаСреза; / КонецЕсли;
old = (
    "\t\t\u0415\u0441\u043b\u0438 \u0412\u044b\u0431\u043e\u0440\u043a\u0430\u0414\u0430\u0442\u044b.\u0421\u043b\u0435\u0434\u0443\u044e\u0449\u0438\u0439() \u0422\u043e\u0433\u0434\u0430\n"
    "\t\t\t\u0414\u0430\u0442\u0430\u0421\u0440\u0435\u0437\u0430 = \u0412\u044b\u0431\u043e\u0440\u043a\u0430\u0414\u0430\u0442\u044b.\u0414\u0430\u0442\u0430\u0421\u0440\u0435\u0437\u0430;\n"
    "\t\t\u041a\u043e\u043d\u0435\u0446\u0415\u0441\u043b\u0438;"
)
new = (
    "\t\t\u0415\u0441\u043b\u0438 \u0412\u044b\u0431\u043e\u0440\u043a\u0430\u0414\u0430\u0442\u044b.\u0421\u043b\u0435\u0434\u0443\u044e\u0449\u0438\u0439() \u0422\u043e\u0433\u0434\u0430\n"
    "\t\t\t\u0414\u0430\u0442\u0430\u0421\u0440\u0435\u0437\u0430 = \u0412\u044b\u0431\u043e\u0440\u043a\u0430\u0414\u0430\u0442\u044b.\u0414\u0430\u0442\u0430\u0421\u0440\u0435\u0437\u0430;\n"
    "\t\t\u0418\u043d\u0430\u0447\u0435\n"
    "\t\t\t// \u043d\u0435\u0442 \u043d\u0438 \u043e\u0434\u043d\u043e\u0433\u043e \u043f\u0440\u043e\u0432\u0435\u0434\u0451\u043d\u043d\u043e\u0433\u043e \u043f\u043b\u0430\u043d\u0430 \u0441\u0446\u0435\u043d\u0430\u0440\u0438\u044f: \u043f\u0443\u043b \u0422\u0421 \u043f\u0443\u0441\u0442,\n"
    "\t\t\t// \u0434\u0430\u0442\u0430 \u0441\u0440\u0435\u0437\u0430 \u043d\u0435 \u0432\u043b\u0438\u044f\u0435\u0442 \u043d\u0430 \u0440\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442, \u043d\u043e \u0442\u0438\u043f \u0414\u0430\u0442\u0430\n"
    "\t\t\t// \u043e\u0431\u044f\u0437\u0430\u0442\u0435\u043b\u0435\u043d \u0434\u043b\u044f \u0421\u0440\u0435\u0437\u041f\u043e\u0441\u043b\u0435\u0434\u043d\u0438\u0445.\n"
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
print("OK: ДатаСреза fallback to Дата(1,1,1) added")
