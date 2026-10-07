#!/usr/bin/env python3
"""B6 product fix: 8.5 virtual table syntax in ЗапросПотребности.

Root cause (found in B6): 1C 8.5 changed accumulation-register virtual
tables: `РегистрНакопления.<Имя>Обороты` -> `РегистрНакопления.<Имя>.Обороты()`
and resource fields inside get the `Оборот` suffix (`Смен_Вер` ->
`Смен_ВерОборот`). The 8.3-style text compiled fine (bsl-ls, CheckConfig)
but failed at runtime -> the whole deficit calculation was dead. Unit tests
13/14 SKIPped on missing data and masked it.

Fixes:
1. Тх_ТехникаСервер.ЗапросПотребности: dot-syntax + Оборот suffix (x2 parts).
2. Тх_Тесты.СценарийСПотребностью: switch to plain record tables (no virtual
   table needed to check "any потребность exists").

BSL files are utf-8-sig + CRLF; edited in binary-exact mode via newline=''.
"""
import io
import sys

FILES = {
    r"src/cfe/ПланированиеТехникиАПК/CommonModules/Тх_ТехникаСервер/Ext/Module.bsl": [
        # mech part: resource field + virtual table
        (
            '\t|\t\t\tМ.Смен" + Суффикс + " КАК Смен\r\n'
            '\t|\t\tИЗ РегистрНакопления.АпкМеханизированныеРаботыПоГодовомуПлануОбороты КАК М',
            '\t|\t\t\tМ.Смен" + Суффикс + "Оборот КАК Смен\r\n'
            '\t|\t\tИЗ РегистрНакопления.АпкМеханизированныеРаботыПоГодовомуПлану.Обороты() КАК М',
        ),
        # transport part
        (
            '\t|\t\t\tТран.Смен" + Суффикс + "\r\n'
            '\t|\t\tИЗ РегистрНакопления.АпкТранспортныеРаботыПоГодовомуПлануОбороты КАК Тран',
            '\t|\t\t\tТран.Смен" + Суффикс + "Оборот\r\n'
            '\t|\t\tИЗ РегистрНакопления.АпкТранспортныеРаботыПоГодовомуПлану.Обороты() КАК Тран',
        ),
    ],
    r"src/cfe/ПланированиеТехникиАПК/CommonModules/Тх_Тесты/Ext/Module.bsl": [
        (
            '\t// Имена таблиц годового плана - динамические (runtime, design 4.1/TD-001).\r\n'
            '\tИмяРегистраМехРабот = "АпкМеханизированныеРаботыПоГодовомуПлану" + "Обороты";\r\n'
            '\tИмяРегистраТранРабот = "АпкТранспортныеРаботыПоГодовомуПлану" + "Обороты";',
            '\t// Имена таблиц годового плана - динамические (runtime, design 4.1/TD-001).\r\n'
            '\t// 8.5: таблицы записей (виртуальная таблица оборотов требует измерения\r\n'
            '\t// в выборке, для проверки существования потребности она не нужна).\r\n'
            '\tИмяРегистраМехРабот = "АпкМеханизированныеРаботыПоГодовомуПлану";\r\n'
            '\tИмяРегистраТранРабот = "АпкТранспортныеРаботыПоГодовомуПлану";',
        ),
    ],
}


def main():
    for path, edits in FILES.items():
        with io.open(path, encoding="utf-8-sig", newline="") as f:
            s = f.read()
        for old, new in edits:
            if s.count(old) != 1:
                print("FAIL %s: pattern count=%d for %r" % (path, s.count(old), old[:60]))
                return 1
            s = s.replace(old, new)
        with io.open(path, "w", encoding="utf-8-sig", newline="") as f:
            f.write(s)
        print("patched %s (%d edits)" % (path, len(edits)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
