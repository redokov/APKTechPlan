#!/usr/bin/env python3
"""B6 fix: disable ListChoiceMode on reference InputFields in Tх_ forms.

8.5/Taxi: reference fields default to a pick-list (recent values), which makes
TestClient's ВвестиТекст fail ("Неподходящий тип элемента управления") and the
generic composite types open a "Выбор типа данных" dialog on the choice button.
With <ListChoiceMode>false</ListChoiceMode> text input is allowed and
Enter-substring selection works (VA steps "в поле ввожу текст" +
"выбираю по строке").

Forms patched (idempotent, only adds the flag where missing):
  - Тх_ФормаЗаписи (register record form)
  - Тх_ФормаДокумента (document form, incl. tabular columns)
  - Тх_ЗаполнениеКоэффициентов/Форма
  - Тх_РасчетДефицита/Форма
"""
import io
import re

FORMS = [
    "src/cfe/ПланированиеТехникиАПК/InformationRegisters/Тх_КоэффициентыПересчетаРабот/Forms/Тх_ФормаЗаписи/Ext/Form.xml",
    "src/cfe/ПланированиеТехникиАПК/Documents/Тх_ПланТехническихРесурсов/Forms/Тх_ФормаДокумента/Ext/Form.xml",
    "src/cfe/ПланированиеТехникиАПК/DataProcessors/Тх_ЗаполнениеКоэффициентов/Forms/Форма/Ext/Form.xml",
    "src/cfe/ПланированиеТехникиАПК/DataProcessors/Тх_РасчетДефицита/Forms/Форма/Ext/Form.xml",
]

REF_INPUTS = [
    "Работа", "МодельТехники", "БазоваяМодель",
    "Организация", "Подразделение", "СценарийПланирования",
    "ОсновнаяТехникаТранспортноеСредство", "ОсновнаяТехникаМодельТехники",
    "ОборудованиеТранспортноеСредство", "ОборудованиеМодельТехники",
    "АвтотранспортТранспортноеСредство", "АвтотранспортМодельТехники",
]


def main():
    for path in FORMS:
        with io.open(path, "r", encoding="utf-8-sig", newline="") as f:
            s = f.read()
        crlf = "\r\n" in s
        nl = "\r\n" if crlf else "\n"
        orig = s
        for name in REF_INPUTS:
            # <InputField name="X" id="N"> ... <DataPath>...</DataPath>
            pat = re.compile(
                r'(<InputField name="' + re.escape(name) + r'" id="\d+">'
                r'(?:.*?<DataPath>[^<]*</DataPath>))',
                re.DOTALL)
            m = pat.search(s)
            if not m:
                continue
            block = m.group(1)
            if "ListChoiceMode" in block:
                continue
            s = s[:m.end(1)] + nl + "\t\t\t<ListChoiceMode>false</ListChoiceMode>" + s[m.end(1):]
        if s != orig:
            with io.open(path, "w", encoding="utf-8-sig", newline="") as f:
                f.write(s)
            print("[patch]", path)
        else:
            print("[skip]", path)


if __name__ == "__main__":
    main()
