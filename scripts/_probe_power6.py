#!/usr/bin/env python3
"""B5 probe 6: does a catalog REF have .Метаданные() in 8.5, or only the object?

Output -> heartbeat/probe_power6.txt (utf-8).
"""
import traceback
import uuid as _u

import win32com.client

CONN_STRING = (
    "Srvr='localhost';Ref='dev_erpapk_demo';"
    "Usr='Администратор (ОрловАВ)';Pwd='';"
)
OUT = r"C:\MyProjects\APKTechPlan\heartbeat\probe_power6.txt"
lines = []

def out(s):
    lines.append(str(s))

def main():
    connector = win32com.client.Dispatch("V85.COMConnector")
    agent = connector.Connect(CONN_STRING)
    try:
        cat = getattr(agent.Справочники, "АпкМоделиСХТехники")
        obj = cat.СоздатьЭлемент()
        obj.Наименование = "Тх_проба6_" + _u.uuid4().hex[:8]
        obj.МощностьДвигателя = 100
        obj.Записать()
        ref = obj.Ссылка

        out("obj.Метаданные().ПолноеИмя = %r"
            % (obj.Метаданные().ПолноеИмя(),))
        try:
            out("ref.Метаданные().ПолноеИмя() = %r"
                % (ref.Метаданные().ПолноеИмя(),))
        except Exception as e:
            out("ref.Метаданные().ПолноеИмя() FAILED: %r" % (e,))

        obj2 = ref.ПолучитьОбъект()
        out("fresh obj.Метаданные().ПолноеИмя() = %r"
            % (obj2.Метаданные().ПолноеИмя(),))
        out("srv.МощностьДвигателяМодели(ref) = %r"
            % (getattr(agent, "Тх_ТехникаСервер").МощностьДвигателяМодели(ref),))

        ref.ПолучитьОбъект().Удалить()
        out("cleanup OK")
    except Exception:
        out("EXCEPTION:\n" + traceback.format_exc())

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("probe done -> %s" % OUT)

if __name__ == "__main__":
    main()
