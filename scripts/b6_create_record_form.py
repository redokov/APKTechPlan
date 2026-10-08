#!/usr/bin/env python3
"""B6 fix: create Тх_ФормаЗаписи for the coefficients register and wire it
as DefaultRecordForm.

Root cause: the platform auto record-form is built on the record manager,
whose Записать() does not fire the record-set BeforeWrite — user edits
bypassed FR-003 validation. The new form is still built on the record manager
(standard pattern for register record forms) but validates in BeforeWrite via
Тх_ТехникаСервер.ПроверитьЗаписьКоэффициента (client -> server no-context).

Files created:
  Forms/Тх_ФормаЗаписи.xml                 (MetaDataObject)
  Forms/Тх_ФормаЗаписи/Ext/Form.xml       (form description)
  Forms/Тх_ФормаЗаписи/Ext/Form/Module.bsl (form module, CRLF, BOM)
Register XML edits:
  DefaultRecordForm -> ...Form.Тх_ФормаЗаписи
  ChildObjects += <Form>Тх_ФормаЗаписи</Form>
"""
import io
import uuid

BASE = "src/cfe/ПланированиеТехникиАПК/InformationRegisters/Тх_КоэффициентыПересчетаРабот"
FORM_UUID = "a3f7c2d1-9e54-4b18-8c3f-2d61b7e94a05"

MD_HEADER = (
    "\ufeff<?xml version=\"1.0\" encoding=\"UTF-8\"?>\r\n"
    "<MetaDataObject xmlns=\"http://v8.1c.ru/8.3/MDClasses\" "
    "xmlns:app=\"http://v8.1c.ru/8.2/managed-application/core\" "
    "xmlns:cfg=\"http://v8.1c.ru/8.1/data/enterprise/current-config\" "
    "xmlns:cmi=\"http://v8.1c.ru/8.2/managed-application/cmi\" "
    "xmlns:ent=\"http://v8.1c.ru/8.1/data/enterprise\" "
    "xmlns:lf=\"http://v8.1c.ru/8.2/managed-application/logform\" "
    "xmlns:pal=\"http://v8.1c.ru/8.1/data/ui/colors/palette\" "
    "xmlns:style=\"http://v8.1c.ru/8.1/data/ui/style\" "
    "xmlns:sys=\"http://v8.1c.ru/8.1/data/ui/fonts/system\" "
    "xmlns:v8=\"http://v8.1c.ru/8.1/data/core\" "
    "xmlns:v8ui=\"http://v8.1c.ru/8.1/data/ui\" "
    "xmlns:web=\"http://v8.1c.ru/8.1/data/ui/colors/web\" "
    "xmlns:win=\"http://v8.1c.ru/8.1/data/ui/colors/windows\" "
    "xmlns:xen=\"http://v8.1c.ru/8.3/xcf/enums\" "
    "xmlns:xpr=\"http://v8.1c.ru/8.3/xcf/predef\" "
    "xmlns:xr=\"http://v8.1c.ru/8.3/xcf/readable\" "
    "xmlns:xs=\"http://www.w3.org/2001/XMLSchema\" "
    "xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" version=\"2.22\">\r\n"
)

FORM_META = (
    MD_HEADER
    + "\t<Form uuid=\"" + FORM_UUID + "\">\r\n"
    + "\t\t<Properties>\r\n"
    + "\t\t\t<Name>Тх_ФормаЗаписи</Name>\r\n"
    + "\t\t\t<Synonym>\r\n"
    + "\t\t\t\t<v8:item>\r\n"
    + "\t\t\t\t\t<v8:lang>ru</v8:lang>\r\n"
    + "\t\t\t\t\t<v8:content>Коэффициент пересчёта работ</v8:content>\r\n"
    + "\t\t\t\t</v8:item>\r\n"
    + "\t\t\t</Synonym>\r\n"
    + "\t\t\t<Comment>Форма записи коэффициента (B6, 2026-10-09): замена платформенной автоформы, построенной на менеджере записи и обходившей контроль модуля набора (FR-003). Валидация - Тх_ТехникаСервер.ПроверитьЗаписьКоэффициента из ПередЗаписью.</Comment>\r\n"
    + "\t\t\t<FormType>Managed</FormType>\r\n"
    + "\t\t\t<IncludeHelpInContents>false</IncludeHelpInContents>\r\n"
    + "\t\t\t<UsePurposes>\r\n"
    + "\t\t\t\t<v8:Value xsi:type=\"app:ApplicationUsePurpose\">PlatformApplication</v8:Value>\r\n"
    + "\t\t\t\t<v8:Value xsi:type=\"app:ApplicationUsePurpose\">MobilePlatformApplication</v8:Value>\r\n"
    + "\t\t\t</UsePurposes>\r\n"
    + "\t\t\t<UseInInterfaceCompatibilityMode>Any</UseInInterfaceCompatibilityMode>\r\n"
    + "\t\t</Properties>\r\n"
    + "\t</Form>\r\n"
    + "</MetaDataObject>\r\n"
)

LF_HEADER = (
    "\ufeff<?xml version=\"1.0\" encoding=\"UTF-8\"?>\r\n"
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


def input_field(name, data_path, title, item_id, tip_id):
    ctx_id = item_id + 1
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
    + "\t</Events>\r\n"
    + "\t<ChildItems>\r\n"
    + input_field("Период", "Запись.Период", 1, 1, 2)
    + input_field("Работа", "Запись.Работа", 1, 3, 4)
    + input_field("ВидТехники", "Запись.ВидТехники", 1, 5, 6)
    + input_field("МодельТехники", "Запись.МодельТехники", 1, 7, 8)
    + input_field("Коэффициент", "Запись.Коэффициент", 1, 9, 10)
    + (
        "\t\t<CheckBoxField name=\"БазоваяМодель\" id=\"11\">\r\n"
        + "\t\t\t<DataPath>Запись.БазоваяМодель</DataPath>\r\n"
        + "\t\t\t<CheckBoxType>Auto</CheckBoxType>\r\n"
        + "\t\t\t<ContextMenu name=\"БазоваяМодельКонтекстноеМеню\" id=\"12\"/>\r\n"
        + "\t\t\t<ExtendedTooltip name=\"БазоваяМодельРасширеннаяПодсказка\" id=\"13\"/>\r\n"
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
    + "\t</Attributes>\r\n"
    + "</Form>\r\n"
)

FORM_MODULE = """\ufeff// Модуль формы записи коэффициента пересчёта работ.
//
// B6, 2026-10-09: замена платформенной автоформы записи. Автоформа построена
// на менеджере записи, а МенеджерЗаписи.Записать() не вызывает ПередЗаписью
// набора записей - контроль FR-003 в модуле набора обходился (probe
// heartbeat/b6_rmprobe3.txt). Здесь валидация выполняется перед записью
// формы вызовом Тх_ТехникаСервер.ПроверитьЗаписьКоэффициента.

&НаКлиенте
Процедура ПередЗаписью(Отказ, ПараметрыЗаписи)

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
\t\t\tСообщить(Текст);
\t\tКонецЦикла;
\tКонецЕсли;

КонецПроцедуры

&НаСервереБезКонтекста
Функция ПроверитьКоэффициентНаСервере(Работа, Период, ВидТехники,
\tМодельТехники, Коэффициент, БазоваяМодель)

\tВозврат Тх_ТехникаСервер.ПроверитьЗаписьКоэффициента(Работа, Период,
\t\tВидТехники, МодельТехники, Коэффициент, БазоваяМодель);

КонецФункции
""".replace("\n", "\r\n")


def write_file(path, content):
    with io.open(path, "w", encoding="utf-8-sig", newline="") as f:
        f.write(content)
    print("[write]", path)


def main():
    import os

    forms_dir = os.path.join(BASE, "Forms")
    write_file(os.path.join(forms_dir, "Тх_ФормаЗаписи.xml"), FORM_META)
    ext_dir = os.path.join(forms_dir, "Тх_ФормаЗаписи", "Ext")
    os.makedirs(ext_dir, exist_ok=True)
    write_file(os.path.join(ext_dir, "Form.xml"), FORM_XML)
    mod_dir = os.path.join(ext_dir, "Form")
    os.makedirs(mod_dir, exist_ok=True)
    write_file(os.path.join(mod_dir, "Module.bsl"), FORM_MODULE)

    # register XML: DefaultRecordForm + ChildObjects
    reg_path = os.path.join(BASE + ".xml")
    with io.open(reg_path, "r", encoding="utf-8-sig", newline="") as f:
        s = f.read()
    assert "Тх_ФормаЗаписи" not in s, "already wired"
    s = s.replace(
        "<DefaultRecordForm/>",
        "<DefaultRecordForm>InformationRegister."
        "Тх_КоэффициентыПересчетаРабот.Form.Тх_ФормаЗаписи</DefaultRecordForm>",
    )
    s = s.replace(
        "\t\t\t<Form>Тх_ФормаСписка</Form>\r\n",
        "\t\t\t<Form>Тх_ФормаСписка</Form>\r\n"
        "\t\t\t<Form>Тх_ФормаЗаписи</Form>\r\n",
    )
    with io.open(reg_path, "w", encoding="utf-8-sig", newline="") as f:
        f.write(s)
    print("[edit] register wired: DefaultRecordForm + ChildObjects")
    print("[uuid-check]", uuid.UUID(FORM_UUID).hex == FORM_UUID.replace("-", ""))


if __name__ == "__main__":
    main()
