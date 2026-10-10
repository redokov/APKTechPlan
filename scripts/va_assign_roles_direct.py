#!/usr/bin/env python3
"""B6: assign roles Тх_Чтение/Тх_Редактирование directly to the IB user
via ПользователиИнформационнойБазы (available from COM external connection
in 8.5). The БСП access-group path proved unreliable here (catalog user may
not be linked to this IB user), direct assignment is deterministic.

Usage: python scripts/va_assign_roles_direct.py <ИБ-имя-пользователя> [add|remove|list]
Default action: add (idempotent). Verifies by re-reading roles in a fresh
session.
"""
import sys

import win32com.client

CONN_STRING = (
    "Srvr='localhost';Ref='dev_erpapk_demo';"
    "Usr='Администратор (ОрловАВ)';Pwd='';"
)

ROLES = ["Тх_Чтение", "Тх_Редактирование"]


def find_ib_user(agent, name):
    return agent.ПользователиИнформационнойБазы.НайтиПоИмени(name)


def role_names(agent, user):
    # Roles collection exposes no enumeration via late binding,
    # use Содержит() membership checks instead (see b6_roles_probe.txt).
    roles = user.Роли
    names = []
    md = agent.Метаданные.Роли
    all_names = []
    try:
        cnt = md.Количество()
        for i in range(cnt):
            all_names.append(md.Получить(i).Имя)
    except Exception:
        all_names = ROLES + ["Администратор", "ПолныеПрава", "БазовыеПрава"]
    for rn in all_names:
        try:
            if roles.Содержит(getattr(md, rn)):
                names.append(rn)
        except Exception:
            pass
    return names


def contains_role(agent, user, role_obj):
    return user.Роли.Содержит(role_obj)


def main():
    name = sys.argv[1]
    action = sys.argv[2] if len(sys.argv) > 2 else "add"
    # argv[3] (optional): comma-separated role list (T12: stage-wise
    # assignment, e.g. only Тх_Чтение). Default: both Тх_-roles.
    roles = sys.argv[3].split(",") if len(sys.argv) > 3 else list(ROLES)

    c = win32com.client.Dispatch("V85.COMConnector")
    agent = c.Connect(CONN_STRING)
    print("[com] connected")

    user = find_ib_user(agent, name)
    if user is None:
        print("[fail] IB user not found: " + name)
        return 2
    print("[user] found: " + name)

    if action == "list":
        print("[roles] " + ", ".join(role_names(agent, user)))
        return 0

    # metadata role objects
    md_roles = {}
    md = agent.Метаданные.Роли
    for role_name in roles:
        role_obj = getattr(md, role_name)
        if role_obj is None:
            print("[fail] metadata role missing: " + role_name)
            return 2
        md_roles[role_name] = role_obj

    # membership check via Содержит
    have = set()
    for role_name, role_obj in md_roles.items():
        if contains_role(agent, user, role_obj):
            have.add(role_name)
    print("[roles] Тх-roles before: " + (", ".join(sorted(have)) or "none"))

    user = user.ПолучитьОбъект() if hasattr(user, "ПолучитьОбъект") else user
    # ИнформационныйБаза user object: user itself is writable via Записать()
    changed = False
    if action == "add":
        for role_name, role_obj in md_roles.items():
            if role_name not in have:
                user.Роли.Добавить(role_obj)
                changed = True
                print("[add] " + role_name)
    elif action == "remove":
        for role_name, role_obj in md_roles.items():
            if role_name in have:
                user.Роли.Удалить(role_obj)
                changed = True
                print("[remove] " + role_name)
    if changed:
        user.Записать()
        print("[write] saved")
    else:
        print("[write] nothing to change")

    # verify in a fresh session
    agent2 = c.Connect(CONN_STRING)
    user2 = find_ib_user(agent2, name)
    have2 = set()
    md2 = agent2.Метаданные.Роли
    for role_name in roles:
        try:
            if user2.Роли.Содержит(getattr(md2, role_name)):
                have2.add(role_name)
        except Exception:
            pass
    print("[verify] Тх-roles now: " + (", ".join(sorted(have2)) or "none"))
    if action == "add":
        ok = all(r in have2 for r in roles)
    else:
        ok = not any(r in have2 for r in roles)
    print("[verify] " + ("OK" if ok else "FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
