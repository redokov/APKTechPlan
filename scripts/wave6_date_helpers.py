# -*- coding: utf-8 -*-
"""Wave 6 item 6: date helpers in Тх_Тests module.

1. Simplify each date helper body:
       Год = G; Месяц = M; День = D; Возврат Дата(Год, Месяц, День);
   ->  Возврат Дата(G, M, D);
   (Дата() constructor literals do not trigger MagicNumber).
2. Rename ДатаДвадцатоеДекабря2098 -> ДатаДвадцатогоДекабря2098
   (unified genitive naming template).
3. Move the block of 15 date helpers from the tail of region
   «Инфраструктура» into a new region «ТестовыеКонстанты» placed
   right after Инфраструктура (before Тесты_ДатыИФункции).

Preserves CRLF/LF and BOM.
"""
import io
import re
import sys

SRC = "src/cfe/ПланированиеТехникиАПК/CommonModules/Тх_Тесты/Ext/Module.bsl"

BODY_RE = re.compile(
    r"(Функция Дата\w+\(\)\n\n)"
    r"\tГод = (\d+);\n"
    r"\tМесяц = (\d+);\n"
    r"\tДень = (\d+);\n"
    r"\tВозврат Дата\(Год, Месяц, День\);\n"
)

START_MARK = "// Возвращает дату 31 декабря 1999 года."
END_RE = re.compile(
    r"Функция ДатаДесятогоФевраля2099\(\)\n\n\t[^\n]*\n\nКонецФункции\n"
)
NEXT_REGION = "#Область Тесты_ДатыИФункции"

OLD_NAME = "ДатаДвадцатоеДекабря2098"
NEW_NAME = "ДатаДвадцатогоДекабря2098"


def main() -> int:
    with io.open(SRC, "rb") as f:
        raw = f.read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    crlf = raw.count(b"\r\n")
    lf_only = raw.count(b"\n") - crlf
    eol = "\r\n" if crlf >= lf_only else "\n"
    text = raw.decode("utf-8-sig").replace("\r\n", "\n")

    # 1. simplify bodies
    n_bodies = 0

    def body_repl(m):
        nonlocal n_bodies
        n_bodies += 1
        return m.group(1) + "\tВозврат Дата(%s, %s, %s);\n\n" % (
            m.group(2), m.group(3), m.group(4))

    text = BODY_RE.sub(body_repl, text)
    if n_bodies == 0:
        print("no bodies matched")
        return 1

    # 2. rename helper
    n_ren = text.count(OLD_NAME)
    text = text.replace(OLD_NAME, NEW_NAME)

    # 3. move date-helper block into new region
    start = text.index(START_MARK)
    func_start = text.index("Функция ДатаДесятогоФевраля2099")
    end = text.index("КонецФункции\n", func_start) + len("КонецФункции\n")
    block = text[start:end]
    text = text[:start] + text[end:]
    # collapse blank lines left behind at the cut point
    while "\n\n\n\n" in text:
        text = text.replace("\n\n\n\n", "\n\n")

    region = (
        "#Область ТестовыеКонстанты\n"
        "// Тестовые даты-константы сценариев (единый шаблон имени ДатаХхх).\n\n"
        + block
        + "\n#КонецОбласти\n\n"
    )
    text = text.replace(NEXT_REGION, region + NEXT_REGION, 1)

    out = text.replace("\n", eol)
    with io.open(SRC, "wb") as f:
        if bom:
            f.write(b"\xef\xbb\xbf")
        f.write(out.encode("utf-8"))
    print("bodies simplified: %d; renamed %s -> %s (%d refs)"
          % (n_bodies, OLD_NAME, NEW_NAME, n_ren))
    return 0


if __name__ == "__main__":
    sys.exit(main())
