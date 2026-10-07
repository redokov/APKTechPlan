#!/usr/bin/env python3
"""B6 preflight: probe demo data needed for Vanessa feature scenarios.

Read-only COM queries; results to heartbeat/b6_probe.txt (utf-8).
"""
import io
import sys

import win32com.client

OUT = io.open("heartbeat/b6_probe.txt", "w", encoding="utf-8")

CONN_STRING = (
    "Srvr='localhost';Ref='dev_erpapk_demo';"
    "Usr='Администратор (ОрловАВ)';Pwd='';"
)


def w(s):
    OUT.write(s + "\n")


def q(agent, text, params=None, limit=5):
    try:
        qobj = agent.NewObject("Query")
        qobj.Text = text
        if params:
            for k, v in params.items():
                qobj.SetParameter(k, v)
        sel = qobj.Execute().Choose()
        rows = []
        while sel.Next() and len(rows) < limit:
            rows.append(sel)
        return rows
    except Exception as e:
        w("  [ERR] %r" % (e,))
        return []


def probe_catalog(agent, name, extra=""):
    w("\n=== Справочник.%s ===" % name)
    text = (
        "ВЫБРАТЬ ПЕРВЫЕ 5 Спр.Ссылка КАК Ссылка"
        + (", " + extra if extra else "")
        + " ИЗ Справочник." + name + " КАК Спр ГДЕ НЕ Спр.ПометкаУдаления"
    )
    rows = q(agent, text)
    w("  count sample: %d (limit 5)" % len(rows))
    for r in rows:
        try:
            descr = r.Ссылка.Description
        except Exception:
            descr = "?"
        extra_str = ""
        if extra:
            parts = [p.strip().split(" КАК ")[1] for p in extra.split(",")]
            extra_str = " | " + ", ".join(
                "%s=%s" % (p, getattr(r, p)) for p in parts
            )
        w("  %s%s" % (descr, extra_str))


def probe_register_meta(agent, name):
    w("\n=== РегистрНакопления.%s (metadata) ===" % name)
    try:
        regs = agent.РегистрыНакопления
        reg = regs[name]
        w("  ВидРегистра: %s" % reg.ВидРегистра)
        dims = reg.Измерения
        names = []
        for i in range(dims.Количество()):
            d = dims.Получить(i)
            names.append(d.Имя)
        w("  Измерения: %s" % ", ".join(names))
        res = reg.Ресурсы
        rnames = []
        for i in range(res.Количество()):
            r = res.Получить(i)
            rnames.append(r.Имя)
        w("  Ресурсы: %s" % ", ".join(rnames))
    except Exception as e:
        w("  [ERR meta] %r" % (e,))


def probe_register_count(agent, name):
    w("\n=== %s: record count (virtual table turnover) ===" % name)
    text = "ВЫБРАТЬ КОЛИЧЕСТВО(*) КАК N ИЗ %s.%s" % ("РегистрНакопления", name + "Обороты")
    rows = q(agent, text, limit=1)
    for r in rows:
        w("  turnover rows: %s" % r.N)


def main():
    connector = win32com.client.Dispatch("V85.COMConnector")
    agent = connector.Connect(CONN_STRING)
    w("connected")

    probe_catalog(agent, "АпкСценарииПланирования")
    probe_catalog(agent, "Организации")
    probe_catalog(agent, "СтруктураПредприятия")
    probe_catalog(agent, "ВидыРаботСотрудников")
    probe_catalog(agent, "АпкМоделиСХТехники", "Спр.МощностьДвигателя КАК Мощность")
    probe_catalog(agent, "ТранспортныеСредства",
                  "Спр.Код КАК Код, Спр.АпкМодель КАК АпкМодель, Спр.АпкХозНомер КАК АпкХозНомер")

    for rn in ("АпкМеханизированныеРаботыПоГодовомуПлану",
               "АпкТранспортныеРаботыПоГодовомуПлану"):
        probe_register_meta(agent, rn)
        probe_register_count(agent, rn)

    # our own register state (leftovers from unit tests)
    w("\n=== РегистрСведений.Тх_ДефицитТехники: record count ===")
    rows = q(agent, "ВЫБРАТЬ КОЛИЧЕСТВО(*) КАК N ИЗ РегистрСведений.Тх_ДефицитТехники", limit=1)
    for r in rows:
        w("  rows: %s" % r.N)
    OUT.close()
    print("done -> heartbeat/b6_probe.txt")


if __name__ == "__main__":
    main()
