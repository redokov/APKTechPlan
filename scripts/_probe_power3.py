#!/usr/bin/env python3
"""B5 probe 3 (rewrite): session language + applied-module type-name check.

1. ПРЕДСТАВЛЕНИЕ(ЗНАЧЕНИЕ(Перечисление.Тх_ВидыТехники.СХТехника)) - shows
   the session language (ru/en synonym of our enum).
2. ПРЕДСТАВЛЕНИЕ(ЗНАЧЕНИЕ(Справочник.XXX.ПустаяСсылка))? - not universal,
   skip. Instead: query main-config catalog presentation via ПРЕДСТАВЛЕНИЕ
   of a table field type is impossible without data; rely on #1 plus the
   behaviour of MoshchnostDvigatelyaModeli as evidence.

Output -> heartbeat/probe_power3.txt (utf-8).
"""
import traceback
import uuid as _u

import win32com.client

CONN_STRING = (
    "Srvr='localhost';Ref='dev_erpapk_demo';"
    "Usr='Администратор (ОрловАВ)';Pwd='';"
)
OUT = r"C:\MyProjects\APKTechPlan\heartbeat\probe_power3.txt"
lines = []

def out(s):
    lines.append(str(s))

def main():
    connector = win32com.client.Dispatch("V85.COMConnector")
    agent = connector.Connect(CONN_STRING)
    try:
        # 1. enum value presentation (session language)
        q = agent.NewObject("Запрос")
        q.Текст = "ВЫБРАТЬ ПРЕДСТАВЛЕНИЕ(ЗНАЧЕНИЕ(Перечисление.Тх_ВидыТехники.СХТехника)) КАК Пр"
        sel = q.Выполнить().Выбрать()
        while sel.Следующий():
            out("enum presentation (session lang): %r" % (sel.Пр,))

        # 2. representation of a main-config enum to double-check language
        try:
            q2 = agent.NewObject("Запрос")
            q2.Текст = ("ВЫБРАТЬ ПРЕДСТАВЛЕНИЕ(ЗНАЧЕНИЕ(Перечисление.Тх_ВидыТехники.Автотранспорт)) "
                        "КАК Пр")
            sel2 = q2.Выполнить().Выбрать()
            while sel2.Следующий():
                out("enum2 presentation: %r" % (sel2.Пр,))
        except Exception as e:
            out("enum2 query failed: %r" % (e,))

        # 3. ИмяСправочникаМоделей export sanity (static, language-independent)
        srv = getattr(agent, "Тх_ТехникаСервер")
        vid = getattr(getattr(agent, "Перечисления").Тх_ВидыТехники, "СХТехника")
        out("srv.ИмяСправочникаМоделей(СХТехника) = %r" % (srv.ИмяСправочникаМоделей(vid),))

        # 4. reproduce: create model with power, call МощностьДвигателяМодели
        cat = getattr(agent.Справочники, "АпкМоделиСХТехники")
        obj = cat.СоздатьЭлемент()
        obj.Наименование = "Тх_проба3_" + _u.uuid4().hex[:8]
        obj.МощностьДвигателя = 100
        obj.Записать()
        ref = obj.Ссылка
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
