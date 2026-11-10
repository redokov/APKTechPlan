#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEC-02 read-only inventory: Документ.АпкПланТехническихРесурсов (main config).

Lists реквизиты + табличные части (with attribute types) of the approved
availability document, plus Принят usage. Read-only, dev_erpapk_demo.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import win32com.client

CONN = "Srvr='localhost';Ref='dev_erpapk_demo';Usr='Администратор (ОрловАВ)';Pwd='';"
agent = win32com.client.Dispatch("V85.COMConnector").Connect(CONN)
print("connected")

md = agent.Метаданные.Документы.АпкПланТехническихРесурсов
print("== Представление:", md.ПолноеИмя())
print("== Реквизиты:")
for r in md.Реквизиты:
    try:
        types = [str(x) for x in r.Тип.Типы()]
    except Exception:
        types = "?"
    print("  -", r.Имя, "|", types)

print("== Табличные части:")
for tc in md.ТабличныеЧасти:
    print("  ТЧ:", tc.Имя)
    for r in tc.Реквизиты:
        try:
            types = [str(x) for x in r.Тип.Типы()]
        except Exception:
            types = "?"
        print("    -", r.Имя, "|", types)

# sample data: last documents, show row shapes (no modifications)
q = agent.NewObject("Запрос")
q.Текст = "ВЫБРАТЬ ПЕРВЫЕ 2 Ссылка, Проведен ИЗ Документ.АпкПланТехническихРесурсов УПОРЯДОЧИТЬ ПО Дата УБЫВ"
sel = q.Выполнить().Выбрать()
refs = []
while sel.Следующий():
    refs.append(sel.Ссылка)
    print("== Образец:", sel.Ссылка, "| проведен:", sel.Проведен)
for ref in refs:
    for tc in md.ТабличныеЧасти:
        try:
            part = getattr(ref, tc.Имя)
            cnt = part.Количество()
        except Exception as e:
            print("   ТЧ", tc.Имя, "недоступна:", e)
            continue
        print("   ТЧ", tc.Имя, "строк:", cnt)
        if cnt:
            row = part.Получить(0)
            for a in tc.Реквизиты:
                v = getattr(row, a.Имя)
                try:
                    vmeta = v.Метаданные().ПолноеИмя()
                except Exception:
                    vmeta = v
                print("      ", a.Имя, "=", vmeta)
