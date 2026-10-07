#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix misplaced locals in Тх_Тесты/Module.bsl:
move ИмяРегистраМехРабот/ИмяРегистраТранРабот assignments from НайтиПервыйЭлемент
(where they are unused) into СценарийСПотребностью (where they are used at line ~1555/1562).
CRLF + BOM safe.
"""
import io

PATH = r"src/cfe/ПланированиеТехникиАПК/CommonModules/Тх_Тесты/Ext/Module.bsl"

raw = open(PATH, "rb").read()
text = raw.decode("utf-8-sig")

moved_block = ("\t// Имена таблиц годового плана - динамические (runtime, design 4.1/TD-001).\r\n"
               "\tИмяРегистраМехРабот = \"АпкМеханизированныеРаботыПоГодовомуПлану\" + \"Обороты\";\r\n"
               "\tИмяРегистраТранРабот = \"АпкТранспортныеРаботыПоГодовомуПлану\" + \"Обороты\";\r\n")

# 1) remove from НайтиПервыйЭлемент
assert moved_block in text, "moved_block not found verbatim"
text = text.replace(moved_block, "", 1)

# 2) insert into СценарийСПотребностью, before its ТекстЗапроса assignment
anchor = "Функция СценарийСПотребностью()\r\n\r\n\tРезультат = Неопределено;\r\n\r\n\tТекстЗапроса"
assert anchor in text, "anchor not found"
text = text.replace(anchor, "Функция СценарийСПотребностью()\r\n\r\n\tРезультат = Неопределено;\r\n\r\n" + moved_block + "\r\n\tТекстЗапроса", 1)

# BOM + CRLF write back
with io.open(PATH, "wb") as f:
    f.write(b"\xef\xbb\xbf" + text.encode("utf-8"))

print("OK: moved block into СценарийСПотребностью")
