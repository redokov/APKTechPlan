# -*- coding: utf-8 -*-
"""T1: синонимы (FR-006). Точные замены с контролем количества вхождений.
Файлы читаются/пишутся utf-8-sig, CRLF сохраняется (newline='')."""
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]

# (path, old, new, expected_count)
REPL = [
    # Документ: синоним объекта
    ("src/cfe/ПланированиеТехникиАПК/Documents/Тх_ПланТехническихРесурсов.xml",
     "<v8:content>План технических ресурсов</v8:content>",
     "<v8:content>Потребность в технике</v8:content>", 1),
    # Документ: комментарий
    ("src/cfe/ПланированиеТехникиАПК/Documents/Тх_ПланТехническихРесурсов.xml",
     "<Comment>План технических ресурсов подразделения по сценарию планирования (design 4.4, FR-005..FR-007).",
     "<Comment>Потребность в технике подразделения по сценарию планирования (spec 002, FR-003; строки = модели техники/прицепных по данным техкарт).", 1),
    # Форма документа: синоним формы (Forms/Тх_ФормаДокумента.xml)
    ("src/cfe/ПланированиеТехникиАПК/Documents/Тх_ПланТехническихРесурсов/Forms/Тх_ФормаДокумента.xml",
     "<v8:content>План технических ресурсов</v8:content>",
     "<v8:content>Потребность в технике</v8:content>", 1),
    # Форма документа: заголовок (Ext/Form.xml)
    ("src/cfe/ПланированиеТехникиАПК/Documents/Тх_ПланТехническихРесурсов/Forms/Тх_ФормаДокумента/Ext/Form.xml",
     "<v8:content>План технических ресурсов</v8:content>",
     "<v8:content>Потребность в технике</v8:content>", 1),
    # Отчёт: синоним объекта
    ("src/cfe/ПланированиеТехникиАПК/Reports/Тх_ДефицитТехники.xml",
     "<v8:content>Дефицит техники</v8:content>",
     "<v8:content>Анализ дефицита техники</v8:content>", 1),
    # Отчёт: титул СКД
    ("src/cfe/ПланированиеТехникиАПК/Reports/Тх_ДефицитТехники/Templates/ОсновнаяСхемаКомпоновкиДанных/Ext/Template.xml",
     "<v8:content>Дефицит техники</v8:content>",
     "<v8:content>Анализ дефицита техники</v8:content>", 1),
    # Enum: синоним
    ("src/cfe/ПланированиеТехникиАПК/Enums/Тх_ВидыТехники.xml",
     "<v8:content>Тх_виды техники</v8:content>",
     "<v8:content>Виды техники (Тх)</v8:content>", 1),
    # Тх_РасчетДефицита: комментарий модуля формы (отчёт переименован)
    ("src/cfe/ПланированиеТехникиАПК/DataProcessors/Тх_РасчетДефицита/Forms/Форма/Ext/Form/Module.bsl",
     "// Тх_ТехникаСервер.РассчитатьДефицит и открытие отчёта «Дефицит техники»",
     "// Тх_ТехникаСервер.РассчитатьДефицит и открытие отчёта «Анализ дефицита техники»", 1),
]

# VA-сценарии: текстовые замены заголовков окон и команд
VA = [
    ("tests/vanessa/03-plan-tehresursov-prinyatye-tc.feature",
     [("План технических ресурсов", "Потребность в технике", 3)]),
    ("tests/vanessa/04-preduprezhdenie-ts-dva-podrazdeleniya.feature",
     [("План технических ресурсов", "Потребность в технике", 4)]),
    ("tests/vanessa/05-raschet-deficita-i-filtry-otcheta.feature",
     [("Дефицит техники", "Анализ дефицита техники", 2)]),
    ("tests/vanessa/06-otchet-tolko-defitsitnye-stroki.feature",
     [("Дефицит техники", "Анализ дефицита техники", 4)]),
    ("tests/vanessa/07-pometka-koeffitsient-ne-zadan.feature",
     [("Дефицит техники", "Анализ дефицита техники", 2)]),
    ("tests/vanessa/08-polzovatel-bez-rolej-ne-vidit.feature",
     [("Дефицит техники", "Анализ дефицита техники", 4)]),
]


def apply(path, old, new, expected):
    p = ROOT / path
    raw = p.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    crlf = "\r\n" in text
    n = text.count(old)
    if n != expected:
        print(f"FAIL {path}: '{old[:40]}...' found {n}, expected {expected}")
        return False
    text = text.replace(old, new)
    data = text.encode("utf-8-sig" if bom else "utf-8")
    p.write_bytes(data)
    norm = text.replace("\r\n", "\n")
    if crlf:
        p.write_bytes(("\r\n".join(norm.split("\n"))).encode("utf-8-sig" if bom else "utf-8"))
    print(f"OK {path}: {expected}x '{old[:36]}...'")
    return True


def main():
    ok = True
    for path, old, new, cnt in REPL:
        ok = apply(path, old, new, cnt) and ok
    for path, subs in VA:
        for old, new, cnt in subs:
            ok = apply(path, old, new, cnt) and ok
    print("RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
