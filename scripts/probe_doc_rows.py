#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read back document Тх_ПланТехническихРесурсов (ТХТЕСТ-001) rows via COM.

Used to diagnose Vanessa assertions: shows what is actually stored in the
tab sections (ТранспортноеСредство / МодельТехники / Принят / Количество) and
what the form-side computed column «ХозНомер» resolves to.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import win32com.client as com  # noqa: F401
except ImportError:
    print("pywin32 is required")
    sys.exit(2)

CONN_STR = ('Srvr="localhost";Ref="dev_erpapk_demo";'
            'Usr="\u0410\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0430\u0442\u043e\u0440 (\u041e\u0440\u043b\u043e\u0432\u0410\u0412)";Pwd="";')


def main():
    conn = com.Dispatch("V85.COMConnector").Connect(CONN_STR)
    q = conn.NewObject("Query")
    q.Text = (
        'ВЫБРАТЬ ПЕРВЫЕ 10\n'
        '\tД.Ссылка КАК Док, Д.Номер КАК Номер, Д.Проведен КАК Проведен\n'
        'ИЗ Документ.Тх_ПланТехническихРесурсов КАК Д\n'
        'УПОРЯДОЧИТЬ ПО Д.Номер'
    )
    res = q.Execute().Unload()
    print("документов: %d" % res.Count())
    for r in res:
        print("  %s  %s  проведен=%s" % (r.Док, r.Номер, r.Проведен))

    q2 = conn.NewObject("Query")
    q2.Text = (
        'ВЫБРАТЬ\n'
        '\tТ.НомерСтроки КАК Н, Т.ТранспортноеСредство.Наименование КАК ТС,\n'
        '\tТ.МодельТехники.Наименование КАК Модель, Т.Принят КАК Принят, Т.Количество КАК Кол\n'
        'ИЗ Документ.Тх_ПланТехническихРесурсов.ОсновнаяТехника КАК Т\n'
        'ГДЕ Т.Ссылка.Номер = "ТХТЕСТ-001"\n'
        'УПОРЯДОЧИТЬ ПО Т.НомерСтроки'
    )
    rows = q2.Execute().Unload()
    print("\nОсновнаяТехника для ТХТЕСТ-001: строк %d" % rows.Count())
    for r in rows:
        print("  #%d ТС=%s | Модель=%s | Принят=%s | Кол=%s"
              % (r.Н, r.ТС, r.Модель, r.Принят, r.Кол))

    # computed ХозНомер lives on the catalog, not in the document
    q3 = conn.NewObject("Query")
    q3.Text = (
        'ВЫБРАТЬ ПЕРВЫЕ 5\n'
        '\tТС.Наименование КАК Имя, ТС.АпкХозНомер КАК ХозНомер\n'
        'ИЗ Справочник.ТранспортныеСредства КАК ТС\n'
        'ГДЕ ТС.Наименование ПОДОБНО "%Тх_Тест ТС%"\n'
        'УПОРЯДОЧИТЬ ПО ТС.Наименование'
    )
    c = q3.Execute().Unload()
    print("\nсправочник ТранспортныеСредства (Тх_Тест ТС*):")
    for r in c:
        print("  %s | АпкХозНомер=%s" % (r.Имя, r.ХозНомер))
    return 0


if __name__ == "__main__":
    sys.exit(main())
