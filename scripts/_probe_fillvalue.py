#!/usr/bin/env python3
"""Probe: does FillValue=true on TCh attribute 'Prinyat' apply on
SozdatDokument() + tabular row Dobavit()? (bare object, no form).
Also dumps metadata FillValue/FillFromFillingValue as seen by platform.
Output -> heartbeat/probe_fillvalue.txt (utf-8).
"""
import sys
import traceback

import win32com.client

CONN_STRING = (
    "Srvr='localhost';Ref='dev_erpapk_demo';"
    "Usr='Администратор (ОрловАВ)';Pwd='';"
)

OUT = r"C:\MyProjects\APKTechPlan\heartbeat\probe_fillvalue.txt"
lines = []


def out(s):
    lines.append(str(s))


def main():
    com = win32com.client.Dispatch("V85.COMConnector")
    con = com.Connect(CONN_STRING)
    out("connected")

    # 1. programmatic: bare object + new row
    try:
        doc = con.Документы.Тх_ПланТехническихРесурсов.СоздатьДокумент()
        row = doc.ОсновнаяТехника.Добавить()
        out("bare row Prinyat = %s" % row.Принят)
    except Exception:
        out("bare-row probe FAILED:")
        out(traceback.format_exc())

    # 2. metadata check: FillValue of the three Prinyat attributes
    try:
        md = con.Метаданные.Документы.Тх_ПланТехническихРесурсов
        for ts_name in ("ОсновнаяТехника", "Оборудование", "Автотранспорт"):
            ts = md.ТабличныеЧасти.Найти(ts_name)
            attr = ts.Реквизиты.Найти("Принят")
            for prop in ("ЗначениеЗаполнения", "ЗаполнятьИзДанныхЗаполнения", "ЗначениеЗаполненияПоУмолчанию"):
                try:
                    out("TCh %s: %s = %s" % (ts_name, prop, getattr(attr, prop)))
                except Exception:
                    out("TCh %s: prop %s not readable" % (ts_name, prop))
    except Exception:
        out("metadata probe FAILED:")
        out(traceback.format_exc())




if __name__ == "__main__":
    try:
        main()
    except Exception:
        lines.append("FATAL:")
        lines.append(traceback.format_exc())
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("written", OUT, len(lines), "lines")
