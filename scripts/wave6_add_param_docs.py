# -*- coding: utf-8 -*-
"""Insert '// Параметры:' doc blocks into Tkh_TestRunner wrapper procedures.

Finds comment headers of the form:
    // Обёртка вызова теста <Name>.
    //
    Процедура ЗапуститьТест<...>(Результаты)
and inserts the standard parameter block before the Процедура line if the
header does not already contain a '// Параметры:' section.

Preserves the original line endings (CRLF/LF) of the file.
"""
import io
import re
import sys

PARAM_BLOCK = (
    "//\n"
    "// Параметры:\n"
    "//   Результаты - Массив - накапливаемые результаты прогона: элементы\n"
    "//                Структура (Имя, Статус, ДлительностьМс, Провалы, Детали).\n"
    "//\n"
)

PATTERN = re.compile(
    r"(// Обёртка вызова теста [^\n]*\.\n)(//\n)(Процедура ЗапуститьТест[^\n]*\(Результаты\))"
)


def main(path: str) -> int:
    with io.open(path, "rb") as f:
        raw = f.read()
    crlf = raw.count(b"\r\n")
    lf_only = raw.count(b"\n") - crlf
    eol = "\r\n" if crlf >= lf_only else "\n"
    text = raw.decode("utf-8-sig").replace("\r\n", "\n")

    count = 0

    def repl(m: "re.Match[str]") -> str:
        nonlocal count
        count += 1
        return m.group(1) + PARAM_BLOCK + m.group(3)

    new_text = PATTERN.sub(repl, text)
    if count == 0:
        print("no matches")
        return 1
    out = new_text.replace("\n", eol)
    with io.open(path, "wb") as f:
        f.write(b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b"")
        f.write(out.encode("utf-8"))
    print("inserted blocks: %d (eol=%r)" % (count, eol))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
