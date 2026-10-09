# -*- coding: utf-8 -*-
"""T7: DataProcessor Тх_ФормированиеПланаРаботТехники + ПотребностьПоТехкартам
(FR-003.1-2, TD-005/006, design §5.4/§6.1).

1. DataProcessor XML (новые UUID) + Forms/Форма.xml + Ext/Form.xml + Module.bsl.
2. Configuration.xml ChildObjects.
3. Subsystem Content.
4. CommandInterface (visibility + order).
5. Roles x2 (Use/View).
6. Тх_ТехникаСервер: +область ФормированиеПланаРабот, +ПотребностьПоТехкартам.
7. Тх_Тесты: +область Тесты_ПотребностьПоТехкартам (+2 теста).
8. Раннер: +2 обёртки (итого 15).
9. run_unit_tests.py: 15.
"""
import pathlib
import re
import sys
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src/cfe/ПланированиеТехникиАПК"
P_SRV = SRC / "CommonModules/Тх_ТехникаСервер/Ext/Module.bsl"
P_TST = SRC / "CommonModules/Тх_Тесты/Ext/Module.bsl"
P_RUN = SRC / "DataProcessors/Тх_РаннерТестов/Ext/ObjectModule.bsl"
P_UT = ROOT / "scripts/run_unit_tests.py"
NEWPROC = "Тх_ФормированиеПланаРаботТехники"
NPPATH = SRC / "DataProcessors" / NEWPROC

ok_all = True


def check(cond, msg):
    global ok_all
    print(("OK " if cond else "FAIL ") + msg.encode("ascii", "backslashreplace").decode())
    if not cond:
        ok_all = False


def save_sig(p, text):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"\xef\xbb\xbf" + text.replace("\n", "\r\n").encode("utf-8"))


def load(p):
    b = p.read_bytes()
    return b[3:].decode("utf-8")


def save(p, text):
    p.write_bytes(b"\xef\xbb\xbf" + text.encode("utf-8"))


HDR = ('<?xml version="1.0" encoding="UTF-8"?>\n'
       '<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" '
       'xmlns:app="http://v8.1c.ru/8.2/managed-application/core" '
       'xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" '
       'xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" '
       'xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" '
       'xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" '
       'xmlns:pal="http://v8.1c.ru/8.1/data/ui/colors/palette" '
       'xmlns:style="http://v8.1c.ru/8.1/data/ui/style" '
       'xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" '
       'xmlns:v8="http://v8.1c.ru/8.1/data/core" '
       'xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" '
       'xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" '
       'xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" '
       'xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" '
       'xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" '
       'xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" '
       'xmlns:xs="http://www.w3.org/2001/XMLSchema" '
       'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.22">\n')


def gen_processor_xml():
    t_obj, v_obj = str(uuid.uuid4()), str(uuid.uuid4())
    t_mgr, v_mgr = str(uuid.uuid4()), str(uuid.uuid4())
    return HDR + f"""\t<DataProcessor uuid="{str(uuid.uuid4())}">
\t\t<InternalInfo>
\t\t\t<xr:GeneratedType name="DataProcessorObject.{NEWPROC}" category="Object">
\t\t\t\t<xr:TypeId>{t_obj}</xr:TypeId>
\t\t\t\t<xr:ValueId>{v_obj}</xr:ValueId>
\t\t\t</xr:GeneratedType>
\t\t\t<xr:GeneratedType name="DataProcessorManager.{NEWPROC}" category="Manager">
\t\t\t\t<xr:TypeId>{t_mgr}</xr:TypeId>
\t\t\t\t<xr:ValueId>{v_mgr}</xr:ValueId>
\t\t\t</xr:GeneratedType>
\t\t</InternalInfo>
\t\t<Properties>
\t\t\t<Name>{NEWPROC}</Name>
\t\t\t<Synonym>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Формирование плана работ техники</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Synonym>
\t\t\t<Comment>Launch form of the work plan forming (design 5.4/6.1, TD-005/006): collects demand parameters (Organization/Department/Scenario/Period/DaysPerPeriod/ShiftsPerDay), queries demand from APK yearly plan turnover registers via Tkh_TekhnikaServer.PotrebnostPoTekhkartam. Document creation/filling - T9 (ZapolnitPlanRabot).</Comment>
\t\t\t<UseStandardCommands>true</UseStandardCommands>
\t\t\t<DefaultForm>DataProcessor.{NEWPROC}.Form.Форма</DefaultForm>
\t\t\t<AuxiliaryForm/>
\t\t\t<IncludeHelpInContents>false</IncludeHelpInContents>
\t\t\t<ExtendedPresentation/>
\t\t\t<Explanation/>
\t\t</Properties>
\t\t<ChildObjects>
\t\t\t<Form>Форма</Form>
\t\t</ChildObjects>
\t</DataProcessor>
</MetaDataObject>
"""


def gen_form_meta_xml():
    return HDR + f"""\t<Form uuid="{str(uuid.uuid4())}">
\t\t<Properties>
\t\t\t<Name>Форма</Name>
\t\t\t<Synonym>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Формирование плана работ техники</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Synonym>
\t\t\t<Comment/>
\t\t\t<FormType>Managed</FormType>
\t\t\t<IncludeHelpInContents>false</IncludeHelpInContents>
\t\t\t<UsePurposes>
\t\t\t\t<v8:Value xsi:type="app:ApplicationUsePurpose">PlatformApplication</v8:Value>
\t\t\t\t<v8:Value xsi:type="app:ApplicationUsePurpose">MobilePlatformApplication</v8:Value>
\t\t\t</UsePurposes>
\t\t\t<UseInInterfaceCompatibilityMode>Any</UseInInterfaceCompatibilityMode>
\t\t\t<ExtendedPresentation/>
\t\t</Properties>
\t</Form>
</MetaDataObject>
"""


def field(name, id0, datapath, title, type_xml, tooltip, events=""):
    # Платформенная нормализация: <Events> идёт ПОСЛЕ <ExtendedTooltip>
    ev = ("\t\t\t\t<Events>\n\t\t\t\t\t<Event name=\"StartChoice\">" + name + "НачалоВыбора</Event>\n"
          "\t\t\t\t</Events>\n") if events else ""
    return f"""\t\t\t<InputField name="{name}" id="{id0}">
\t\t\t\t<DataPath>{datapath}</DataPath>
\t\t\t\t<ListChoiceMode>false</ListChoiceMode>
\t\t\t\t<Title>
\t\t\t\t\t<v8:item>
\t\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t\t<v8:content>{title}</v8:content>
\t\t\t\t\t</v8:item>
\t\t\t\t</Title>
\t\t\t\t<ToolTip>
\t\t\t\t\t<v8:item>
\t\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t\t<v8:content>{tooltip}</v8:content>
\t\t\t\t\t</v8:item>
\t\t\t\t</ToolTip>
\t\t\t\t<ClearButton>true</ClearButton>
\t\t\t\t<ContextMenu name="{name}КонтекстноеМеню" id="{id0 + 1}"/>
\t\t\t\t<ExtendedTooltip name="{name}РасширеннаяПодсказка" id="{id0 + 2}"/>
{ev}\t\t\t</InputField>
"""


def gen_form_xml():
    types = {
        "Организация": "\t\t\t\t<Type>\n\t\t\t\t\t<v8:Type>cfg:CatalogRef.Организации</v8:Type>\n\t\t\t\t</Type>\n",
        "Подразделение": "\t\t\t\t<Type>\n\t\t\t\t\t<v8:Type>cfg:CatalogRef.СтруктураПредприятия</v8:Type>\n\t\t\t\t</Type>\n",
        "СценарийПланирования": "\t\t\t\t<Type>\n\t\t\t\t\t<v8:Type>cfg:CatalogRef.АпкСценарииПланирования</v8:Type>\n\t\t\t\t</Type>\n",
        "ПериодС": "\t\t\t\t<Type>\n\t\t\t\t\t<v8:Type>xs:dateTime</v8:Type>\n\t\t\t\t\t<v8:DateQualifiers>\n\t\t\t\t\t\t<v8:DateFractions>Date</v8:DateFractions>\n\t\t\t\t\t</v8:DateQualifiers>\n\t\t\t\t</Type>\n",
        "ПериодПо": "\t\t\t\t<Type>\n\t\t\t\t\t<v8:Type>xs:dateTime</v8:Type>\n\t\t\t\t\t<v8:DateQualifiers>\n\t\t\t\t\t\t<v8:DateFractions>Date</v8:DateFractions>\n\t\t\t\t\t</v8:DateQualifiers>\n\t\t\t\t</Type>\n",
        "ДнейПериода": "\t\t\t\t<Type>\n\t\t\t\t\t<v8:Type>xs:decimal</v8:Type>\n\t\t\t\t\t<v8:NumberQualifiers>\n\t\t\t\t\t\t<v8:Digits>10</v8:Digits>\n\t\t\t\t\t\t<v8:FractionDigits>0</v8:FractionDigits>\n\t\t\t\t\t\t<v8:AllowedSign>Nonnegative</v8:AllowedSign>\n\t\t\t\t\t</v8:NumberQualifiers>\n\t\t\t\t</Type>\n",
        "СменВдень": "\t\t\t\t<Type>\n\t\t\t\t\t<v8:Type>xs:decimal</v8:Type>\n\t\t\t\t\t<v8:NumberQualifiers>\n\t\t\t\t\t\t<v8:Digits>5</v8:Digits>\n\t\t\t\t\t\t<v8:FractionDigits>1</v8:FractionDigits>\n\t\t\t\t\t\t<v8:AllowedSign>Nonnegative</v8:AllowedSign>\n\t\t\t\t\t</v8:NumberQualifiers>\n\t\t\t\t</Type>\n",
    }
    attrs = ["Организация", "Подразделение", "СценарийПланирования",
             "ПериодС", "ПериодПо", "ДнейПериода", "СменВдень"]
    attr_ids = {a: 30 + i for i, a in enumerate(attrs)}
    attr_xml = "".join(
        f"""\t\t<Attribute name="{a}" id="{attr_ids[a]}">
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>{a}</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
{types[a]}\t\t</Attribute>
""" for a in attrs)

    fields = (
        field("Организация", 3, "Организация", "Организация", "",
              "Пусто - все организации") +
        field("Подразделение", 6, "Подразделение", "Подразделение", "",
              "Пусто - все подразделения выращивания (отбор В ИЕРАРХИИ)") +
        field("СценарийПланирования", 9, "СценарийПланирования",
              "Сценарий планирования", "", "Обязательный параметр", events="1") +
        field("ПериодС", 12, "ПериодС", "Период с", "",
              "Левая граница окна потребности (пересечение с периодами строк техкарт)") +
        field("ПериодПо", 15, "ПериодПо", "Период по", "",
              "Правая граница окна потребности") +
        field("ДнейПериода", 18, "ДнейПериода", "Дней в периоде", "",
              "Календарных дней периода для расчёта количества единиц (T9)") +
        field("СменВдень", 21, "СменВдень", "Смен в день", "",
              "1..3, по умолчанию 1")
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Form xmlns="http://v8.1c.ru/8.3/xcf/logform" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:dcscor="http://v8.1c.ru/8.1/data-composition-system/core" xmlns:dcssch="http://v8.1c.ru/8.1/data-composition-system/schema" xmlns:dcsset="http://v8.1c.ru/8.1/data-composition-system/settings" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:pal="http://v8.1c.ru/8.1/data/ui/colors/palette" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.22">
\t<Title>
\t\t<v8:item>
\t\t\t<v8:lang>ru</v8:lang>
\t\t\t<v8:content>Формирование плана работ техники</v8:content>
\t\t</v8:item>
\t</Title>
\t<AutoTitle>false</AutoTitle>
\t<AutoCommandBar name="ФормаКоманднаяПанель" id="-1"/>
\t<ChildItems>
\t\t<UsualGroup name="ГруппаПараметров" id="1">
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Параметры потребности</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<Group>HorizontalIfPossible</Group>
\t\t\t<ExtendedTooltip name="ГруппаПараметровРасширеннаяПодсказка" id="2"/>
\t\t\t<ChildItems>
{fields}\t\t\t</ChildItems>
\t\t</UsualGroup>
\t\t<Button name="КнопкаСформировать" id="24">
\t\t\t<Type>UsualButton</Type>
\t\t\t<CommandName>Form.Command.Сформировать</CommandName>
\t\t\t<ExtendedTooltip name="КнопкаСформироватьРасширеннаяПодсказка" id="25"/>
\t\t</Button>
\t</ChildItems>
\t<Attributes>
\t\t<Attribute name="Объект" id="38">
\t\t\t<Type>
\t\t\t\t<v8:Type>cfg:DataProcessorObject.{NEWPROC}</v8:Type>
\t\t\t</Type>
\t\t\t<MainAttribute>true</MainAttribute>
\t\t</Attribute>
{attr_xml}\t</Attributes>
\t<Commands>
\t\t<Command name="Сформировать" id="40">
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Сформировать</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<Action>Сформировать</Action>
\t\t</Command>
\t</Commands>
</Form>
"""


FORM_MODULE = """// Форма обработки «Тх_ФормированиеПланаРаботТехники» (design 5.4/6.1, T7):
// параметры потребности по техкартам годового плана АПК и кнопка
// «Сформировать» (Form.Command.Сформировать).
//
// T7: кнопка выполняет запрос потребности
// (Тх_ТехникаСервер.ПотребностьПоТехкартам) и сообщает сводку результата;
// создание и заполнение документа «Потребность в технике» - T9
// (Тх_ТехникаСервер.ЗаполнитьПланРабот).
//
// Без модальности и фоновых заданий (NFR-001). Форма выбора типового
// справочника сценариев открывается по строковому имени (FAQ Q8, TD-001).

&НаКлиенте
Процедура СценарийПланированияНачалоВыбора(Элемент, СтандартнаяОбработка)

\tСтандартнаяОбработка = Ложь;
\tОткрытьФорму("Справочник." + ИмяСправочникаСценариев() + ".ФормаВыбора", , Элемент);

КонецПроцедуры

&НаСервере
Процедура ПриСозданииНаСервере(Отказ, СтандартнаяОбработка)

\t// Умолчание (design 5.4): СменВдень = 1.
\tЕсли НЕ ЗначениеЗаполнено(СменВдень) Тогда
\t\tСменВдень = 1;
\tКонецЕсли;

КонецПроцедуры

&НаКлиенте
Процедура Сформировать(Команда)

\t// Сценарий планирования обязателен (design 5.4).
\tЕсли НЕ ЗначениеЗаполнено(СценарийПланирования) Тогда
\t\tПоказатьПредупреждение(,
\t\t\tНСтр("ru = 'Укажите сценарий планирования.'"));
\t\tВозврат;
\tКонецЕсли;

\tРезультат = СформироватьНаСервере();

\tЕсли Результат.КоличествоСтрок = 0 Тогда
\t\t// Крайний случай design: техкарты за период не найдены.
\t\tПоказатьОповещениеПользователя(НСтр("ru = 'Формирование плана работ'"), ,
\t\t\tНСтр("ru = 'Техкарты за период не найдены.'"));
\tИначе
\t\tПоказатьОповещениеПользователя(НСтр("ru = 'Формирование плана работ'"), ,
\t\t\tСтрШаблон(НСтр("ru = 'Строк потребности: %1, смен всего: %2 (часов: %3)'"),
\t\t\t\tРезультат.КоличествоСтрок, Результат.ВсегоСмен, Результат.ВсегоЧасов));
\tКонецЕсли;

КонецПроцедуры

&НаСервере
Функция СформироватьНаСервере()

\t// Сборка параметров запроса потребности (design 6.1, TD-005) и сводка
\t// результата; заполнение документа - T9.
\tПараметрыЗапроса = Новый Структура;
\tПараметрыЗапроса.Вставить("СценарийПланирования", СценарийПланирования);
\tПараметрыЗапроса.Вставить("Организация", Организация);
\tПараметрыЗапроса.Вставить("Подразделение", Подразделение);
\tПараметрыЗапроса.Вставить("ДатаНачала", ПериодС);
\tПараметрыЗапроса.Вставить("ДатаОкончания", ПериодПо);

\tВыборка = Тх_ТехникаСервер.ПотребностьПоТехкартам(ПараметрыЗапроса).Выбрать();

\tРезультат = Новый Структура("КоличествоСтрок, ВсегоСмен, ВсегоЧасов", 0, 0, 0);
\tПока Выборка.Следующий() Цикл
\t\tРезультат.КоличествоСтрок = Результат.КоличествоСтрок + 1;
\t\tРезультат.ВсегоСмен = Результат.ВсегоСмен + Выборка.ПотребностьСмен;
\t\tРезультат.ВсегоЧасов = Результат.ВсегоЧасов + Выборка.ПотребностьЧасов;
\tКонецЦикла;

\tВозврат Результат;

КонецФункции

&НаКлиенте
Функция ИмяСправочникаСценариев()

\t// Локальная константа имени (design 4.1, п. 3): каноническое значение хранит
\t// Тх_ТехникаСервер.ИмяСправочникаСценариевПланирования; серверный модуль с
\t// клиента недоступен (FAQ Q8), значение продублировано в клиентском модуле.
\tВозврат "АпкСценарииПланирования";

КонецФункции
"""


SERVER_FUNC = """#Область ФормированиеПланаРабот

// Возвращает агрегированную потребность в технике по оборотам регистров
// годового плана АПК (design 6.1, TD-005/TD-006, FR-003.1-2):
// суммы Смен_Вер/Часов_Вер (вероятностный план - базовый вариант АПК;
// *_Мин/_Макс не читаем, переключатель - релиз 2) по виду работ, модели
// техники и оборудованию, отдельно для СХ-техники и автотранспорта.
//
// Источники - обороты ДВУХ регистров накопления (TD-005):
//   АпкМеханизированныеРаботыПоГодовомуПлану (Техника/Оборудование) и
//   АпкТранспортныеРаботыПоГодовомуПлану (Автомобиль/Прицеп).
// Период - пересечение ПериодНачала/ПериодОкончания строк техкарт с окном
// запроса (FAQ Q2). Подразделение выращивания - отбор В ИЕРАРХИИ
// (включая дочерние, если указано групповое).
//
// Параметры:
//   Параметры - Структура:
//     * СценарийПланирования - СправочникСсылка - сценарий (обязателен);
//     * Организация     - СправочникСсылка - отбор, если заполнена;
//     * Подразделение   - СправочникСсылка - отбор В ИЕРАРХИИ, если заполнено;
//     * ДатаНачала      - Дата - левая граница окна (пусто - без ограничения);
//     * ДатаОкончания   - Дата - правая граница окна (пусто - без ограничения).
//
// Возвращаемое значение:
//   РезультатЗапроса - колонки: ВидТехники, ВидРаботы, МодельТехники
//     (СХТехника - АпкМоделиСХТехники; Автотранспорт - АпкМоделиАвтотранспорта),
//     Оборудование (СХТехника - АпкМоделиСХОборудования; Автотранспорт -
//     АпкМоделиПрицепов), ПотребностьСмен, ПотребностьЧасов.
//
Функция ПотребностьПоТехкартам(Параметры) Экспорт

\tЕсли НЕ ЗначениеЗаполнено(Параметры.СценарийПланирования) Тогда
\t\tВызватьИсключение НСтр("ru = 'Не задан сценарий планирования: запрос потребности по техкартам невозможен.'");
\tКонецЕсли;

\tСуффикс = СуффиксОбъема(Параметры);

\tДатаНачала = ЗначениеПоУмолчанию(Параметры, "ДатаНачала", Дата(1, 1, 1));
\tДатаОкончания = ЗначениеПоУмолчанию(Параметры, "ДатаОкончания", Дата(3999, 12, 31));

\tУсловияМеханизированных = "М.СценарийПланирования = &СценарийПланирования
\t|\tИ М.ПериодОкончания >= &ДатаНачала
\t|\tИ М.ПериодНачала <= &ДатаОкончания";
\tУсловияТранспортных = "Тран.СценарийПланирования = &СценарийПланирования
\t|\tИ Тран.ПериодОкончания >= &ДатаНачала
\t|\tИ Тран.ПериодНачала <= &ДатаОкончания";

\tЕсли ЗначениеЗаполнено(Параметры.Организация) Тогда
\t\tУсловияМеханизированных = УсловияМеханизированных + "
\t|\tИ М.Организация = &Организация";
\t\tУсловияТранспортных = УсловияТранспортных + "
\t|\tИ Тран.Организация = &Организация";
\tКонецЕсли;

\tЕсли ЗначениеЗаполнено(Параметры.Подразделение) Тогда
\t\t// Отбор по подразделению выращивания В ИЕРАРХИИ (design 6.1):
\t\t// групповое подразделение включает дочерние.
\t\tУсловияМеханизированных = УсловияМеханизированных + "
\t|\tИ М.Подразделение В ИЕРАРХИИ(&Подразделение)";
\t\tУсловияТранспортных = УсловияТранспортных + "
\t|\tИ Тран.Подразделение В ИЕРАРХИИ(&Подразделение)";
\tКонецЕсли;

\tТекстЗапроса = "ВЫБРАТЬ
\t|\tТ.ВидТехники КАК ВидТехники,
\t|\tТ.ВидРаботы КАК ВидРаботы,
\t|\tТ.МодельТехники КАК МодельТехники,
\t|\tТ.Оборудование КАК Оборудование,
\t|\tСУММА(Т.Смен) КАК ПотребностьСмен,
\t|\tСУММА(Т.Часов) КАК ПотребностьЧасов
\t|ИЗ
\t|\t(
\t|\t\tВЫБРАТЬ
\t|\t\t\tЗНАЧЕНИЕ(Перечисление.Тх_ВидыТехники.СХТехника) КАК ВидТехники,
\t|\t\t\tМ.ВидРаботы КАК ВидРаботы,
\t|\t\t\tМ.Техника КАК МодельТехники,
\t|\t\t\tМ.Оборудование КАК Оборудование,
\t|\t\t\tМ.Смен" + Суффикс + "Оборот КАК Смен,
\t|\t\t\tМ.Часов" + Суффикс + "Оборот КАК Часов
\t|\t\tИЗ РегистрНакопления.АпкМеханизированныеРаботыПоГодовомуПлану.Обороты() КАК М
\t|\t\tГДЕ " + УсловияМеханизированных + "
\t|
\t|\t\tОБЪЕДИНИТЬ ВСЕ
\t|
\t|\t\tВЫБРАТЬ
\t|\t\t\tЗНАЧЕНИЕ(Перечисление.Тх_ВидыТехники.Автотранспорт),
\t|\t\t\tТран.ВидРаботы,
\t|\t\t\tТран.Автомобиль,
\t|\t\t\tТран.Прицеп,
\t|\t\t\tТран.Смен" + Суффикс + "Оборот,
\t|\t\t\tТран.Часов" + Суффикс + "Оборот
\t|\t\tИЗ РегистрНакопления.АпкТранспортныеРаботыПоГодовомуПлану.Обороты() КАК Тран
\t|\t\tГДЕ " + УсловияТранспортных + "
\t|\t) КАК Т
\t|СГРУППИРОВАТЬ ПО
\t|\tТ.ВидТехники,
\t|\tТ.ВидРаботы,
\t|\tТ.МодельТехники,
\t|\tТ.Оборудование";

\tПараметрыЗапроса = Новый Структура;
\tПараметрыЗапроса.Вставить("СценарийПланирования", Параметры.СценарийПланирования);
\tПараметрыЗапроса.Вставить("ДатаНачала", ДатаНачала);
\tПараметрыЗапроса.Вставить("ДатаОкончания", ДатаОкончания);
\tЕсли ЗначениеЗаполнено(Параметры.Организация) Тогда
\t\tПараметрыЗапроса.Вставить("Организация", Параметры.Организация);
\tКонецЕсли;
\tЕсли ЗначениеЗаполнено(Параметры.Подразделение) Тогда
\t\tПараметрыЗапроса.Вставить("Подразделение", Параметры.Подразделение);
\tКонецЕсли;

\tВозврат ВыполнитьЗапросАПК(ТекстЗапроса, ПараметрыЗапроса);

КонецФункции

#КонецОбласти

""".replace("\n", "\r\n")


TESTS = """#Область Тесты_ПотребностьПоТехкартам

// Тест запроса потребности по техкартам (T7, FR-003.1-2, TD-005/TD-006)
// на данных годового плана АПК («зависит от данных ИБ», SKIP при их
// отсутствии). Кросс-чек: сумма смен ПотребностьПоТехкартам должна
// совпадать с суммой релиза-001 ЗапросПотребности по тем же отборам.
//
// Возвращаемое значение:
//   Булево - Истина, если все проверки пройдены (или SKIP).
//
Функция ТестПотребностьПоТехкартам_ДемоДанные() Экспорт

\tКонтекст = НовыйКонтекстТеста("ТестПотребностьПоТехкартам_ДемоДанные");
\tСценарий = СценарийСПотребностью();

\tЕсли Сценарий = Неопределено Тогда
\t\tСообщитьПропуск(Контекст, НСтр("ru = 'нет данных годового плана АПК (техкарты)'"));
\t\tВозврат РезультатТеста(Контекст);
\tКонецЕсли;

\tПопытка
\t\tПараметры = Новый Структура;
\t\tПараметры.Вставить("СценарийПланирования", Сценарий);

\t\tПотребность = Тх_ТехникаСервер.ПотребностьПоТехкартам(Параметры).Выгрузить();

\t\tПроверить(Контекст, НСтр("ru = 'строки потребности найдены'"),
\t\t\tПотребность.Количество() > 0, Строка(Потребность.Количество()));

\t\tВсегоСмен = 0;
\t\tСтрокБезСмен = 0;
\t\tДля Каждого Стр Из Потребность Цикл
\t\t\tВсегоСмен = ВсегоСмен + Стр.ПотребностьСмен;
\t\t\tЕсли Стр.ПотребностьСмен <= 0 Тогда
\t\t\t\tСтрокБезСмен = СтрокБезСмен + 1;
\t\t\tКонецЕсли;
\t\tКонецЦикла;
\t\tПроверить(Контекст, НСтр("ru = 'все строки с положительными сменами'"),
\t\t\tСтрокБезСмен = 0, Строка(СтрокБезСмен));

\t\t// Кросс-чек с релизом-001: те же регистры, тот же сценарий, те же
\t\t// окна (по умолчанию), тот же суффикс _Вер - суммы обязаны совпасть.
\t\tЭталон = Тх_ТехникаСервер.ЗапросПотребности(Параметры).Выгрузить();
\t\tВсегоСменЭталон = 0;
\t\tДля Каждого Стр Из Эталон Цикл
\t\t\tВсегоСменЭталон = ВсегоСменЭталон + Стр.ПотребностьСмен;
\t\tКонецЦикла;
\t\tОтклонение = Макс(ВсегоСмен - ВсегоСменЭталон, ВсегоСменЭталон - ВсегоСмен);
\t\tПроверить(Контекст, НСтр("ru = 'сумма смен = сумма ЗапросПотребности (кросс-чек)'"),
\t\t\tОтклонение < 0.0001,
\t\t\tСтрока(ВсегоСмен) + " / " + Строка(ВсегоСменЭталон));
\tИсключение
\t\tПроверить(Контекст, НСтр("ru = 'выполнение без исключений'"), Ложь,
\t\t\tОписаниеОшибки());
\tКонецПопытки;

\tВозврат РезультатТеста(Контекст);

КонецФункции

// Тест фильтра потребности по «чужому» подразделению (T7, design 6.1):
// отбор В ИЕРАРХИИ по подразделению без данных должен возвращать пустой
// результат.
//
// Возвращаемое значение:
//   Булево - Истина, если все проверки пройдены (или SKIP).
//
Функция ТестПотребностьПоТехкартам_ЧужоеПодразделение() Экспорт

\tКонтекст = НовыйКонтекстТеста("ТестПотребностьПоТехкартам_ЧужоеПодразделение");
\tСценарий = СценарийСПотребностью();
\tЧужоеПодразделение = Неопределено;

\tЕсли Сценарий = Неопределено Тогда
\t\tСообщитьПропуск(Контекст, НСтр("ru = 'нет данных годового плана АПК (техкарты)'"));
\t\tВозврат РезультатТеста(Контекст);
\tКонецЕсли;

\tПопытка
\t\tЧужоеПодразделение = СоздатьЭлемент("СтруктураПредприятия");
\t\tЕсли ЧужоеПодразделение = Неопределено Тогда
\t\t\tСообщитьПропуск(Контекст, НСтр("ru = 'не удалось создать тестовое подразделение'"));
\t\tИначе
\t\t\tПараметры = Новый Структура;
\t\t\tПараметры.Вставить("СценарийПланирования", Сценарий);
\t\t\tПараметры.Вставить("Подразделение", ЧужоеПодразделение);

\t\t\tПотребность = Тх_ТехникаСервер.ПотребностьПоТехкартам(Параметры).Выгрузить();
\t\t\tПроверить(Контекст, НСтр("ru = 'по чужому подразделению - пусто'"),
\t\t\t\tПотребность.Количество() = 0, Строка(Потребность.Количество()));
\t\tКонецЕсли;
\tИсключение
\t\tПроверить(Контекст, НСтр("ru = 'выполнение без исключений'"), Ложь,
\t\t\tОписаниеОшибки());
\tКонецПопытки;

\tУдалитьСсылку(ЧужоеПодразделение);

\tВозврат РезультатТеста(Контекст);

КонецФункции

#КонецОбласти

""".replace("\n", "\r\n")


def main():
    # 1. файлы обработки
    save_sig(NPPATH.with_suffix(".xml") if False else NPPATH.parent / (NEWPROC + ".xml"), gen_processor_xml())
    save_sig(NPPATH / "Forms/Форма.xml", gen_form_meta_xml())
    save_sig(NPPATH / "Forms/Форма/Ext/Form.xml", gen_form_xml())
    save_sig(NPPATH / "Forms/Форма/Ext/Form/Module.bsl", FORM_MODULE.replace("\n", "\r\n"))
    check((NPPATH.parent / (NEWPROC + ".xml")).exists()
          and (NPPATH / "Forms/Форма/Ext/Form/Module.bsl").exists(), "1: файлы обработки созданы")

    # 2. Configuration.xml
    p = SRC / "Configuration.xml"
    t = load(p)
    line = "\t\t\t<DataProcessor>Тх_РаннерТестов</DataProcessor>\r\n"
    assert t.count(line) == 1
    t = t.replace(line, line + "\t\t\t<DataProcessor>%s</DataProcessor>\r\n" % NEWPROC, 1)
    save(p, t)
    check(NEWPROC in t, "2: Configuration ChildObjects")

    # 3. Subsystem Content
    p = SRC / "Subsystems/Тх_ПланированиеТехники.xml"
    t = load(p)
    anchor = '\t\t\t\t<xr:Item xsi:type="xr:MDObjectRef">DataProcessor.Тх_РасчетДефицита</xr:Item>\r\n'
    assert t.count(anchor) == 1
    t = t.replace(anchor, anchor + '\t\t\t\t<xr:Item xsi:type="xr:MDObjectRef">DataProcessor.%s</xr:Item>\r\n' % NEWPROC, 1)
    save(p, t)
    check(NEWPROC in t, "3: Subsystem Content")

    # 4. CommandInterface
    p = SRC / "Subsystems/Тх_ПланированиеТехники/Ext/CommandInterface.xml"
    t = load(p)
    vis_tpl = """\t\t<Command name="DataProcessor.Тх_РасчетДефицита.StandardCommand.Open">
\t\t\t<Visibility>
\t\t\t\t<xr:Common>false</xr:Common>
\t\t\t\t<xr:Value name="Role.Тх_Чтение">true</xr:Value>
\t\t\t\t<xr:Value name="Role.Тх_Редактирование">true</xr:Value>
\t\t\t</Visibility>
\t\t</Command>
""".replace("\n", "\r\n")
    assert t.count(vis_tpl) == 1, "4: visibility anchor"
    vis_new = vis_tpl.replace("Тх_РасчетДефицита", NEWPROC)
    t = t.replace(vis_tpl, vis_tpl + vis_new, 1)
    ord_tpl = """\t\t<Command name="DataProcessor.Тх_РасчетДефицита.StandardCommand.Open">
\t\t\t<CommandGroup>ActionsPanelTools</CommandGroup>
\t\t</Command>
""".replace("\n", "\r\n")
    assert t.count(ord_tpl) == 1, "4: order anchor"
    t = t.replace(ord_tpl, ord_tpl + ord_tpl.replace("Тх_РасчетДефицита", NEWPROC), 1)
    save(p, t)
    check(t.count(NEWPROC) == 2, "4: CommandInterface 2 блока")

    # 5. Roles
    for role in ["Тх_Чтение", "Тх_Редактирование"]:
        p = SRC / f"Roles/{role}/Ext/Rights.xml"
        t = load(p)
        block = """\t<object>
\t\t<name>DataProcessor.%s</name>
\t\t<right>
\t\t\t<name>Use</name>
\t\t\t<value>true</value>
\t\t</right>
\t\t<right>
\t\t\t<name>View</name>
\t\t\t<value>true</value>
\t\t</right>
\t</object>
\r\n""" % NEWPROC
        block = block.replace("\n", "\r\n")
        # Платформенная нормализация: блок перед Report.Тх_ДефицитТехники
        anchor = "\t<object>\r\n\t\t<name>Report.Тх_ДефицитТехники</name>\r\n"
        i = t.find(anchor)
        assert i > 0, f"5: anchor в {role}"
        t = t[:i] + block + t[i:]
        save(p, t)
        check(t.count(NEWPROC) == 1, f"5: {role}")

    # 6. серверный модуль
    p = P_SRV
    t = load(p)
    anchor = "#КонецОбласти\r\n\r\n#Область РасчетДефицита\r\n"
    assert t.count(anchor) == 1, "6: серверный якорь"
    t = t.replace(anchor, "#КонецОбласти\r\n\r\n" + SERVER_FUNC + "#Область РасчетДефицита\r\n", 1)
    save(p, t)
    check("ПотребностьПоТехкартам" in t, "6: ПотребностьПоТехкартам добавлена")

    # 7. тесты
    p = P_TST
    t = load(p)
    anchor = "#Область Тесты_Сцепка\r\n"
    i = t.find(anchor)
    assert i > 0, "7: якорь тестов"
    t = t[:i] + TESTS + t[i:]
    save(p, t)
    check("ТестПотребностьПоТехкартам_ДемоДанные" in t
          and "ТестПотребностьПоТехкартам_ЧужоеПодразделение" in t, "7: +2 теста")

    # 8. раннер
    p = P_RUN
    t = load(p)
    t = t.replace("все 13 тестов", "все 15 тестов")
    t = t.replace("\tЗапуститьТестДоступноСменЗамещениеНеЗадан(Результаты);\r\n",
                  "\tЗапуститьТестДоступноСменЗамещениеНеЗадан(Результаты);\r\n"
                  "\tЗапуститьТестПотребностьПоТехкартамДемоДанные(Результаты);\r\n"
                  "\tЗапуститьТестПотребностьПоТехкартамЧужоеПодразделение(Результаты);\r\n", 1)
    wraps = ""
    for test, wrap in [("ТестПотребностьПоТехкартам_ДемоДанные", "ЗапуститьТестПотребностьПоТехкартамДемоДанные"),
                       ("ТестПотребностьПоТехкартам_ЧужоеПодразделение", "ЗапуститьТестПотребностьПоТехкартамЧужоеПодразделение")]:
        wraps += '''// Обёртка вызова теста %s.
//
Процедура %s(Результаты)

\tИмяТеста = "%s";
\tНачалоТеста = ТекущаяУниверсальнаяДатаВМиллисекундах();
\tПрошёл = Ложь;
\tПопытка
\t\tПрошёл = Тх_Тесты.%s();
\tИсключение
\t\tПрошёл = Ложь;
\t\tСообщитьОбИсключенииТеста(ИмяТеста, ОписаниеОшибки());
\tКонецПопытки;
\tЗафиксироватьРезультат(Результаты, ИмяТеста, Прошёл, НачалоТеста);

КонецПроцедуры

''' % (test, wrap, test, test)
    tail = "#КонецОбласти\r\n"
    i = t.rfind(tail)
    t = t[:i] + wraps.replace("\n", "\r\n") + t[i:]
    n_calls = len(re.findall(r"^\tЗапуститьТест\w+\(Результаты\);", t, re.M))
    check(n_calls == 15, f"8: раннер вызывает {n_calls} тестов (15)")
    save(p, t)

    # 9. run_unit_tests.py
    t = P_UT.read_text(encoding="utf-8")
    t = t.replace("all 13 tests", "all 15 tests").replace("total != 13", "total != 15")
    P_UT.write_text(t, encoding="utf-8", newline="")
    check("total != 15" in t, "9: run_unit_tests.py 15")

    print("RESULT:", "PASS" if ok_all else "FAIL")
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
