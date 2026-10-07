#!/usr/bin/env python3
"""B5 probe 2: call Tkh_TekhnikaServer.MoshchnostDvigatelyaModeli via COM
on a model created the same way the test does (Справочники[Имя].СоздатьЭлемент +
Наименование + Поля structure + Записать).

Output -> heartbeat/probe_power2.txt (utf-8).
"""
import traceback
import uuid as _u

import win32com.client

CONN_STRING = (
    "Srvr='localhost';Ref='dev_erpapk_demo';"
    "Usr='Администратор (ОрловАВ)';Pwd='';"
)
OUT = r"C:\MyProjects\APKTechPlan\heartbeat\probe_power2.txt"
lines = []

def out(s):
    lines.append(str(s))

def main():
    connector = win32com.client.Dispatch("V85.COMConnector")
    agent = connector.Connect(CONN_STRING)
    try:
        srv = getattr(agent, "Тх_ТехникаСервер")
        out("srv module resolved: %r" % (srv,))

        cat = getattr(agent.Справочники, "АпкМоделиСХТехники")
        obj = cat.СоздатьЭлемент()
        name = "Тх_проба2_" + _u.uuid4().hex[:8]
        obj.Наименование = name
        # replicate СоздатьЭлемент: iterate structure fields
        obj.МощностьДвигателя = 100
        obj.Записать()
        ref = obj.Ссылка
        out("model created via COM, ref ok: %r" % (ref is not None,))

        p = srv.МощностьДвигателяМодели(ref)
        out("srv.МощностьДвигателяМодели(ref) = %r" % (p,))

        # cleanup
        ref.ПолучитьОбъект().Удалить()
        out("cleanup OK")
    except Exception:
        out("EXCEPTION:\n" + traceback.format_exc())

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("probe done -> %s" % OUT)

if __name__ == "__main__":
    main()
