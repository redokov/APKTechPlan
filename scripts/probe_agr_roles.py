#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Probe: Агроном effective roles/panels - why Планирование техники visible without Тх_-roles."""
import sys
import win32com.client

conn = win32com.client.Dispatch("V85.COMConnector").Connect(
    "Srvr='localhost';Ref='dev_erpapk_demo';Usr='Администратор (ОрловАВ)';Pwd='';")

def out(s):
    sys.stdout.buffer.write((s + "\n").encode("utf-8"))

users = conn.ПользователиИнформационнойБазы
user = None
for i in range(users.Количество()):
    u = users.Получить(i)
    if u.Имя == "Агроном":
        user = u
        break

out("user: %s" % user.Имя)
roles = user.Роли
out("direct roles:")
for i in range(roles.Количество()):
    out("  - %s" % roles.Получить(i).Имя)

# Профили групп доступа (БСП) - отдельные объекты
out("=== профили групп доступа пользователя ===")
try:
    q = conn.NewObject("Запрос")
    q.Текст = ("ВЫБРАТЬ ГС.Ссылка КАК Группа, ГС.Наименование КАК Имя "
               "ИЗ Справочник.ГруппыДоступа КАК ГС "
               "ГДЕ ГС.Пользователи.Пользователь = &П")
    # найти справочник пользователей БСП
    q2 = conn.NewObject("Запрос")
    q2.Текст = ("ВЫБРАТЬ ПЕРВЫЕ 3 Спр.Ссылка ИЗ Справочник.Пользователи КАК Спр ГДЕ Спр.Наименование ПОДОБНО \"Агроном%\"")
    s = q2.Выполнить().Выбрать()
    if s.Следующий():
        q.УстановитьПараметр("П", s.Ссылка)
        r = q.Выполнить().Выбрать()
        while r.Следующий():
            out("  группа доступа: %s" % r.Имя)
    else:
        out("  (пользователь БСП «Агроном» не найден)")
except Exception as e:
    out("  ERR: %s" % str(e)[:150])
