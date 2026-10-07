#!/usr/bin/env python3
"""B5 probe 5: prerequisites for ТестНеПринятыеТСИсключены fix.

- can we create ТранспортныеСредства with just Наименование?
- do Организации / СтруктураПредприятия have first elements?

Output -> heartbeat/probe_power5.txt (utf-8).
"""
import traceback
import uuid as _u

import win32com.client

CONN_STRING = (
    "Srvr='localhost';Ref='dev_erpapk_demo';"
    "Usr='Администратор (ОрловАВ)';Pwd='';"
)
OUT = r"C:\MyProjects\APKTechPlan\heartbeat\probe_power5.txt"
lines = []

def out(s):
    lines.append(str(s))

def first(agent, name):
    q = agent.NewObject("Запрос")
    q.Текст = ("ВЫБРАТЬ ПЕРВЫЕ 1 Спр.Ссылка КАК Ссылка ИЗ Справочник." + name
               + " КАК Спр ГДЕ НЕ Спр.ПометкаУдаления")
    sel = q.Выполнить().Выбрать()
    if sel.Следующий():
        return sel.Ссылка
    return None

def main():
    connector = win32com.client.Dispatch("V85.COMConnector")
    agent = connector.Connect(CONN_STRING)
    try:
        out("Организации first: %r" % (first(agent, "Организации"),))
        out("СтруктураПредприятия first: %r" % (first(agent, "СтруктураПредприятия"),))

        cat = getattr(agent.Справочники, "ТранспортныеСредства")
        refs = []
        for i in range(2):
            obj = cat.СоздатьЭлемент()
            obj.Наименование = "Тх_проба5_" + _u.uuid4().hex[:8]
            obj.Код = "ТХПР" + _u.uuid4().hex[:10].upper()
            obj.Записать()
            refs.append(obj.Ссылка)
        out("created 2 ТС OK")
        for r in refs:
            r.ПолучитьОбъект().Удалить()
        out("cleanup OK")
    except Exception:
        out("EXCEPTION:\n" + traceback.format_exc())

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("probe done -> %s" % OUT)

if __name__ == "__main__":
    main()
