#!/usr/bin/env python3
"""B5 probe 4: call temporary debug export Tkh_OtladkaTip on a live model.

Output -> heartbeat/probe_power4.txt (utf-8).
"""
import traceback
import uuid as _u

import win32com.client

CONN_STRING = (
    "Srvr='localhost';Ref='dev_erpapk_demo';"
    "Usr='Администратор (ОрловАВ)';Pwd='';"
)
OUT = r"C:\MyProjects\APKTechPlan\heartbeat\probe_power4.txt"
lines = []

def out(s):
    lines.append(str(s))

def main():
    connector = win32com.client.Dispatch("V85.COMConnector")
    agent = connector.Connect(CONN_STRING)
    try:
        srv = getattr(agent, "Тх_ТехникаСервер")
        cat = getattr(agent.Справочники, "АпкМоделиСХТехники")
        obj = cat.СоздатьЭлемент()
        obj.Наименование = "Тх_проба4_" + _u.uuid4().hex[:8]
        obj.МощностьДвигателя = 100
        obj.Записать()
        ref = obj.Ссылка

        st = srv.Тх_ОтладкаТип(ref)
        out("ТипСтрокой: %r" % (st.ТипСтрокой,))
        out("Заполнено: %r" % (st.Заполнено,))
        out("ИмяСправочника: %r" % (st.ИмяСправочника,))
        out("srv.МощностьДвигателяМодели(ref) = %r" % (srv.МощностьДвигателяМодели(ref),))

        ref.ПолучитьОбъект().Удалить()
        out("cleanup OK")
    except Exception:
        out("EXCEPTION:\n" + traceback.format_exc())

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("probe done -> %s" % OUT)

if __name__ == "__main__":
    main()
