#!/usr/bin/env python3
"""B6 fix (v4): rewrite Тх_ФормаЗаписи - concrete-typed input attributes, all visible.

History:
 - v2: StartChoice handlers - useless: 8.5 opens «Выбор типа данных» for
   any composite-typed field regardless of value typing.
 - v3: typed attributes + visibility switching by ВидТехники - НТТ does not
   raise OnChange, so НТТ-driven tests can't switch visibility.
 - v4 (current): typed attributes РаботаВвод / МодельСХТехники /
   МодельАвтотранспорта, ALL always visible; generic МодельТехники kept for
   kinds without a model catalog; no OnChange handling. Sync in
   ПриСозданииНаСервере (record -> attrs) and ПередЗаписью (attrs -> record).

Usage: python scripts/b6_record_form_v3.py
"""
import io
import os

BASE = "src/cfe/ПланированиеТехникиАПК/InformationRegisters/Тх_КоэффициентыПересчетаРабот/Forms/Тх_ФормаЗаписи"

MODULE = """// Модуль формы записи коэффициента пересчёта работ.
//
// B6, 2026-10-09 (v4): поля generic-составного типа (TypeSet CatalogRef,
// TD-001) в 8.5 при нажатии выбора всегда открывают окно «Выбор типа
// данных», а МенеджерЗаписи.Записать() не вызывает ПередЗаписью набора -
// контроль FR-003 в модуле набора обходился. Поэтому:
//  1) ввод выполняется в реквизиты формы с конкретными типами
//     (РаботаВвод, МодельСХТехники, МодельАвтотранспорта), видимые всегда
//     (НТТ-выбор значений не порождает OnChange - видимость не переключаем);
//     для видов техники без каталога моделей остаётся generic-поле;
//  2) валидация выполняется вызовом
//     Тх_ТехникаСервер.ПроверитьЗаписьКоэффициента из ПередЗаписью.

&НаКлиенте
Процедура ПередЗаписью(Отказ, ПараметрыЗаписи)

\t// Перенос значений из реквизитов ввода в запись.
\tЗапись.Работа = РаботаВвод;
\tЗапись.МодельТехники = МодельТехникиПоВиду();

\t// FR-003(б): у базовой строки коэффициент принудительно 1,0000.
\tЕсли Запись.БазоваяМодель Тогда
\t\tЗапись.Коэффициент = 1;
\tКонецЕсли;

\tСообщения = ПроверитьКоэффициентНаСервере(Запись.Работа, Запись.Период,
\t\tЗапись.ВидТехники, Запись.МодельТехники, Запись.Коэффициент,
\t\tЗапись.БазоваяМодель);
\tЕсли Сообщения.Количество() > 0 Тогда
\t\tОтказ = Истина;
\t\tДля Каждого Текст Из Сообщения Цикл
\t\t\tСообщение = Новый СообщениеПользователю;
\t\t\tСообщение.Текст = Текст;
\t\t\tСообщение.Сообщить();
\t\tКонецЦикла;
\tКонецЕсли;

КонецПроцедуры

&НаСервере
Процедура ПриСозданииНаСервере(Отказ, СтандартнаяОбработка)

\t// Перенос значений записи в реквизиты ввода конкретных типов
\t// (при редактировании существующей записи).
\tЕсли Тх_ТехникаСервер.ВалидироватьТипАПК(Запись.Работа,
\t\tТх_ТехникаСервер.ИмяСправочникаРабот()) Тогда
\t\tРаботаВвод = Запись.Работа;
\tКонецЕсли;
\tУстановитьМодельПоВиду();

КонецПроцедуры

// Возвращает значение модели из реквизита конкретного типа,
// соответствующего виду техники; для видов без каталога моделей -
// значение generic-поля.
//
// Возвращаемое значение:
//\t СправочникСсылка - модель техники.
&НаСервере
Функция МодельТехникиПоВиду()

\tЕсли Запись.ВидТехники = Перечисления.Тх_ВидыТехники.СХТехника Тогда
\t\tВозврат МодельСХТехники;
\tИначеЕсли Запись.ВидТехники = Перечисления.Тх_ВидыТехники.Автотранспорт Тогда
\t\tВозврат МодельАвтотранспорта;
\tИначе
\t\tВозврат Запись.МодельТехники;
\tКонецЕсли;

КонецФункции

// Переносит значение записи в реквизит модели соответствующего каталога.
&НаСервере
Процедура УстановитьМодельПоВиду()

\tЕсли Запись.ВидТехники = Перечисления.Тх_ВидыТехники.СХТехника Тогда
\t\tЕсли Тх_ТехникаСервер.ВалидироватьТипАПК(Запись.МодельТехники,
\t\t\tТх_ТехникаСервер.ИмяСправочникаМоделейСХТехники()) Тогда
\t\t\tМодельСХТехники = Запись.МодельТехники;
\t\tКонецЕсли;
\tИначеЕсли Запись.ВидТехники = Перечисления.Тх_ВидыТехники.Автотранспорт Тогда
\t\tЕсли Тх_ТехникаСервер.ВалидироватьТипАПК(Запись.МодельТехники,
\t\t\tТх_ТехникаСервер.ИмяСправочникаМоделей(Запись.ВидТехники)) Тогда
\t\t\tМодельАвтотранспорта = Запись.МодельТехники;
\t\tКонецЕсли;
\tИначе
\t\t// Для видов без каталога моделей ввод - в generic-поле МодельТехники.
\tКонецЕсли;

КонецПроцедуры

&НаСервереБезКонтекста
Функция ПроверитьКоэффициентНаСервере(Знач Работа, Знач Период,
\tЗнач ВидТехники, Знач МодельТехники, Знач Коэффициент,
\tЗнач БазоваяМодель)

\tВозврат Тх_ТехникаСервер.ПроверитьЗаписьКоэффициента(Работа, Период,
\t\tВидТехники, МодельТехники, Коэффициент, БазоваяМодель);

КонецФункции
"""

LF_HEADER = (
    "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\r\n"
    "<Form xmlns=\"http://v8.1c.ru/8.3/xcf/logform\" "
    "xmlns:app=\"http://v8.1c.ru/8.2/managed-application/core\" "
    "xmlns:cfg=\"http://v8.1c.ru/8.1/data/enterprise/current-config\" "
    "xmlns:dcscor=\"http://v8.1c.ru/8.1/data-composition-system/core\" "
    "xmlns:dcssch=\"http://v8.1c.ru/8.1/data-composition-system/schema\" "
    "xmlns:dcsset=\"http://v8.1c.ru/8.1/data-composition-system/settings\" "
    "xmlns:ent=\"http://v8.1c.ru/8.1/data/enterprise\" "
    "xmlns:lf=\"http://v8.1c.ru/8.2/managed-application/logform\" "
    "xmlns:pal=\"http://v8.1c.ru/8.1/data/ui/colors/palette\" "
    "xmlns:style=\"http://v8.1c.ru/8.1/data/ui/style\" "
    "xmlns:sys=\"http://v8.1c.ru/8.1/data/ui/fonts/system\" "
    "xmlns:v8=\"http://v8.1c.ru/8.1/data/core\" "
    "xmlns:v8ui=\"http://v8.1c.ru/8.1/data/ui\" "
    "xmlns:web=\"http://v8.1c.ru/8.1/data/ui/colors/web\" "
    "xmlns:win=\"http://v8.1c.ru/8.1/data/ui/colors/windows\" "
    "xmlns:xr=\"http://v8.1c.ru/8.3/xcf/readable\" "
    "xmlns:xs=\"http://www.w3.org/2001/XMLSchema\" "
    "xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" version=\"2.22\">\r\n"
)


def field(name, data_path, item_id, ctx_id, tip_id):
    return (
        "\t\t<InputField name=\"" + name + "\" id=\"" + str(item_id) + "\">\r\n"
        + "\t\t\t<DataPath>" + data_path + "</DataPath>\r\n"
        + "\t\t\t<ContextMenu name=\"" + name + "КонтекстноеМеню\" id=\"" + str(ctx_id) + "\"/>\r\n"
        + "\t\t\t<ExtendedTooltip name=\"" + name + "РасширеннаяПодсказка\" id=\"" + str(tip_id) + "\"/>\r\n"
        + "\t\t</InputField>\r\n"
    )


FORM_XML = (
    LF_HEADER
    + "\t<WindowOpeningMode>LockOwnerWindow</WindowOpeningMode>\r\n"
    + "\t<AutoCommandBar name=\"ФормаКоманднаяПанель\" id=\"-1\"/>\r\n"
    + "\t<Events>\r\n"
    + "\t\t<Event name=\"BeforeWrite\">ПередЗаписью</Event>\r\n"
    + "\t\t<Event name=\"OnCreateAtServer\">ПриСозданииНаСервере</Event>\r\n"
    + "\t</Events>\r\n"
    + "\t<ChildItems>\r\n"
    + field("Период", "Запись.Период", 1, 2, 3)
    + field("РаботаВвод", "РаботаВвод", 4, 5, 6)
    + field("ВидТехники", "Запись.ВидТехники", 7, 8, 9)
    + field("МодельСХТехники", "МодельСХТехники", 10, 11, 12)
    + field("МодельАвтотранспорта", "МодельАвтотранспорта", 13, 14, 15)
    + field("МодельТехники", "Запись.МодельТехники", 16, 17, 18)
    + field("Коэффициент", "Запись.Коэффициент", 19, 20, 21)
    + (
        "\t\t<CheckBoxField name=\"БазоваяМодель\" id=\"22\">\r\n"
        + "\t\t\t<DataPath>Запись.БазоваяМодель</DataPath>\r\n"
        + "\t\t\t<CheckBoxType>Auto</CheckBoxType>\r\n"
        + "\t\t\t<ContextMenu name=\"БазоваяМодельКонтекстноеМеню\" id=\"23\"/>\r\n"
        + "\t\t\t<ExtendedTooltip name=\"БазоваяМодельРасширеннаяПодсказка\" id=\"24\"/>\r\n"
        + "\t\t</CheckBoxField>\r\n"
    )
    + "\t</ChildItems>\r\n"
    + "\t<Attributes>\r\n"
    + "\t\t<Attribute name=\"Запись\" id=\"1\">\r\n"
    + "\t\t\t<Type>\r\n"
    + "\t\t\t\t<v8:Type>cfg:InformationRegisterRecordManager.Тх_КоэффициентыПересчетаРабот</v8:Type>\r\n"
    + "\t\t\t</Type>\r\n"
    + "\t\t\t<MainAttribute>true</MainAttribute>\r\n"
    + "\t\t\t<SavedData>true</SavedData>\r\n"
    + "\t\t</Attribute>\r\n"
    + "\t\t<Attribute name=\"РаботаВвод\" id=\"2\">\r\n"
    + "\t\t\t<Type>\r\n"
    + "\t\t\t\t<v8:Type>cfg:CatalogRef.ВидыРаботСотрудников</v8:Type>\r\n"
    + "\t\t\t</Type>\r\n"
    + "\t\t</Attribute>\r\n"
    + "\t\t<Attribute name=\"МодельСХТехники\" id=\"3\">\r\n"
    + "\t\t\t<Type>\r\n"
    + "\t\t\t\t<v8:Type>cfg:CatalogRef.АпкМоделиСХТехники</v8:Type>\r\n"
    + "\t\t\t</Type>\r\n"
    + "\t\t</Attribute>\r\n"
    + "\t\t<Attribute name=\"МодельАвтотранспорта\" id=\"4\">\r\n"
    + "\t\t\t<Type>\r\n"
    + "\t\t\t\t<v8:Type>cfg:CatalogRef.АпкМоделиАвтотранспорта</v8:Type>\r\n"
    + "\t\t\t</Type>\r\n"
    + "\t\t</Attribute>\r\n"
    + "\t</Attributes>\r\n"
    + "</Form>\r\n"
)


def main():
    with io.open(os.path.join(BASE, "Ext", "Form.xml"), "w", encoding="utf-8-sig", newline="") as f:
        f.write(FORM_XML)
    print("[write] Form.xml (v4)")
    with io.open(os.path.join(BASE, "Ext", "Form", "Module.bsl"), "w", encoding="utf-8-sig", newline="") as f:
        f.write(MODULE.replace("\n", "\r\n"))
    print("[write] Module.bsl (v4)")


if __name__ == "__main__":
    main()
