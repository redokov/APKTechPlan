#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Probe: СрезПоследних(&Д) parameter type behavior on live IB."""
import win32com.client

conn = win32com.client.Dispatch("V85.COMConnector").Connect(
    "Srvr='localhost';Ref='dev_erpapk_demo';Usr='Администратор (ОрловАВ)';Pwd='';")

QT = ("ВЫБРАТЬ ПЕРВЫЕ 1 Т.Организация "
      "ИЗ РегистрСведений.АпкИсторияТранспортныхСредств.СрезПоследних(&Д) КАК Т")

def get_qdate(y, m, d):
    q = conn.NewObject("Запрос")
    q.Текст = "ВЫБРАТЬ ДАТАВРЕМЯ(%d, %d, %d) КАК Д" % (y, m, d)
    v = q.Выполнить().Выбрать()
    v.Следующий()
    return v.Д

def probe(val, label):
    q = conn.NewObject("Запрос")
    q.Текст = QT
    q.УстановитьПараметр("Д", val)
    try:
        q.Выполнить()
        print(label, "OK")
    except Exception as e:
        print(label, "FAIL:", str(e)[:170])

probe(get_qdate(1, 1, 1), "q-date(1,1,1):")
probe(get_qdate(2026, 1, 1), "q-date(2026,1,1):")
probe(None, "None(=>NULL):")
probe("20261101", "string:")
