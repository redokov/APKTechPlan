#!/usr/bin/env python3
"""B6: Тх_ЗаполнениеКоэффициентов form - concrete-typed attributes (v2).

Same 8.5 problem as the record form: generic TypeSet fields can't be filled
via НТТ (ВвестиТекст rejected, choice button opens «Выбор типа данных»).
Fix: Работа gets a concrete type; base model input moves to typed attributes
БазоваяМодельСХТехники / БазоваяМодельАвтотранспорта (all visible, НТТ-safe);
generic БазоваяМодель kept for kinds without a model catalog. Server call
receives the value selected by ВидТехники.

Usage: python scripts/b6_filler_form_v2.py
"""
import io
import os

BASE = "src/cfe/ПланированиеТехникиАПК/DataProcessors/Тх_ЗаполнениеКоэффициентов/Forms/Форма"

# --- Module.bsl: patch ПараметрыЗаполнения block + add БазоваяМодельПоВиду
MOD = os.path.join(BASE, "Ext", "Form", "Module.bsl")
s = io.open(MOD, encoding="utf-8-sig", newline="").read()

old = ("\tПараметрыЗаполнения.Вставить(\"БазоваяМодель\", БазоваяМодель);\r\n")
new = ("\tПараметрыЗаполнения.Вставить(\"БазоваяМодель\", БазоваяМодельПоВиду());\r\n")
assert old in s, "server param block not found"
s = s.replace(old, new)

old2 = "\tТх_ТехникаСервер.АвтозаполнениеПоМощности(ПараметрыЗаполнения);\r\n\r\nКонецПроцедуры\r\n"
add = """\tТх_ТехникаСервер.АвтозаполнениеПоМощности(ПараметрыЗаполнения);

КонецПроцедуры

// Возвращает значение базовой модели из реквизита конкретного типа,
// соответствующего виду техники; для видов без каталога моделей -
// значение generic-поля БазоваяМодель (B6: НТТ-ввод в generic-поля
// невозможен в 8.5, поэтому ввод выполняется в типизированные поля).
//
// Возвращаемое значение:
//\t СправочникСсылка - базовая модель техники.
&НаСервере
Функция БазоваяМодельПоВиду()

\tЕсли ВидТехники = Перечисления.Тх_ВидыТехники.СХТехника Тогда
\t\tВозврат БазоваяМодельСХТехники;
\tИначеЕсли ВидТехники = Перечисления.Тх_ВидыТехники.Автотранспорт Тогда
\t\tВозврат БазоваяМодельАвтотранспорта;
\tИначе
\t\tВозврат БазоваяМодель;
\tКонецЕсли;

КонецФункции
"""
add = add.replace("\n", "\r\n")
assert old2 in s, "server call block not found"
s = s.replace(old2, add)

# ПроверитьЗаполнениеПолей: проверять типизированное значение
old3 = "\tЕсли НЕ ЗначениеЗаполнено(БазоваяМодель) Тогда"
new3 = "\tЕсли НЕ ЗначениеЗаполнено(БазоваяМодельСХТехники)\r\n\t\tИ НЕ ЗначениеЗаполнено(БазоваяМодельАвтотранспорта)\r\n\t\tИ НЕ ЗначениеЗаполнено(БазоваяМодель) Тогда"
assert old3 in s, "client check block not found"
s = s.replace(old3, new3)

io.open(MOD, "w", encoding="utf-8-sig", newline="").write(s)
print("[write] Module.bsl")

# --- Form.xml: concrete type for Работа, add typed base-model fields
FX = os.path.join(BASE, "Ext", "Form.xml")
f = io.open(FX, encoding="utf-8-sig", newline="").read()

# Работа: TypeSet -> concrete type
oldA = ('\t\t<Attribute name="Работа" id="19">\r\n\t\t\t<Title>\r\n\t\t\t\t<v8:item>\r\n\t\t\t\t\t<v8:lang>ru</v8:lang>\r\n\t\t\t\t\t<v8:content>Работа</v8:content>\r\n\t\t\t\t</v8:item>\r\n\t\t\t</Title>\r\n\t\t\t<Type>\r\n\t\t\t\t<v8:TypeSet>cfg:CatalogRef</v8:TypeSet>\r\n\t\t\t</Type>\r\n\t\t</Attribute>\r\n')
newA = ('\t\t<Attribute name="Работа" id="19">\r\n\t\t\t<Title>\r\n\t\t\t\t<v8:item>\r\n\t\t\t\t\t<v8:lang>ru</v8:lang>\r\n\t\t\t\t\t<v8:content>Работа</v8:content>\r\n\t\t\t\t</v8:item>\r\n\t\t\t</Title>\r\n\t\t\t<Type>\r\n\t\t\t\t<v8:Type>cfg:CatalogRef.ВидыРаботСотрудников</v8:Type>\r\n\t\t\t</Type>\r\n\t\t</Attribute>\r\n')
assert oldA in f, "Работа attribute not found"
f = f.replace(oldA, newA)

# add typed base-model attributes after БазоваяМодель attribute
oldB = ('\t\t<Attribute name="БазоваяМодель" id="22">')
newB = ('\t\t<Attribute name="БазоваяМодельСХТехники" id="23">\r\n'
        '\t\t\t<Title>\r\n\t\t\t\t<v8:item>\r\n\t\t\t\t\t<v8:lang>ru</v8:lang>\r\n\t\t\t\t\t<v8:content>Базовая модель (с/х техника)</v8:content>\r\n\t\t\t\t</v8:item>\r\n\t\t\t</Title>\r\n'
        '\t\t\t<Type>\r\n\t\t\t\t<v8:Type>cfg:CatalogRef.АпкМоделиСХТехники</v8:Type>\r\n\t\t\t</Type>\r\n\t\t</Attribute>\r\n'
        '\t\t<Attribute name="БазоваяМодельАвтотранспорта" id="24">\r\n'
        '\t\t\t<Title>\r\n\t\t\t\t<v8:item>\r\n\t\t\t\t\t<v8:lang>ru</v8:lang>\r\n\t\t\t\t\t<v8:content>Базовая модель (автотранспорт)</v8:content>\r\n\t\t\t\t</v8:item>\r\n\t\t\t</Title>\r\n'
        '\t\t\t<Type>\r\n\t\t\t\t<v8:Type>cfg:CatalogRef.АпкМоделиАвтотранспорта</v8:Type>\r\n\t\t\t</Type>\r\n\t\t</Attribute>\r\n'
        '\t\t<Attribute name="БазоваяМодель" id="22">')
assert oldB in f, "БазоваяМодель attribute not found"
f = f.replace(oldB, newB)

# add visible input fields for typed attributes: insert before БазоваяМодель field in ChildItems
# find the БазоваяМодель InputField in ChildItems
import re
m = re.search(r'(\t\t<InputField name="БазоваяМодель" id="\d+">)', f)
assert m, "БазоваяМодель input field not found"
fld = ('\t\t<InputField name="БазоваяМодельСХТехники" id="25">\r\n'
       '\t\t\t<DataPath>БазоваяМодельСХТехники</DataPath>\r\n'
       '\t\t\t<ContextMenu name="БазоваяМодельСХТехникиКонтекстноеМеню" id="26"/>\r\n'
       '\t\t\t<ExtendedTooltip name="БазоваяМодельСХТехникиРасширеннаяПодсказка" id="27"/>\r\n'
       '\t\t</InputField>\r\n'
       '\t\t<InputField name="БазоваяМодельАвтотранспорта" id="28">\r\n'
       '\t\t\t<DataPath>БазоваяМодельАвтотранспорта</DataPath>\r\n'
       '\t\t\t<ContextMenu name="БазоваяМодельАвтотранспортаКонтекстноеМеню" id="29"/>\r\n'
       '\t\t\t<ExtendedTooltip name="БазоваяМодельАвтотранспортаРасширеннаяПодсказка" id="30"/>\r\n'
       '\t\t</InputField>\r\n')
f = f[:m.start(1)] + fld + f[m.start(1):]

io.open(FX, "w", encoding="utf-8-sig", newline="").write(f)
print("[write] Form.xml")
