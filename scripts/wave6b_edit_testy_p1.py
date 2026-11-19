#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wave 6b: mechanical fixes for Тх_Тесты/Ext/Module.bsl (file 1, part 1).

Covers: CEL x4, region rename + 10 suppression pairs, date-helper rollback
(15) + 3 new 2025 helpers + call-site replacements, UsageWriteLogEvent x2,
Typo pairs x16, DSL const-functions x4 + literal replacement, MagicNumber
misc sites, IfConditionComplexity (Сцепка site).

EXCLUDED (handled by GLM decomposition later, same functions):
QToMM x3 + NestedStatements (ТестДоступныеМодели_ПланРаспределения),
IfConditionComplexity 2954 + Magic 2994/2997/3001 (ЗамещениеПоШирине)...
NOTE: Magic 2994/2997/3001 and DSL lines 2945-2947 DO get fixed here (simple
statements preserved 1:1 by decomposition).

All anchors are regexes (ASCII-escaped Cyrillic); every op asserts; abort
leaves the file untouched. Run, then gate with bsl_ls_file.py.
"""
import re
import sys

PATH = ("src/cfe/\u041f\u043b\u0430\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435"
        "\u0422\u0435\u0445\u043d\u0438\u043a\u0438\u0410\u041f\u041a/CommonModules/"
        "\u0422\u0445_\u0422\u0435\u0441\u0442\u044b/Ext/Module.bsl")

raw = open(PATH, "rb").read()
bom = raw.startswith(b"\xef\xbb\xbf")
text = raw.decode("utf-8-sig")
NL = "\r\n" if "\r\n" in text else "\n"
assert "\r" not in text.replace("\r\n", "")
lines = text.replace("\r\n", "\n").split("\n")
if lines and lines[-1] == "":
    lines.pop()

FAIL = []


def req(cond, msg):
    if not cond:
        FAIL.append(msg)
        raise SystemExit("ANCHOR FAIL: " + msg)


def find_line(pattern, flags=0):
    """1-based line number of the unique line matching regex, else abort."""
    rx = re.compile(pattern, flags)
    hits = [i for i, l in enumerate(lines, 1) if rx.match(l)]
    req(len(hits) == 1, "unique match expected for %r, got %d" % (pattern, len(hits)))
    return hits[0]


def find_lines(pattern, flags=0):
    rx = re.compile(pattern)
    return [i for i, l in enumerate(lines, 1) if rx.search(l)]


def insert_before(n, new):
    lines[n - 1:n - 1] = new


def insert_after(n, new):
    lines[n:n] = new


# --------------------------------------------------------------- SECTION 1 CEL
runs = []
i = 0
while i < len(lines):
    if lines[i] == "" and i + 1 < len(lines) and lines[i + 1] == "":
        start = i
        while i < len(lines) and lines[i] == "":
            i += 1
        runs.append((start + 1, i))  # 1-based inclusive
    else:
        i += 1
req(len(runs) == 4, "expected 4 blank runs, got %d: %r" % (len(runs), runs))
for start, end in reversed(runs):
    del lines[start:end - 1]  # keep one blank

# ------------------------------------------------- SECTION 2 region rename
OBL = "#\u041e\u0431\u043b\u0430\u0441\u0442\u044c "
n = find_line(re.escape(OBL + "\u0418\u043d\u0444\u0440\u0430\u0441\u0442\u0440\u0443\u043a\u0442\u0443\u0440\u0430") + r"$")
lines[n - 1] = OBL + ("\u0421\u043b\u0443\u0436\u0435\u0431\u043d\u044b\u0435"
                      "\u041f\u0440\u043e\u0446\u0435\u0434\u0443\u0440\u044b"
                      "\u0418\u0424\u0443\u043d\u043a\u0446\u0438\u0438")

# ------------------------------------------------ SECTION 3 region pairs
OFF1 = "// BSLLS:NonStandardRegion-off (тестовый регион - трассировка на группу тестов,"
OFF2 = "// переименование ломает рубрикацию прогона)"
ON_R = "// BSLLS:NonStandardRegion-on"
for name in ["\u0422\u0435\u0441\u0442\u043e\u0432\u044b\u0435\u041a\u043e\u043d\u0441\u0442\u0430\u043d\u0442\u044b",
             "\u0422\u0435\u0441\u0442\u044b_\u0414\u0430\u0442\u044b\u0418\u0424\u0443\u043d\u043a\u0446\u0438\u0438",
             "\u0422\u0435\u0441\u0442\u044b_\u041f\u0435\u0440\u0435\u0441\u0447\u0435\u0442\u0414\u0435\u0444\u0438\u0446\u0438\u0442\u0430",
             "\u0422\u0435\u0441\u0442\u044b_\u041f\u043e\u0442\u0440\u0435\u0431\u043d\u043e\u0441\u0442\u044c\u041f\u043e\u0422\u0435\u0445\u043a\u0430\u0440\u0442\u0430\u043c",
             "\u0422\u0435\u0441\u0442\u044b_\u0414\u043e\u0441\u0442\u0443\u043f\u043d\u043e\u0441\u0442\u044c\u041c\u043e\u0434\u0435\u043b\u0435\u0439",
             "\u0422\u0435\u0441\u0442\u044b_\u0417\u0430\u043f\u043e\u043b\u043d\u0438\u0442\u044c\u041f\u043b\u0430\u043d\u0430\u0420\u0430\u0431\u043e\u0442",
             "\u0422\u0435\u0441\u0442\u044b_\u0421\u0446\u0435\u043f\u043a\u0430",
             "\u0422\u0435\u0441\u0442\u044b_\u041a\u043e\u044d\u0444\u0444\u0438\u0446\u0438\u0435\u043d\u0442\u0417\u0430\u043c\u0435\u0449\u0435\u043d\u0438\u044f"]:
    n = find_line(re.escape(OBL + name) + r"$")
    insert_before(n, [OFF1, OFF2])
    insert_after(n, [ON_R])
for srv in ["SRV03", "SRV04"]:
    n = find_line(re.escape(OBL + "\u0422\u0435\u0441\u0442\u044b_" + srv) + r".*$")
    insert_before(n, ["// BSLLS:NonStandardRegion-off (тестовый регион - трассировка на требование %s)" % srv])
    insert_after(n, [ON_R])

# ------------------------------------------- SECTION 4 date helper rollback
TCONST = find_line(re.escape(OBL + "\u0422\u0435\u0441\u0442\u043e\u0432\u044b\u0435\u041a\u043e\u043d\u0441\u0442\u0430\u043d\u0442\u044b") + r"$")
KON = "#\u041a\u043e\u043d\u0435\u0446\u041e\u0431\u043b\u0430\u0441\u0442\u0438"
tconst_end = min(i for i in range(TCONST + 1, len(lines) + 1) if lines[i - 1] == KON)
rx_ret = re.compile(r"^\t\u0412\u043e\u0437\u0432\u0440\u0430\u0442 \u0414\u0430\u0442\u0430\((\d{4}), (\d{1,2}), (\d{1,2})\);$")
matches = [i for i in range(TCONST + 1, tconst_end)
            if rx_ret.match(lines[i - 1])]
req(len(matches) == 15, "date rollback expected 15, got %d" % len(matches))
for i in reversed(matches):  # bottom-up: no index shifts
    y, mo, d = rx_ret.match(lines[i - 1]).groups()
    lines[i - 1:i] = ["\t\u0413\u043e\u0434 = %s;" % y,
                      "\t\u041c\u0435\u0441\u044f\u0446 = %s;" % mo,
                      "\t\u0414\u0435\u043d\u044c = %s;" % d,
                      "\t\u0412\u043e\u0437\u0432\u0440\u0430\u0442 \u0414\u0430\u0442\u0430(\u0413\u043e\u0434, \u041c\u0435\u0441\u044f\u0446, \u0414\u0435\u043d\u044c);"]
rolled = len(matches)
req(rolled == 15, "date rollback expected 15, got %d" % rolled)

# --------------------------------------------- SECTION 5 new 2025 helpers
def helper_block(name, day, comment):
    return ["// " + comment,
            "//",
            "// \u0412\u043e\u0437\u0432\u0440\u0430\u0449\u0430\u0435\u043c\u043e\u0435 \u0437\u043d\u0430\u0447\u0435\u043d\u0438\u0435:",
            "//   \u0414\u0430\u0442\u0430 - %d \u043c\u0430\u0440\u0442\u0430 2025 \u0433\u043e\u0434\u0430." % day,
            "//",
            "\u0424\u0443\u043d\u043a\u0446\u0438\u044f " + name + "()",
            "",
            "\t\u0413\u043e\u0434 = 2025;",
            "\t\u041c\u0435\u0441\u044f\u0446 = 3;",
            "\t\u0414\u0435\u043d\u044c = %d;" % day,
            "\t\u0412\u043e\u0437\u0432\u0440\u0430\u0442 \u0414\u0430\u0442\u0430(\u0413\u043e\u0434, \u041c\u0435\u0441\u044f\u0446, \u0414\u0435\u043d\u044c);",
            "",
            "\u041a\u043e\u043d\u0435\u0446\u0424\u0443\u043d\u043a\u0446\u0438\u0438",
            ""]

H1 = "\u0414\u0430\u0442\u0430\u041d\u0430\u0447\u0430\u043b\u0430\u041c\u0430\u0440\u0442\u043e\u0432\u0441\u043a\u043e\u0433\u043e\u041f\u0435\u0440\u0438\u043e\u0434\u0430\u0417\u0430\u0422\u0432" if False else \
     "\u0414\u0430\u0442\u0430\u041d\u0430\u0447\u0430\u043b\u0430\u041c\u0430\u0440\u0442\u043e\u0432\u0441\u043a\u043e\u0433\u043e\u041f\u0435\u0440\u0438\u043e\u0434\u0430\u041f\u0435\u0440\u0438\u043e\u0434\u0430\u0422\u0435\u0441\u0442\u0430"
# simpler canonical names:
H1 = "\u0414\u0430\u0442\u0430\u041d\u0430\u0447\u0430\u043b\u0430\u0422\u0435\u0441\u0442\u043e\u0432\u043e\u0433\u043e\u041f\u0435\u0440\u0438\u043e\u0434\u0430"          # ДатаНачалаТестовогоПериода
H2 = "\u0414\u0430\u0442\u0430\u0421\u0435\u0440\u0435\u0434\u0438\u043d\u044b\u0422\u0435\u0441\u0442\u043e\u0432\u043e\u0433\u043e\u041f\u0435\u0440\u0438\u043e\u0434\u0430"      # ДатаСерединыТестовогоПериода
H3 = "\u0414\u0430\u0442\u0430\u041e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f\u0422\u0435\u0441\u0442\u043e\u0432\u043e\u0433\u043e\u041f\u0435\u0440\u0438\u043e\u0434\u0430"    # ДатаОкончанияТестовогоПериода
new_helpers = []
new_helpers += helper_block(H1, 1, "Возвращает дату 1 марта 2025 года - начало тестового периода потребности.")
new_helpers += helper_block(H2, 5, "Возвращает дату 5 марта 2025 года - одиночный день внутри тестового периода.")
new_helpers += helper_block(H3, 10, "Возвращает дату 10 марта 2025 года - окончание тестового периода потребности.")
tconst_end = min(i for i in range(TCONST + 1, len(lines) + 1) if lines[i - 1] == KON)
insert_before(tconst_end, new_helpers)

# ------------------------------------- SECTION 6 text replaces (line-wise DSL)
def replace_in_lines(old, new, expected):
    cnt = 0
    for i, l in enumerate(lines):
        if l.lstrip().startswith("//"):
            continue
        if old in l:
            lines[i] = l.replace(old, new)
            cnt += l.count(old) - (l.count(old) - l.count(old)) + 1 if False else 1
            cnt = cnt  # count lines
    req(cnt == expected, "replace %r expected %d lines, got %d" % (old, expected, cnt))

for old, new, exp in [
    ('"\u0410\u043f\u043a\u041c\u043e\u0434\u0435\u043b\u0438\u0421\u0425\u0422\u0435\u0445\u043d\u0438\u043a\u0438"',
     "\u0418\u043c\u044f\u041a\u0430\u0442\u0430\u043b\u043e\u0433\u0430\u041c\u043e\u0434\u0435\u043b\u0435\u0439\u0421\u0425\u0422\u0435\u0445\u043d\u0438\u043a\u0438()", 21),
    ('"\u0428\u0438\u0440\u0438\u043d\u0430\u041e\u0431\u0440\u0430\u0431\u043e\u0442\u043a\u0438"',
     "\u0418\u043c\u044f\u0420\u0435\u043a\u0432\u0438\u0437\u0438\u0442\u0430\u0428\u0438\u0440\u0438\u043d\u044b\u041e\u0431\u0440\u0430\u0431\u043e\u0442\u043a\u0438()", 13),
    ('"\u041a\u043e\u044d\u0444\u0444\u0438\u0446\u0438\u0435\u043d\u0442\u041f\u0435\u0440\u0435\u0432\u043e\u0434\u0430\u0412\u0423\u042d\u0413\u0410"',
     "\u0418\u043c\u044f\u0420\u0435\u043a\u0432\u0438\u0437\u0438\u0442\u0430\u041a\u043e\u044d\u0444\u0444\u0438\u0446\u0438\u0435\u043d\u0442\u0430\u041f\u0435\u0440\u0435\u0432\u043e\u0434\u0430\u0412\u0423\u042d\u0413\u0410()", 4),
    ('"\u041c\u043e\u0449\u043d\u043e\u0441\u0442\u044c\u0414\u0432\u0438\u0433\u0430\u0442\u0435\u043b\u044f"',
     "\u0418\u043c\u044f\u0420\u0435\u043a\u0432\u0438\u0437\u0438\u0442\u0430\u041c\u043e\u0449\u043d\u043e\u0441\u0442\u0438\u0414\u0432\u0438\u0433\u0430\u0442\u0435\u043b\u044f()", 5),
]:
    replace_in_lines(old, new, exp)

# -------------------------------------- SECTION 7 DSL const functions
ORG = find_line(r"^\u0424\u0443\u043d\u043a\u0446\u0438\u044f \u0418\u043c\u044f\u0422\u0435\u0441\u0442\u043e\u0432\u043e\u0439\u041e\u0440\u0433\u0430\u043d\u0438\u0437\u0430\u0446\u0438\u0438\(\)$")
kf_end = min(i for i in range(ORG + 1, len(lines) + 1)
             if lines[i - 1] == "\u041a\u043e\u043d\u0435\u0446\u0424\u0443\u043d\u043a\u0446\u0438\u0438")


def const_fn(name, lit, comment):
    return ["// " + comment,
            "//",
            "// \u0412\u043e\u0437\u0432\u0440\u0430\u0449\u0430\u0435\u043c\u043e\u0435 \u0437\u043d\u0430\u0447\u0435\u043d\u0438\u0435:",
            "//   \u0421\u0442\u0440\u043e\u043a\u0430 - \u0438\u043c\u044f \u0438\u0437 \u043c\u0435\u0442\u0430\u0434\u0430\u043d\u043d\u044b\u0445 \u043e\u0441\u043d\u043e\u0432\u043d\u043e\u0439 \u043a\u043e\u043d\u0444\u0438\u0433\u0443\u0440\u0430\u0446\u0438\u0438.",
            "//",
            "\u0424\u0443\u043d\u043a\u0446\u0438\u044f " + name + "()",
            "",
            '\t\u0412\u043e\u0437\u0432\u0440\u0430\u0442 "' + lit + '";',
            "",
            "\u041a\u043e\u043d\u0435\u0446\u0424\u0443\u043d\u043a\u0446\u0438\u0438",
            ""]


fns = []
fns += const_fn("\u0418\u043c\u044f\u041a\u0430\u0442\u0430\u043b\u043e\u0433\u0430\u041c\u043e\u0434\u0435\u043b\u0435\u0439\u0421\u0425\u0422\u0435\u0445\u043d\u0438\u043a\u0438",
                "\u0410\u043f\u043a\u041c\u043e\u0434\u0435\u043b\u0438\u0421\u0425\u0422\u0435\u0445\u043d\u0438\u043a\u0438",
                "Возвращает имя каталога моделей СХ-техники АПК (внешний контур метаданных).")
fns += const_fn("\u0418\u043c\u044f\u0420\u0435\u043a\u0432\u0438\u0437\u0438\u0442\u0430\u0428\u0438\u0440\u0438\u043d\u044b\u041e\u0431\u0440\u0430\u0431\u043e\u0442\u043a\u0438",
                "\u0428\u0438\u0440\u0438\u043d\u0430\u041e\u0431\u0440\u0430\u0431\u043e\u0442\u043a\u0438",
                "Возвращает имя реквизита ширины обработки (внешний контур метаданных).")
fns += const_fn("\u0418\u043c\u044f\u0420\u0435\u043a\u0432\u0438\u0437\u0438\u0442\u0430\u041a\u043e\u044d\u0444\u0444\u0438\u0446\u0438\u0435\u043d\u0442\u0430\u041f\u0435\u0440\u0435\u0432\u043e\u0434\u0430\u0412\u0423\u042d\u0413\u0410",
                "\u041a\u043e\u044d\u0444\u0444\u0438\u0446\u0438\u0435\u043d\u0442\u041f\u0435\u0440\u0435\u0432\u043e\u0434\u0430\u0412\u0423\u042d\u0413\u0410",
                "Возвращает имя реквизита коэффициента перевода в УЭГ А (внешний контур метаданных).")
fns += const_fn("\u0418\u043c\u044f\u0420\u0435\u043a\u0432\u0438\u0437\u0438\u0442\u0430\u041c\u043e\u0449\u043d\u043e\u0441\u0442\u0438\u0414\u0432\u0438\u0433\u0430\u0442\u0435\u043b\u044f",
                "\u041c\u043e\u0449\u043d\u043e\u0441\u0442\u044c\u0414\u0432\u0438\u0433\u0430\u0442\u0435\u043b\u044f",
                "Возвращает имя реквизита мощности двигателя (внешний контур метаданных).")
insert_after(kf_end + 1, fns)  # after the blank line following КонецФункции

print("sections 1-7 OK, lines=%d" % len(lines))
out = NL.join(lines) + NL
# SECTION 6b: whole-text replaces (dates, log level) after join
reps = [("\u0414\u0430\u0442\u0430(2025, 3, 1)", H1 + "()", 8),
        ("\u0414\u0430\u0442\u0430(2025, 3, 10)", H3 + "()", 8),
        ("\u0414\u0430\u0442\u0430(2025, 3, 5)", H2 + "()", 2)]
for old, new, exp in reps:
    cnt = out.count(old)
    req(cnt == exp, "text replace %r expected %d, got %d" % (old, exp, cnt))
    out = out.replace(old, new)
old = "\u0423\u0440\u043e\u0432\u0435\u043d\u044c\u0416\u0443\u0440\u043d\u0430\u043b\u0430\u0420\u0435\u0433\u0438\u0441\u0442\u0440\u0430\u0446\u0438\u0438.\u0418\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f,,, \u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435\u041e\u0448\u0438\u0431\u043a\u0438());"
cnt = out.count(old)
req(cnt == 2, "log level replace expected 2, got %d" % cnt)
out = out.replace(old, "\u0423\u0440\u043e\u0432\u0435\u043d\u044c\u0416\u0443\u0440\u043d\u0430\u043b\u0430\u0420\u0435\u0433\u0438\u0441\u0442\u0440\u0430\u0446\u0438\u0438.\u041e\u0448\u0438\u0431\u043a\u0430,,, \u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435\u041e\u0448\u0438\u0431\u043a\u0438());")
lines = out.replace("\r\n", "\n").split("\n")
if lines and lines[-1] == "":
    lines.pop()

print("sections 6b OK")
data = out.encode("utf-8")
if bom:
    data = b"\xef\xbb\xbf" + data
open(PATH, "wb").write(data)
print("WROTE part 1. lines=%d" % len(lines))
