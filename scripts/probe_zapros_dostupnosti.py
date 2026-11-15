#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Probe: call Тх_ТехникаСервер.ЗапросДоступности directly (no ДатаСреза)
with a scenario that has no posted plans -> expect empty result, NO exception
if hotfix3 is applied in the IB; NULL-type error if module is stale."""
import win32com.client

conn = win32com.client.Dispatch("V85.COMConnector").Connect(
    "Srvr='localhost';Ref='dev_erpapk_demo';Usr='Администратор (ОрловАВ)';Pwd='';")

# find any scenario element
# create a FRESH scenario (no plans) - exercises the NULL fallback branch
mgr = conn.Справочники.АпкСценарииПланирования
obj = mgr.СоздатьЭлемент()
obj.Наименование = "probe_zd_null"
obj.Записать()
scn = obj.Ссылка
obj2 = mgr.СоздатьЭлемент()  # will be deleted below
print("fresh scenario created")

srv = conn.Тх_ТехникаСервер
params = conn.NewObject("Структура")
params.Вставить("СценарийПланирования", scn)
try:
    res = srv.ЗапросДоступности(params)
    n = res.Количество() if hasattr(res, "Количество") else -1
    print("OK, rows:", n)
except Exception as e:
    print("EXCEPTION:", str(e)[:400])
finally:
    try:
        obj.ОбменДанными.Загрузка = True
        obj.Удалить()
    except Exception:
        pass
