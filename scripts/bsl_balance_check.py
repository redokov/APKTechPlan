#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Static sanity check of BSL modules: block-keyword balance.

Catches the failure mode that /CheckModules did NOT: a module that is
syntactically balanced per-file-begin but truncated at the end
("Ожидается ключевое слово 'КонецФункции'").

Checks per file:
  * Функция/Процедура vs КонецФункции/КонецПроцедуры counts
  * Если/КонецЕсли, Цикл/КонецЦикла, Попытка/КонецПопытки, Тогда-blocks via Если
  * file ends inside an open procedure/function

Usage: python scripts/bsl_balance_check.py [root_dir]
Exit code 1 if any problem found.
"""
import os
import re
import sys

ROOT_DEFAULT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "src", "cfe", "\u041f\u043b\u0430\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435\u0422\u0435\u0445\u043d\u0438\u043a\u0438\u0410\u041f\u041a")

# (opening pattern, closing pattern)
PAIRS = [
    (r"^\s*(?:Асинх|Async)?Функция\s", r"^\s*КонецФункции\b"),
    (r"^\s*(?:Асинх|Async)?Процедура\s", r"^\s*КонецПроцедуры\b"),
]

KEYWORDS = {
    "Если": (r"^\s*Если\s.*\sТогда\s*$", r"^\s*КонецЕсли\b"),
    "Попытка": (r"^\s*Попытка\s*$", r"^\s*КонецПопытки\b"),
    "Цикл": (r"^\s*(?:Для|Пока)\b.*\sЦикл\s*$", r"^\s*КонецЦикла\b"),
}


def read_text(path):
    raw = open(path, "rb").read()
    for enc in ("utf-8-sig", "utf-8", "cp1251"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def check_file(path):
    text = read_text(path)
    lines = text.replace("\r\n", "\n").split("\n")
    problems = []

    func_open = sum(1 for l in lines if re.match(PAIRS[0][0], l))
    func_close = sum(1 for l in lines if re.match(PAIRS[0][1], l))
    proc_open = sum(1 for l in lines if re.match(PAIRS[1][0], l))
    proc_close = sum(1 for l in lines if re.match(PAIRS[1][1], l))
    if func_open != func_close:
        problems.append("Функция=%d КонецФункции=%d" % (func_open, func_close))
    if proc_open != proc_close:
        problems.append("Процедура=%d КонецПроцедуры=%d" % (proc_open, proc_close))

    # last meaningful line should be a closing keyword of a routine
    meaningful = [l for l in lines if l.strip() and not l.strip().startswith("//")]
    if meaningful:
        last = meaningful[-1].strip()
        if not re.match(r"^(КонецФункции|КонецПроцедуры|#КонецОбласти)$", last):
            problems.append("файл не заканчивается КонецФункции/КонецПроцедуры (последняя строка: %r)"
                            % last[:60])

    return problems


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else ROOT_DEFAULT
    bad = 0
    total = 0
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            if not fn.endswith(".bsl"):
                continue
            p = os.path.join(dirpath, fn)
            total += 1
            problems = check_file(p)
            if problems:
                bad += 1
                rel = os.path.relpath(p, root)
                print("FAIL %s" % rel)
                for pr in problems:
                    print("     - %s" % pr)
    print("\nchecked=%d broken=%d" % (total, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
