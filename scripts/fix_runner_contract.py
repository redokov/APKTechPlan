# -*- coding: utf-8 -*-
"""Fix runner/form result contract (spec-003 safe lane, review P0-1/P1-6).

Changes (GATE-01 manifest: 4 files, all in the approved CFE scope):
1. Form/Module.bsl (full rewrite): consume Статус + Провалы instead of the
   missing Результат.Прошёл; show PASS/FAIL/SKIP distinctly; summary message
   with separate counters, no terminal SKIP verdict; remove stale "15" wording.
2. ObjectModule.bsl: fix stale Прошёл docs; exception path passes
   Неопределено to ЗафиксироватьРезультат (existing FAIL contract, no new
   exception schema); remove dead Прошёл variable from all 20 wrappers.
3. Тх_Тесты/Module.bsl: derive FAIL from Провалы in РезультатТеста;
   skip branches return the result structure instead of Булево; fix stale
   "Возвращаемое значение: Булево" docs on export tests.
4. Form.xml: remove stale "15 модульных тестов" tooltip wording.

Preserves UTF-8 BOM and CRLF. ASCII-only console output. Aborts without
writing if any expected pattern count mismatches.
"""
import io
import re
import sys

BASE = r"C:\MyProjects\APKTechPlan\src\cfe\ПланированиеТехникиАПК"
FORM_MODULE = BASE + r"\DataProcessors\Тх_РаннерТестов\Forms\Форма\Ext\Form\Module.bsl"
OBJ_MODULE = BASE + r"\DataProcessors\Тх_РаннерТестов\Ext\ObjectModule.bsl"
TESTS_MODULE = BASE + r"\CommonModules\Тх_Тесты\Ext\Module.bsl"
FORM_XML = BASE + r"\DataProcessors\Тх_РаннерТестов\Forms\Форма\Ext\Form.xml"

CRLF = "\r\n"


def read(path):
    with io.open(path, "r", encoding="utf-8-sig", newline="") as f:
        return f.read()


def write(path, text):
    with io.open(path, "w", encoding="utf-8-sig", newline="") as f:
        f.write(text)


def replace_counted(text, old, new, expected, label):
    got = text.count(old)
    if got != expected:
        print("ABORT %s: expected %d, found %d" % (label, expected, got))
        sys.exit(1)
    return text.replace(old, new)


def main():
    # ---------- 1. Form/Module.bsl: full rewrite ----------
    form_lines = [
        u"// Модуль формы обработки «Тх_РаннерТестов» (design §11, задача A11).",
        u"//",
        u"// Запуск тестов - только по команде «Выполнить тесты» (ПриСозданииНаСервере",
        u"// автозапуска нет): серверный вызов, таблица результатов, итоговое",
        u"// немодальное сообщение с раздельными счётчиками PASS/FAIL/SKIP.",
        u"// Терминальный вердикт прогона и политика SKIP в форме не решаются (Q-007).",
        u"",
        u"#Область ОбработчикиКомандФормы",
        u"",
        u"// Команда «Выполнить тесты»: серверный прогон всех тестов Тх_Тесты,",
        u"// заполнение таблицы результатов и вывод итоговой сводки.",
        u"//",
        u"// Параметры:",
        u"//   Команда - КомандаФормы - команда формы.",
        u"//",
        u"&НаКлиенте",
        u"Процедура ВыполнитьТесты(Команда)",
        u"",
        u"\tСообщение = Новый СообщениеПользователю;",
        u"\tСообщение.Текст = ВыполнитьТестовНаСервере();",
        u"\tСообщение.Сообщить();",
        u"",
        u"КонецПроцедуры",
        u"",
        u"#КонецОбласти",
        u"",
        u"#Область СлужебныеПроцедурыИФункции",
        u"",
        u"// Выполняет все тесты модульного прогона на сервере, заполняет таблицу",
        u"// результатов формы и возвращает сводку прогона.",
        u"//",
        u"// Потребляет контракт раннера: Статус (\"PASS\"/\"FAIL\"/\"SKIP\") и Провалы",
        u"// каждого результата; счётчики PASS/FAIL/SKIP раздельны.",
        u"//",
        u"// Возвращаемое значение:",
        u"//   Строка - сводка прогона: всего тестов и раздельные счётчики.",
        u"//",
        u"&НаСервере",
        u"Функция ВыполнитьТестовНаСервере()",
        u"",
        u"\tРезультатыЗапуска = Обработки.Тх_РаннерТестов.Создать().ВыполнитьТесты();",
        u"",
        u"\tРезультаты.Очистить();",
        u"\tПрошло = 0;",
        u"\tПровалено = 0;",
        u"\tПропущено = 0;",
        u"",
        u"\tДля Каждого Результат Из РезультатыЗапуска Цикл",
        u"\t\tСтрокаРезультата = Результаты.Добавить();",
        u"\t\tСтрокаРезультата.Тест = Результат.Имя;",
        u"\t\tСтрокаРезультата.Результат = ПредставлениеСтатуса(",
        u"\t\t\tРезультат.Статус, Результат.Провалы);",
        u"\t\tЕсли Результат.Статус = \"PASS\" Тогда",
        u"\t\t\tПрошло = Прошло + 1;",
        u"\t\tИначеЕсли Результат.Статус = \"FAIL\" Тогда",
        u"\t\t\tПровалено = Провалено + 1;",
        u"\t\tИначеЕсли Результат.Статус = \"SKIP\" Тогда",
        u"\t\t\tПропущено = Пропущено + 1;",
        u"\t\tКонецЕсли;",
        u"\tКонецЦикла;",
        u"",
        u"\tВсегоТестов = Результаты.Количество();",
        u"",
        u"\tВозврат СтрШаблон(НСтр(\"ru = 'Тестов: %1. PASS: %2, FAIL: %3, SKIP: %4.'\"),",
        u"\t\tВсегоТестов, Прошло, Провалено, Пропущено);",
        u"",
        u"КонецФункции",
        u"",
        u"// Возвращает представление статуса теста для колонки «Результат»:",
        u"// статусы PASS/FAIL/SKIP различимы; для FAIL добавляется число",
        u"// проваленных проверок из Провалов.",
        u"//",
        u"// Параметры:",
        u"//   Статус  - Строка - статус теста из результата прогона;",
        u"//   Провалы - Массив - имена проваленных проверок.",
        u"//",
        u"// Возвращаемое значение:",
        u"//   Строка - отображаемое представление статуса.",
        u"//",
        u"Функция ПредставлениеСтатуса(Статус, Провалы)",
        u"",
        u"\tЕсли Статус = \"FAIL\" И Провалы.Количество() > 0 Тогда",
        u"\t\tВозврат СтрШаблон(НСтр(\"ru = 'FAIL (провалов проверок: %1)'\"),",
        u"\t\t\tПровалы.Количество());",
        u"\tКонецЕсли;",
        u"",
        u"\tВозврат Статус;",
        u"",
        u"КонецФункции",
        u"",
        u"#КонецОбласти",
        u"",
    ]
    form_new = CRLF.join(form_lines)

    # ---------- 2. ObjectModule.bsl ----------
    om = read(OBJ_MODULE)

    # 2a. Doc of ВыполнитьТесты: actual structure Имя, Статус, ДлительностьМс, Провалы.
    om = replace_counted(
        om,
        u"//     * Прошёл         - Булево - результат (Истина для SKIP-пропусков);" + CRLF
        + u"//     * ДлительностьМс - Число - длительность выполнения, миллисекунды.",
        u"//     * Статус         - Строка - статус теста: \"PASS\", \"FAIL\" или \"SKIP\";" + CRLF
        + u"//     * ДлительностьМс - Число - длительность выполнения, миллисекунды;" + CRLF
        + u"//     * Провалы        - Массив - имена проваленных проверок (пустой для PASS и SKIP).",
        1, "OM doc VypolnitTesty")

    # 2b. Doc of ЗафиксироватьРезультат: replace both stale blocks (regex span).
    om_pat = re.compile(
        u"// Фиксирует результат одного теста с длительностью выполнения\\." + CRLF
        + u"//" + CRLF
        + u"(?:.|" + CRLF + ")*?"
        + u"(?=" + CRLF + u"Процедура ЗафиксироватьРезультат)")
    if len(om_pat.findall(om)) != 1:
        print("ABORT OM doc ZafiksirovatResultat: span count %d" % len(om_pat.findall(om)))
        sys.exit(1)
    om_new_doc = (
        u"// Фиксирует результат одного теста с длительностью выполнения." + CRLF
        + u"//" + CRLF
        + u"// Параметры:" + CRLF
        + u"//   Результаты          - Массив - накапливаемые результаты прогона;" + CRLF
        + u"//   ИмяТеста            - Строка - имя теста;" + CRLF
        + u"//   СтруктураРезультата - Структура, Неопределено - результат теста" + CRLF
        + u"//                         (Статус \"PASS\"/\"FAIL\"/\"SKIP\", Провалы);" + CRLF
        + u"//                         Неопределено - тест упал с необработанным" + CRLF
        + u"//                         исключением (фиксируется как FAIL);" + CRLF
        + u"//   НачалоТеста         - Число - момент старта теста (универсальное время, мс)." + CRLF
        + u"//")
    om = om_pat.sub(lambda m: om_new_doc, om, count=1)

    # 2c. Wrappers: dead Прошёл var -> РезультатТеста = Неопределено (20x each).
    om = replace_counted(
        om,
        u"\tПрошёл = Ложь;" + CRLF + u"\tПопытка" + CRLF,
        u"\tРезультатТеста = Неопределено;" + CRLF + u"\tПопытка" + CRLF,
        20, "OM wrapper pre-Popytka")
    om = replace_counted(
        om,
        u"\tИсключение" + CRLF + u"\t\tПрошёл = Ложь;" + CRLF + u"\t\tСообщитьОбИсключенииТеста(",
        u"\tИсключение" + CRLF + u"\t\tРезультатТеста = Неопределено;" + CRLF
        + u"\t\tСообщитьОбИсключенииТеста(",
        20, "OM wrapper exception")

    if u"Прошёл" in om:
        print("ABORT OM: stale 'Proshel' still present")
        sys.exit(1)

    # ---------- 3. Тх_Тесты/Ext/Module.bsl ----------
    tm = read(TESTS_MODULE)

    # 3a. Header: structure contract instead of Boolean.
    tm = replace_counted(
        tm,
        u"//  - возвращает Булево: Истина - все проверки пройдены (или SKIP)." + CRLF,
        u"//  - возвращает структуру результата (Имя, Статус, Провалы): Статус" + CRLF
        + u"//    \"PASS\"/\"FAIL\"/\"SKIP\" (SKIP - нет данных ИБ), Провалы - имена" + CRLF
        + u"//    проваленных проверок; терминальная политика SKIP для прогона" + CRLF
        + u"//    здесь не решается." + CRLF,
        1, "TM header")

    # 3b. РезультатТеста: derive FAIL from Провалы; fix doc.
    tm_old_rez = (
        u"// Возвращает итог теста: Истина - провалов нет." + CRLF
        + u"//" + CRLF
        + u"// Параметры:" + CRLF
        + u"//   СтруктураТеста - Структура - контекст теста." + CRLF
        + u"//" + CRLF
        + u"// Возвращаемое значение:" + CRLF
        + u"//   Булево - результат теста." + CRLF
        + u"//" + CRLF
        + u"Функция РезультатТеста(СтруктураТеста)" + CRLF
        + CRLF
        + u"\tВозврат СтруктураТеста;" + CRLF
        + CRLF
        + u"КонецФункции")
    tm_new_rez = (
        u"// Возвращает итоговый контекст теста. Если есть проваленные проверки," + CRLF
        + u"// статус FAIL (провал не маскируется ранее выставленным SKIP);" + CRLF
        + u"// иначе сохранённый статус: PASS или SKIP." + CRLF
        + u"//" + CRLF
        + u"// Параметры:" + CRLF
        + u"//   СтруктураТеста - Структура - контекст теста." + CRLF
        + u"//" + CRLF
        + u"// Возвращаемое значение:" + CRLF
        + u"//   Структура - Имя (Строка), Статус (\"PASS\"/\"FAIL\"/\"SKIP\"), Провалы (Массив)." + CRLF
        + u"//" + CRLF
        + u"Функция РезультатТеста(СтруктураТеста)" + CRLF
        + CRLF
        + u"\tЕсли СтруктураТеста.Провалы.Количество() > 0 Тогда" + CRLF
        + u"\t\tСтруктураТеста.Статус = \"FAIL\";" + CRLF
        + u"\tКонецЕсли;" + CRLF
        + CRLF
        + u"\tВозврат СтруктураТеста;" + CRLF
        + CRLF
        + u"КонецФункции")
    tm = replace_counted(tm, tm_old_rez, tm_new_rez, 1, "TM RezultatTesta")

    # 3c. Skip branches: return the structure, not Boolean (5x).
    tm = replace_counted(
        tm,
        u"СообщитьПропуск(Контекст, НСтр(\"ru = 'нет каталогов моделей АПК'\"));" + CRLF
        + u"\t\t\tВозврат Истина;",
        u"СообщитьПропуск(Контекст, НСтр(\"ru = 'нет каталогов моделей АПК'\"));" + CRLF
        + u"\t\t\tВозврат РезультатТеста(Контекст);",
        5, "TM skip-branch return")
    if tm.count(u"Возврат Истина;") != 1:
        print("ABORT TM: Vozvrat Istina count %d (expected 1, TablitsyIdentichny)" % tm.count(u"Возврат Истина;"))
        sys.exit(1)

    # 3d. Stale export-test doc lines (17 + 2 + 1 = 20).
    new_doc = u"//   Структура - результат теста: Имя, Статус (\"PASS\"/\"FAIL\"/\"SKIP\"), Провалы."
    tm = replace_counted(
        tm, u"//   Булево - Истина, если все проверки пройдены (или SKIP).",
        new_doc, 17, "TM doc 'vse proverki (ili SKIP)'")
    tm = replace_counted(
        tm, u"//   Булево - Истина, если проверки пройдены (или SKIP).",
        new_doc, 2, "TM doc 'proverki (ili SKIP)'")
    tm = replace_counted(
        tm, u"//   Булево - Истина, если все проверки пройдены.",
        new_doc, 1, "TM doc 'vse proverki'")

    # ---------- 4. Form.xml tooltip ----------
    fx = read(FORM_XML)
    fx = replace_counted(
        fx,
        u"<v8:content>Последовательно выполняет 15 модульных тестов общего модуля Тх_Тесты</v8:content>",
        u"<v8:content>Последовательно выполняет все модульные тесты общего модуля Тх_Тесты</v8:content>",
        1, "Form.xml tooltip")

    # ---------- write all (only after every count check passed) ----------
    write(FORM_MODULE, form_new)
    write(OBJ_MODULE, om)
    write(TESTS_MODULE, tm)
    write(FORM_XML, fx)

    # ---------- post-verify ----------
    for path in (FORM_MODULE, OBJ_MODULE, TESTS_MODULE, FORM_XML):
        raw = io.open(path, "rb").read()
        if not raw.startswith(b"\xef\xbb\xbf"):
            print("ABORT: BOM lost in %s" % path)
            sys.exit(1)
        if b"\r\n" not in raw:
            print("ABORT: CRLF lost in %s" % path)
            sys.exit(1)
    chk = read(OBJ_MODULE) + read(TESTS_MODULE) + read(FORM_MODULE) + read(FORM_XML)
    if u"из 15" in chk or u"15 модульных" in chk or u"Результат.Прошёл" in chk:
        print("ABORT: stale wording still present")
        sys.exit(1)
    print("OK: all replacements applied; BOM/CRLF preserved; no stale wording left")
    print("files changed: 4 (Form/Module.bsl, ObjectModule.bsl, Tkh_Testy Module.bsl, Form.xml)")


if __name__ == "__main__":
    main()
