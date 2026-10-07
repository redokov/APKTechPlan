#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""COM probe: run ВыполнитьТесты, dump exact exception text (utf-8 file, no console mangling)."""
import sys
import traceback
import win32com.client

CONN = "Srvr='localhost';Ref='dev_erpapk_demo';Usr='Администратор (ОрловАВ)';Pwd='';"
OUT = r'C:\MyProjects\APKTechPlan\heartbeat\com_error.txt'

lines = []
connector = win32com.client.Dispatch("V85.COMConnector")
try:
    agent = connector.Connect(CONN)
    lines.append("connected")
    runner = agent.Обработки.Тх_РаннерТестов.Создать()
    lines.append("runner created: %r" % (runner,))
    results = runner.ВыполнитьТесты()
    lines.append("results count: %s" % (results.Count() if hasattr(results, 'Count') else len(results)))
    for i in range(results.Count()):
        item = results.Get(i)
        lines.append("%s | passed=%s | %s ms" % (item.Имя, item.Прошёл, item.ДлительностьМс))
except Exception as e:
    lines.append("EXCEPTION repr: %r" % (e,))
    # pywin32 com_error: (hr, scode, excepinfo, argerror); excepinfo[2] = description
    try:
        ei = e.args[2]
        for idx, part in enumerate(ei):
            lines.append("excepinfo[%d] = %r" % (idx, part))
    except Exception as e2:
        lines.append("excepinfo dump failed: %r" % (e2,))
    lines.append(traceback.format_exc())

with open(OUT, 'w', encoding='utf-8') as f:
    f.write("\n".join(str(x) for x in lines))
print("written to " + OUT)
