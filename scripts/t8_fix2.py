#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T8 fix2: неверное имя системного перечисления - РежимПроведенияДокумента
не существует (поле .Проведение -> runtime "Поле объекта не обнаружено");
правильное имя - РежимЗаписиДокумента.Проведение (Записать)."""
import pathlib

TST = pathlib.Path(
    "src/cfe/ПланированиеТехникиАПК/CommonModules/Тх_Тесты/Ext/Module.bsl")

BOM = bytes([0xEF, 0xBB, 0xBF])


def main():
    t = TST.read_bytes()[3:].decode("utf-8")
    old = "ДокОбъект.Записать(РежимПроведенияДокумента.Проведение);"
    assert t.count(old) == 1, "якорь не найден"
    t = t.replace(old, "ДокОбъект.Записать(РежимЗаписиДокумента.Проведение);")
    TST.write_bytes(BOM + t.encode("utf-8"))
    print("t8_fix2: RezhimZapisiDokumenta.Provedenie")


if __name__ == "__main__":
    main()
