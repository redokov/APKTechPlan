#!/usr/bin/env python3
"""B5 probe: why MoshchnostDvigatelyaModeli returns 0 for a created model.

Creates an item in ApkModeliSKhTekhniki with MoshchnostDvigatelya=100,
then reads it back three ways:
  1. object attribute read-back after Write();
  2. re-read fresh object via GetObject();
  3. query "VYBRAT Spr.MoshchnostDvigatelya IZ Spravochnik.<name> GDE Sprr.Ssylka = &Model"
     (same text as Tkh_TekhnikaServer.MoshchnostDvigatelyaModeli).
Also prints attribute availability check: does the object have the attribute?
Output -> utf-8 file heartbeat/com_error.txt (console cyrillic is unreliable).
"""
import sys
import traceback

import win32com.client

CONN_STRING = (
    "Srvr='localhost';Ref='dev_erpapk_demo';"
    "Usr='Администратор (ОрловАВ)';Pwd='';"
)

OUT = r"C:\MyProjects\APKTechPlan\heartbeat\probe_power.txt"

lines = []

def out(s):
    lines.append(str(s))


def main():
    connector = win32com.client.Dispatch("V85.COMConnector")
    agent = connector.Connect(CONN_STRING)

    try:
        spc = getattr(agent, "Справочники")
        cat = spc.АпкМоделиСХТехники
        obj = cat.СоздатьЭлемент()
        import uuid as _u
        name = "Тх_проба_" + _u.uuid4().hex[:8]
        obj.Наименование = name
        out("created object, name set: %s" % name)

        # attribute write
        try:
            obj.МощностьДвигателя = 100
            out("obj.MoshchnostDvigatelya := 100 OK, read-back before write: %r" % obj.МощностьДвигателя)
        except Exception as e:
            out("obj.MoshchnostDvigatelya SET FAILED: %r" % (e,))

        obj.Записать()
        ref = obj.Ссылка
        out("write() OK, ref=%r" % (ref,))

        # 1. read back via fresh object
        obj2 = ref.ПолучитьОбъект()
        out("fresh object МощностьДвигателя: %r" % obj2.МощностьДвигателя)
        out("fresh object Наименование: %r" % obj2.Наименование)

        # 2. query exactly as МощностьДвигателяМодели
        q = agent.NewObject("Запрос")
        q.Текст = ("ВЫБРАТЬ Спр.МощностьДвигателя КАК МощностьДвигателя "
                   "ИЗ Справочник.АпкМоделиСХТехники КАК Спр "
                   "ГДЕ Спр.Ссылка = &Модель")
        q.УстановитьПараметр("Модель", ref)
        res = q.Выполнить()
        sel = res.Выбрать()
        cnt = 0
        while sel.Следующий():
            cnt += 1
            out("query row %d: МощностьДвигателя=%r" % (cnt, sel.МощностьДвигателя))
        out("query rows: %d" % cnt)

        # 3. type-name function check (as ИмяСправочникаПоТипуСсылки)
        out("ТипЗнч(ref) string: %r" % str(agent.XMLString(agent.NewObject("МоментВремени"))) if False else None)
        t = agent.NewObject("ОписаниеТипов")
        out("skip typedesc")

        # cleanup
        obj2.Удалить()
        out("cleanup OK")
    except Exception:
        out("EXCEPTION:\n" + traceback.format_exc())

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("probe done -> %s" % OUT)


if __name__ == "__main__":
    main()
