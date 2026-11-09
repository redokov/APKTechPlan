#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VA suite preflight/residue probe (spec-003 safe lane, E2E phase).

Read-only COM queries against the target test IB (dev_erpapk_demo):
  mode "ib"      - connectivity check only (exit 0 = IB available)
  mode "full"    - full marker/fixture snapshot (JSON to stdout)

Marker contract (from tests/vanessa features):
  - 01/02 create + IN-SCENARIO-delete models/trailers named "Тх_VA ..." -> 0 after run
  - 03 leaves exactly 1 doc Тх_ПланТехническихРесурсов Комментарий "Тх_Тест" (ТХТЕСТ-001)
  - 04 leaves exactly 2 docs Комментарий "Тх_Тест4*" (ТХТЕСТ4-А/Б)
  - 07 leaves exactly 1 doc Комментарий "Тх_VA_07Доступность"
  - 08 leaves exactly 1 doc Комментарий "Тх_VA_ПланРабот" and DELETES posted
    demo АпкПланТехническихРесурсов (НИВА/Основной) as its designed precondition
  - stable prep fixtures (va_prep_data.py): "Тх_Тест Базовая/Аналог/БезМощности",
    ТС "Тх_Тест ТС 001..004" + codes ТХТС*, "Тх_Тест Подразделение 1/2",
    work "Тх_Тест Работа"

Read-only: no object is created, written or deleted by this probe.
"""
import json
import sys

import win32com.client

CONN_STRING = (
    "Srvr='localhost';Ref='dev_erpapk_demo';"
    "Usr='Администратор (ОрловАВ)';Pwd='';"
)

QUERIES = [
    ("models_va", u"ВЫБРАТЬ КОЛИЧЕСТВО(*) КАК CNT ИЗ Справочник.АпкМоделиСХТехники ГДЕ Наименование ПОДОБНО &P",
     u"%Тх_VA%"),
    ("trailers_va", u"ВЫБРАТЬ КОЛИЧЕСТВО(*) КАК CNT ИЗ Справочник.АпкМоделиПрицепов ГДЕ Наименование ПОДОБНО &P",
     u"%Тх_VA%"),
    ("txplan_va_any", u"ВЫБРАТЬ КОЛИЧЕСТВО(*) КАК CNT ИЗ Документ.Тх_ПланТехническихРесурсов ГДЕ Комментарий ПОДОБНО &P",
     u"Тх_VA%"),
    ("txplan_va_07", u"ВЫБРАТЬ КОЛИЧЕСТВО(*) КАК CNT ИЗ Документ.Тх_ПланТехническихРесурсов ГДЕ Комментарий ПОДОБНО &P",
     u"Тх_VA_07Доступность"),
    ("txplan_va_08", u"ВЫБРАТЬ КОЛИЧЕСТВО(*) КАК CNT ИЗ Документ.Тх_ПланТехническихРесурсов ГДЕ Комментарий ПОДОБНО &P",
     u"Тх_VA_ПланРабот"),
    ("txplan_test4", u"ВЫБРАТЬ КОЛИЧЕСТВО(*) КАК CNT ИЗ Документ.Тх_ПланТехническихРесурсов ГДЕ Комментарий ПОДОБНО &P",
     u"Тх_Тест4%"),
    ("txplan_test_exact", u"ВЫБРАТЬ КОЛИЧЕСТВО(*) КАК CNT ИЗ Документ.Тх_ПланТехническихРесурсов ГДЕ Комментарий ПОДОБНО &P",
     u"Тх_Тест"),
    ("txplan_test_any", u"ВЫБРАТЬ КОЛИЧЕСТВО(*) КАК CNT ИЗ Документ.Тх_ПланТехническихРесурсов ГДЕ Комментарий ПОДОБНО &P",
     u"Тх_Тест%"),
    ("apkplan_posted_niva_osn", u"ВЫБРАТЬ КОЛИЧЕСТВО(*) КАК CNT ИЗ Документ.АпкПланТехническихРесурсов ГДЕ Проведен И Организация = &Орг И СценарийПланирования = &Сцен",
     None),
    ("deficit_rows_total", u"ВЫБРАТЬ КОЛИЧЕСТВО(*) КАК CNT ИЗ РегистрСведений.Тх_ДефицитТехники", None),
    ("deficit_rows_niva", u"ВЫБРАТЬ КОЛИЧЕСТВО(*) КАК CNT ИЗ РегистрСведений.Тх_ДефицитТехники ГДЕ Организация = &Орг И Подразделение = &Подр И СценарийПланирования = &Сцен", None),
    ("deficit_nofactor_niva", u"ВЫБРАТЬ КОЛИЧЕСТВО(*) КАК CNT ИЗ РегистрСведений.Тх_ДефицитТехники ГДЕ Организация = &Орг И Подразделение = &Подр И СценарийПланирования = &Сцен И КоэффициентНеЗадан", None),
    ("ts_test", u"ВЫБРАТЬ КОЛИЧЕСТВО(*) КАК CNT ИЗ Справочник.ТранспортныеСредства ГДЕ Наименование ПОДОБНО &P",
     u"Тх_Тест ТС%"),
    ("ts_thxtc_codes", u"ВЫБРАТЬ КОЛИЧЕСТВО(*) КАК CNT ИЗ Справочник.ТранспортныеСредства ГДЕ Код ПОДОБНО &P",
     u"ТХТС%"),
    ("models_test", u"ВЫБРАТЬ КОЛИЧЕСТВО(*) КАК CNT ИЗ Справочник.АпкМоделиСХТехники ГДЕ Наименование ПОДОБНО &P",
     u"Тх_Тест%"),
    ("subdiv_test", u"ВЫБРАТЬ КОЛИЧЕСТВО(*) КАК CNT ИЗ Справочник.СтруктураПредприятия ГДЕ Наименование ПОДОБНО &P",
     u"Тх_Тест Подразделение%"),
    ("work_test", u"ВЫБРАТЬ КОЛИЧЕСТВО(*) КАК CNT ИЗ Справочник.ВидыРаботСотрудников ГДЕ Наименование ПОДОБНО &P",
     u"Тх_Тест Работа%"),
]


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    agent = win32com.client.Dispatch("V85.COMConnector").Connect(CONN_STRING)
    print("[probe] connected to dev_erpapk_demo")
    if mode == "ib":
        return 0

    # reference values for org/subdivision/scenario (existing demo objects)
    refs = {
        u"Орг": agent.Справочники.Организации.НайтиПоНаименованию(u"НИВА"),
        u"Подр": agent.Справочники.СтруктураПредприятия.НайтиПоНаименованию(u"Отделение №2"),
        u"Сцен": agent.Справочники.АпкСценарииПланирования.НайтиПоНаименованию(u"Основной"),
    }

    out = {}
    for name, q, like in QUERIES:
        params = dict(refs) if "Орг" in q or "Подр" in q or "Сцен" in q else {}
        if like is not None:
            params[u"P"] = like
        query = agent.NewObject(u"Запрос")
        query.Text = q
        for k, v in params.items():
            query.SetParameter(k, v)
        sel = query.Execute().Choose()
        sel.Next()
        out[name] = int(sel.CNT)
    print(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
