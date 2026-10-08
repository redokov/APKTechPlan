#!/usr/bin/env python3
"""B6: prepare stable-name test data for Vanessa feature scenarios (COM).

Creates (idempotent, find-or-create by name/code):
  - work  "Тх_Тест Работа"            (Catalog.ВидыРаботСотрудников)
  - model "Тх_Тест Базовая"  (power 100, АпкМоделиСХТехники)
  - model "Тх_Тест Аналог"   (power 125 -> K = 100/125 = 0.8)
  - model "Тх_Тест БезМощности" (no power -> autofill skips, names in message)
  - TS    "Тх_Тест ТС 001/002/003" (Catalog.ТранспортныеСредства,
    manual unique Code, АпкМодель=base model, АпкХозНомер filled)

Writes heartbeat/va_data.json with the values used by feature files.
"""
import io
import json
import sys

import win32com.client

OUT_PATH = "heartbeat/va_data.json"

CONN_STRING = (
    "Srvr='localhost';Ref='dev_erpapk_demo';"
    "Usr='Администратор (ОрловАВ)';Pwd='';"
)

WORK_NAME = "Тх_Тест Работа"
MODEL_BASE_NAME = "Тх_Тест Базовая"
MODEL_ANALOG_NAME = "Тх_Тест Аналог"
MODEL_NOMASS_NAME = "Тх_Тест БезМощности"
TS_ITEMS = [
    ("Тх_Тест ТС 001", "ТХТС00001", "ТХХ-00001"),
    ("Тх_Тест ТС 002", "ТХТС00002", "ТХХ-00002"),
    ("Тх_Тест ТС 003", "ТХТС00003", "ТХХ-00003"),
    ("Тх_Тест ТС 004", "ТХТС00004", "ТХХ-00004"),
]


def log(agent, s):
    print(s)

def find_by_name(agent, catalog, name):
    q = agent.NewObject("Query")
    q.Text = (
        "ВЫБРАТЬ ПЕРВЫЕ 1 Спр.Ссылка КАК Ссылка ИЗ Справочник." + catalog
        + " КАК Спр ГДЕ Спр.Наименование = &Имя И НЕ Спр.ПометкаУдаления"
    )
    q.SetParameter("Имя", name)
    sel = q.Execute().Choose()
    if sel.Next():
        return sel.Ссылка
    return None


def find_by_code(agent, catalog, code):
    q = agent.NewObject("Query")
    q.Text = (
        "ВЫБРАТЬ ПЕРВЫЕ 1 Спр.Ссылка КАК Ссылка ИЗ Справочник." + catalog
        + " КАК Спр ГДЕ Спр.Код = &Код И НЕ Спр.ПометкаУдаления"
    )
    q.SetParameter("Код", code)
    sel = q.Execute().Choose()
    if sel.Next():
        return sel.Ссылка
    return None


def ensure_item(agent, catalog, finder, key, name, fields=None):
    ref = finder(agent, catalog, key)
    created = False
    if ref is None:
        obj = getattr(agent.Справочники, catalog).СоздатьЭлемент()
        obj.Наименование = name
        for k, v in (fields or {}).items():
            setattr(obj, k, v)
        obj.Записать()
        ref = obj.Ссылка
        created = True
    return ref, created


def main():
    c = win32com.client.Dispatch("V85.COMConnector")
    agent = c.Connect(CONN_STRING)

    report = {"created": [], "existing": []}

    work, cr = ensure_item(agent, "ВидыРаботСотрудников",
                           find_by_name, WORK_NAME, WORK_NAME)
    report["created" if cr else "existing"].append("Работа " + WORK_NAME)

    models = {}
    for name, power in ((MODEL_BASE_NAME, 100),
                        (MODEL_ANALOG_NAME, 125),
                        (MODEL_NOMASS_NAME, None)):
        fields = {}
        if power is not None:
            fields["МощностьДвигателя"] = power
        ref, cr = ensure_item(agent, "АпкМоделиСХТехники",
                              find_by_name, name, name, fields)
        models[name] = str(ref)
        report["created" if cr else "existing"].append("Модель " + name)

    ts_refs = []
    base_ref = None
    q = agent.NewObject("Query")
    q.Text = ("ВЫБРАТЬ ПЕРВЫЕ 1 Спр.Ссылка КАК Ссылка ИЗ Справочник."
              "АпкМоделиСХТехники КАК Спр ГДЕ Спр.Наименование = &Имя")
    q.SetParameter("Имя", MODEL_BASE_NAME)
    sel = q.Execute().Choose()
    if sel.Next():
        base_ref = sel.Ссылка

    for name, code, hoz in TS_ITEMS:
        ref, cr = ensure_item(
            agent, "ТранспортныеСредства", find_by_code, code, name,
            {"Код": code, "АпкМодель": base_ref, "АпкХозНомер": hoz},
        )
        ts_refs.append(str(ref))
        report["created" if cr else "existing"].append("ТС " + code)

    data = {
        "work": WORK_NAME,
        "model_base": MODEL_BASE_NAME,
        "model_analog": MODEL_ANALOG_NAME,
        "model_nomass": MODEL_NOMASS_NAME,
        "ts": [t[0] for t in TS_ITEMS],
        "ts_codes": [t[1] for t in TS_ITEMS],
        "ts_hoz": [t[2] for t in TS_ITEMS],
    }
    with io.open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    for line in report["created"]:
        print("[create] " + line)
    for line in report["existing"]:
        print("[exists] " + line)
    print("data -> " + OUT_PATH)
    return 0


if __name__ == "__main__":
    sys.exit(main())
