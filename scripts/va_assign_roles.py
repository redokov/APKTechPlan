#!/usr/bin/env python3
"""B6/B8: assign roles Тх_Чтение+Тх_Редактирование to the IB user via БСП.

Path: Catalog.ПрофилиГруппДоступа (ТЧ Роли) -> Catalog.ГруппыДоступа
(Профиль + ТЧ Пользователи). On group write, the БСП object module calls
УправлениеДоступом.ОбновитьРолиПользователей() which rewrites the IB user's
role set. This is the ERP-standard way to grant our extension roles.

Idempotent: finds profile/group by name, creates if missing.
After running, verifies РолиДоступны("Тх_Чтение") in a FRESH COM session.
"""
import sys

import win32com.client

CONN_STRING = (
    "Srvr='localhost';Ref='dev_erpapk_demo';"
    "Usr='Администратор (ОрловАВ)';Pwd='';"
)

PROFILE_NAME = "Тх_ Планирование техники (тест)"
GROUP_NAME = "Тх_ Планирование техники (тест)"
USER_NAME_LIKE = "Орлов Александр Владимирович"
ROLES = ["Тх_Чтение", "Тх_Редактирование"]


def find_first(agent, text, params=None):
    q = agent.NewObject("Query")
    q.Text = text
    for k, v in (params or {}).items():
        q.SetParameter(k, v)
    sel = q.Execute().Choose()
    if sel.Next():
        return sel
    return None


def main():
    c = win32com.client.Dispatch("V85.COMConnector")
    agent = c.Connect(CONN_STRING)
    print("[com] connected")

    # 1. catalog user for the IB admin
    row = find_first(
        agent,
        "ВЫБРАТЬ ПЕРВЫЕ 1 Спр.Ссылка КАК Ссылка, Спр.Наименование КАК Имя "
        "ИЗ Справочник.Пользователи КАК Спр "
        "ГДЕ Спр.Наименование ПОДОБНО &Шаблон И НЕ Спр.ПометкаУдаления",
        {"Шаблон": USER_NAME_LIKE},
    )
    if row is None:
        print("[fail] catalog user not found for " + USER_NAME_LIKE)
        return 2
    user_ref = row.Ссылка
    print("[user] " + str(row.Имя))

    # 2. profile: find or create
    row = find_first(
        agent,
        "ВЫБРАТЬ ПЕРВЫЕ 1 Спр.Ссылка КАК Ссылка "
        "ИЗ Справочник.ПрофилиГруппДоступа КАК Спр "
        "ГДЕ Спр.Наименование = &Имя И НЕ Спр.ПометкаУдаления",
        {"Имя": PROFILE_NAME},
    )
    if row is not None:
        profile_ref = row.Ссылка
        print("[profile] exists")
    else:
        obj = agent.Справочники.ПрофилиГруппДоступа.СоздатьЭлемент()
        obj.Наименование = PROFILE_NAME
        for role in ROLES:
            line = obj.Роли.Добавить()
            line.Роль = role
        obj.Записать()
        profile_ref = obj.Ссылка
        print("[profile] created with roles: " + ", ".join(ROLES))

    # 3. group: find or create with the user inside
    row = find_first(
        agent,
        "ВЫБРАТЬ ПЕРВЫЕ 1 Г.Ссылка КАК Ссылка "
        "ИЗ Справочник.ГруппыДоступа КАК Г "
        "ГДЕ Г.Наименование = &Имя И НЕ Г.ПометкаУдаления",
        {"Имя": GROUP_NAME},
    )
    if row is not None:
        group_ref = row.Ссылка
        # ensure the user is in the group
        inner = find_first(
            agent,
            "ВЫБРАТЬ ПЕРВЫЕ 1 1 КАК Есть "
            "ИЗ Справочник.ГруппыДоступа.Пользователи КАК ГП "
            "ГДЕ ГП.Ссылка = &Группа И ГП.Пользователь = &Пользователь",
            {"Группа": group_ref, "Пользователь": user_ref},
        )
        if inner is not None:
            print("[group] exists, user already in")
        else:
            gobj = group_ref.ПолучитьОбъект()
            line = gobj.Пользователи.Добавить()
            line.Пользователь = user_ref
            gobj.Записать()
            print("[group] user added to existing group")
    else:
        gobj = agent.Справочники.ГруппыДоступа.СоздатьЭлемент()
        gobj.Наименование = GROUP_NAME
        gobj.Профиль = profile_ref
        line = gobj.Пользователи.Добавить()
        line.Пользователь = user_ref
        gobj.Записать()
        print("[group] created, user added (roles recalculated on write)")

    # 4. verify in a FRESH session (role set is cached per session)
    agent2 = c.Connect(CONN_STRING)
    try:
        ok_read = agent2.РолиДоступны("Тх_Чтение")
        ok_edit = agent2.РолиДоступны("Тх_Редактирование")
        print("[verify] РолиДоступны(Тх_Чтение)=%s, (Тх_Редактирование)=%s"
              % (ok_read, ok_edit))
        return 0 if (ok_read and ok_edit) else 1
    except Exception as e:
        print("[verify] call failed: %r" % (e,))
        return 1


if __name__ == "__main__":
    sys.exit(main())
