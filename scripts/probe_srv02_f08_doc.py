#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Probe: metadata of Документ.АпкПланТехническихРесурсов (attributes, tabular sections, columns)."""
import sys
import win32com.client

conn = win32com.client.Dispatch("V85.COMConnector").Connect(
    "Srvr='localhost';Ref='dev_erpapk_demo';Usr='Администратор (ОрловАВ)';Pwd='';")

mddoc = None
for i in range(conn.Метаданные.Документы.Количество()):
    d = conn.Метаданные.Документы.Получить(i)
    if d.Имя == "АпкПланТехническихРесурсов":
        mddoc = d
        break
doc = mddoc

def out(s):
    sys.stdout.buffer.write((s + "\n").encode("utf-8"))

out("=== Recv props of АпкПланТехническихРесурсов ===")
for i in range(doc.Реквизиты.Количество()):
    r = doc.Реквизиты.Получить(i)
    out("attr: %s" % r.Имя)

out("=== Standard props ===")
out("Проведен: yes (std); Комментарий: probe below")

# Test Комментарий via query
q = conn.NewObject("Запрос")
q.Текст = "ВЫБРАТЬ ПЕРВЫЕ 1 С.Ссылка, С.Комментарий ИЗ Документ.АпкПланТехническихРесурсов КАК С"
try:
    q.Выполнить()
    out("Комментарий in query: OK")
except Exception as e:
    out("Комментарий in query: FAIL: " + str(e)[:200])

out("=== Tabular sections ===")
for i in range(doc.ТабличныеЧасти.Количество()):
    t = doc.ТабличныеЧасти.Получить(i)
    out("tab: %s" % t.Имя)
    for j in range(t.Реквизиты.Количество()):
        c = t.Реквизиты.Получить(j)
        out("   col: %s" % c.Имя)

out("=== Probe query variants for Подразделение ===")
for fld in ["С.Подразделение", "С.ЭксплуатирующеПодразделение"]:
    q = conn.NewObject("Запрос")
    q.Текст = "ВЫБРАТЬ ПЕРВЫЕ 1 С.Ссылка ИЗ Документ.АпкПланТехническихРесурсов КАК С ГДЕ " + fld + " = &П"
    q.УстановитьПараметр("П", conn.Справочники.СтруктураПредприятия.ПустаяСсылка())
    try:
        q.Выполнить()
        out(fld + ": OK")
    except Exception as e:
        out(fld + ": FAIL: " + str(e)[:200])

# tabular join probe
q = conn.NewObject("Запрос")
q.Текст = ("ВЫБРАТЬ ПЕРВЫЕ 1 С.Ссылка ИЗ Документ.АпкПланТехническихРесурсов.Подразделения КАК С "
           "ГДЕ С.Подразделение = &П")
q.УстановитьПараметр("П", conn.Справочники.СтруктураПредприятия.ПустаяСсылка())
try:
    q.Выполнить()
    out("tab Подразделения.Подразделение: OK")
except Exception as e:
    out("tab Подразделения.Подразделение: FAIL: " + str(e)[:200])
