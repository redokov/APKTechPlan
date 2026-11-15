#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SRV-02 п.5 (аномалия прав 09, NFR-004): бисекция - убрать <DefaultRoles>
(Тх_Чтение + Тх_Редактирование) из Configuration.xml расширения.
Гипотеза (а): платформа при первичной загрузке пересозданного расширения
неявно применяет роли по умолчанию ко всем пользователям."""
import io
import sys

PATH = "src/cfe/ПланированиеТехникиАПК/Configuration.xml"

BLOCK = """\t\t\t<DefaultRoles>
\t\t\t\t<xr:Item xsi:type="xr:MDObjectRef">Role.Тх_Чтение</xr:Item>
\t\t\t\t<xr:Item xsi:type="xr:MDObjectRef">Role.Тх_Редактирование</xr:Item>
\t\t\t</DefaultRoles>
"""


def main():
    s = io.open(PATH, encoding="utf-8").read()
    assert s.count(BLOCK) == 1, s.count(BLOCK)
    s = s.replace(BLOCK, "")
    assert "DefaultRoles" not in s
    io.open(PATH, "w", encoding="utf-8", newline="").write(s)
    sys.stdout.buffer.write("OK: DefaultRoles удалён из Configuration.xml\n".encode("utf-8"))


if __name__ == "__main__":
    main()
