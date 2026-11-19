#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wave 6b part 2 for Тх_Тесты/Ext/Module.bsl: Typo suppression pairs x16,
MagicNumber named locals (misc sites), IfConditionComplexity (Сцепка).
Content-anchored, all asserts, abort leaves file untouched.
"""
import re

PATH = ("src/cfe/\u041f\u043b\u0430\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435"
        "\u0422\u0435\u0445\u043d\u0438\u043a\u0438\u0410\u041f\u041a/CommonModules/"
        "\u0422\u0445_\u0422\u0435\u0441\u0442\u044b/Ext/Module.bsl")

raw = open(PATH, "rb").read()
bom = raw.startswith(b"\xef\xbb\xbf")
text = raw.decode("utf-8-sig")
NL = "\r\n" if "\r\n" in text else "\n"
lines = text.replace("\r\n", "\n").split("\n")
if lines and lines[-1] == "":
    lines.pop()


def req(cond, msg):
    if not cond:
        raise SystemExit("ANCHOR FAIL: " + msg)


def find_line(pattern):
    rx = re.compile(pattern)
    hits = [i for i, l in enumerate(lines, 1) if rx.match(l)]
    req(len(hits) == 1, "unique match expected for %r, got %d at %r" % (pattern, len(hits), hits))
    return hits[0]


def find_lines(sub):
    return [i for i, l in enumerate(lines, 1) if sub in l]


def wrap(idx, off, on):
    """off comment above line idx, on comment below line idx."""
    lines[idx - 1:idx - 1] = [off]
    lines[idx:idx] = [on]


ON_T = "// BSLLS:Typo-on"

# ---- T1: Подр literal (Тх_ТестПодр)
n = find_line(r"^\t\u0412\u043e\u0437\u0432\u0440\u0430\u0442 \"\u0422\u0445_\u0422\u0435\u0441\u0442\u041f[^ \"]*\";$")
wrap(n, "// BSLLS:Typo-off (эталонный литерал тестового подразделения - внешний контракт данных)", ON_T)

# ---- T2: three test-name declarations (Техресурсов / ДемоДанные / ЧужоеПодразделение)
NAMES = ["\u0422\u0435\u0441\u0442\u041f\u043b\u0430\u043d\u0422\u0435\u0445\u0440\u0435\u0441\u0443\u0440\u0441\u043e\u0432",
         "\u0422\u0435\u0441\u0442\u041f\u043e\u0442\u0440\u0435\u0431\u043d\u043e\u0441\u0442\u044c\u041f\u043e\u0422\u0435\u0445\u043a\u0430\u0440\u0442\u0430\u043c"]
OFF_NAME = "// BSLLS:Typo-off (эталонное имя теста - внешний контракт прогона)"
decls = []
for pat in [r"^\u0424\u0443\u043d\u043a\u0446\u0438\u044f \u0422\u0435\u0441\u0442\u041f\u043b\u0430\u043d\u0422\u0435\u0445\u0440\u0435\u0441\u0443\u0440\u0441\u043e\u0432[^ (]*\(\) \u042d\u043a\u0441\u043f\u043e\u0440\u0442$",
            r"^\u0424\u0443\u043d\u043a\u0446\u0438\u044f \u0422\u0435\u0441\u0442\u041f\u043e\u0442\u0440\u0435\u0431\u043d\u043e\u0441\u0442\u044c\u041f\u043e\u0422\u0435\u0445\u043a\u0430\u0440\u0442\u0430\u043c[^ (]*\(\) \u042d\u043a\u0441\u043f\u043e\u0440\u0442$"]:
    rx = re.compile(pat)
    decls += [i for i, l in enumerate(lines, 1) if rx.match(l)]
req(len(decls) == 3, "expected 3 test decls, got %d: %r" % (len(decls), decls))
for i in reversed(sorted(decls)):
    wrap(i, OFF_NAME, ON_T)

# ---- T3: their context lines
ctxs = []
for pat in [r"^\t\u041a\u043e\u043d\u0442\u0435\u043a\u0441\u0442 = \u041d\u043e\u0432\u044b\u0439\u041a\u043e\u043d\u0442\u0435\u043a\u0441\u0442\u0422\u0435\u0441\u0442\u0430\(\"\u0422\u0435\u0441\u0442\u041f\u043b\u0430\u043d\u0422\u0435\u0445\u0440\u0435\u0441\u0443\u0440\u0441\u043e\u0432[^\"]*\"\);$",
            r"^\t\u041a\u043e\u043d\u0442\u0435\u043a\u0441\u0442 = \u041d\u043e\u0432\u044b\u0439\u041a\u043e\u043d\u0442\u0435\u043a\u0441\u0442\u0422\u0435\u0441\u0442\u0430\(\"\u0422\u0435\u0441\u0442\u041f\u043e\u0442\u0440\u0435\u0431\u043d\u043e\u0441\u0442\u044c\u041f\u043e\u0422\u0435\u0445\u043a\u0430\u0440\u0442\u0430\u043c[^\"]*\"\);$"]:
    rx = re.compile(pat)
    ctxs += [i for i, l in enumerate(lines, 1) if rx.match(l)]
req(len(ctxs) == 3, "expected 3 ctx lines, got %d: %r" % (len(ctxs), ctxs))
for i in reversed(sorted(ctxs)):
    wrap(i, OFF_NAME, ON_T)

# ---- T4: Тран variable
n = find_line(r"^\t\u0418\u043c\u044f\u0420\u0435\u0433\u0438\u0441\u0442\u0440\u0430\u0422\u0440\u0430\u043d\u0420\u0430\u0431\u043e\u0442 = \"[^\"]*\";$")
wrap(n, "// BSLLS:Typo-off (Тран - принятый доменный префикс транспортных работ в имени переменной)", ON_T)

# ---- T5: техкарты message lines x4
SUB5 = ("\u043d\u0435\u0442 \u0434\u0430\u043d\u043d\u044b\u0445 \u0433\u043e\u0434\u043e\u0432\u043e\u0433\u043e "
        "\u043f\u043b\u0430\u043d\u0430 \u0410\u041f\u041a (\u0442\u0435\u0445\u043a\u0430\u0440\u0442\u044b)")
hits = find_lines(SUB5)
req(len(hits) == 4, "expected 4 техкарты lines, got %d: %r" % (len(hits), hits))
for i in reversed(hits):
    wrap(i, "// BSLLS:Typo-off («техкарты» - доменное сокращение годового плана АПК в тексте сообщения)", ON_T)

# ---- T6: Неопределено Проверить blocks x4
T6 = ["\u0421\u0425-\u043e\u0431\u043e\u0440\u0443\u0434\u043e\u0432\u0430\u043d\u0438\u0435 \u0431\u0435\u0437 \u0448\u0438\u0440\u0438\u043d\u044b - \u041d\u0435\u043e\u043f\u0440\u0435\u0434\u0435\u043b\u0435\u043d\u043e",
      "\u0443 \u0437\u0430\u043c\u0435\u043d\u044b \u043d\u0435 \u0437\u0430\u043f\u043e\u043b\u043d\u0435\u043d \u0440\u0435\u043a\u0432\u0438\u0437\u0438\u0442 - \u041d\u0435\u043e\u043f\u0440\u0435\u0434\u0435\u043b\u0435\u043d\u043e",
      "\u0440\u0430\u0437\u043d\u044b\u0435 \u0431\u0430\u0437\u043e\u0432\u044b\u0435 \u0440\u0435\u043a\u0432\u0438\u0437\u0438\u0442\u044b - \u041d\u0435\u043e\u043f\u0440\u0435\u0434\u0435\u043b\u0435\u043d\u043e",
      "\u0440\u0430\u0437\u043d\u044b\u0435 \u043a\u0430\u0442\u0430\u043b\u043e\u0433\u0438 - \u041d\u0435\u043e\u043f\u0440\u0435\u0434\u0435\u043b\u0435\u043d\u043e"]
OFF6 = "// BSLLS:Typo-off (слово «Неопределено» в тексте проверки - значение контракта)"
for sub in T6:
    hits = find_lines(sub)
    req(len(hits) == 1, "expected 1 line for %r, got %r" % (sub[:20], hits))
    i = hits[0]
    req("\u041f\u0440\u043e\u0432\u0435\u0440\u0438\u0442\u044c" in lines[i - 1], "T6 anchor not a Проверить line: %r" % lines[i - 1][:60])
    # off above, on below the expression line i+1
    lines[i - 1:i - 1] = [OFF6]
    lines[i + 1:i + 1] = [ON_T]

# ---- M1: Окр(..., 2)
n = find_line(r"^\t\u0412\u043e\u0437\u0432\u0440\u0430\u0442 \u041c\u0430\u043a\u0441\(0, \u041e\u043a\u0440\(\u041f\u043e\u0442\u0440\u0435\u0431\u043d\u043e\u0441\u0442\u044c\u0421\u043c\u0435\u043d - \u0414\u043e\u0441\u0442\u0443\u043f\u043d\u043e\u0421\u043c\u0435\u043d, 2\)\);$")
lines[n - 1:n] = ["\t\u0417\u043d\u0430\u043a\u043e\u0432\u041e\u043a\u0440\u0443\u0433\u043b\u0435\u043d\u0438\u044f\u0414\u0435\u0444\u0438\u0446\u0438\u0442\u0430 = 2;",
                  "\t\u0412\u043e\u0437\u0432\u0440\u0430\u0442 \u041c\u0430\u043a\u0441(0, \u041e\u043a\u0440(\u041f\u043e\u0442\u0440\u0435\u0431\u043d\u043e\u0441\u0442\u044c\u0421\u043c\u0435\u043d - \u0414\u043e\u0441\u0442\u0443\u043f\u043d\u043e\u0421\u043c\u0435\u043d, \u0417\u043d\u0430\u043a\u043e\u0432\u041e\u043a\u0440\u0443\u0433\u043b\u0435\u043d\u0438\u044f\u0414\u0435\u0444\u0438\u0446\u0438\u0442\u0430));"]

# ---- M2: Ожидаемо = 10 / 1.5
n = find_line(r"^\t\t\t\u041e\u0436\u0438\u0434\u0430\u0435\u043c\u043e = 10 / 1\.5;$")
lines[n - 1:n] = ["\t\t\t\u041f\u043e\u043b\u043d\u0430\u044f\u0415\u043c\u043a\u043e\u0441\u0442\u044c\u0421\u043c\u0435\u043d = 10;",
                  "\t\t\t\u041a\u043e\u044d\u0444\u0444\u0438\u0446\u0438\u0435\u043d\u0442\u0417\u0430\u043c\u0435\u0449\u0435\u043d\u0438\u044f\u0422\u0435\u0441\u0442\u0430 = 1.5;",
                  "\t\t\t\u041e\u0436\u0438\u0434\u0430\u0435\u043c\u043e = \u041f\u043e\u043b\u043d\u0430\u044f\u0415\u043c\u043a\u043e\u0441\u0442\u044c\u0421\u043c\u0435\u043d / \u041a\u043e\u044d\u0444\u0444\u0438\u0446\u0438\u0435\u043d\u0442\u0417\u0430\u043c\u0435\u0449\u0435\u043d\u0438\u044f\u0422\u0435\u0441\u0442\u0430;"]

# ---- M3: ЧислоДнейПериода = 10 дней
n = find_line(r"^\t\t\u041f\u0440\u043e\u0432\u0435\u0440\u0438\u0442\u044c\(.*01\.03\.\.10\.03 .*$")
lines[n - 1:n - 1] = ["\t\t\u041e\u0436\u0438\u0434\u0430\u0435\u043c\u043e\u0414\u043d\u0435\u0439\u041f\u0435\u0440\u0438\u043e\u0434\u0430 = 10;"]
req("= 10)" in lines[n + 1], "M3 expr line unexpected: %r" % lines[n + 1][:70])
lines[n + 1] = lines[n + 1].replace("= 10)", "= \u041e\u0436\u0438\u0434\u0430\u0435\u043c\u043e\u0414\u043d\u0435\u0439\u041f\u0435\u0440\u0438\u043e\u0434\u0430)")

# ---- M4: колонки карты = 3
n = find_line(r"^.*\u043a\u043e\u043b\u043e\u043d\u043a\u0438 \u043a\u0430\u0440\u0442\u044b.*$")
lines[n - 1:n - 1] = ["\u041e\u0436\u0438\u0434\u0430\u0435\u043c\u043e\u041a\u043e\u043b\u043e\u043d\u043e\u043a\u041a\u0430\u0440\u0442\u044b = 3;"]
req("= 3," in lines[n + 1], "M4 expr unexpected: %r" % lines[n + 1][:70])
lines[n + 1] = lines[n + 1].replace("= 3,", "= \u041e\u0436\u0438\u0434\u0430\u0435\u043c\u043e\u041a\u043e\u043b\u043e\u043d\u043e\u043a\u041a\u0430\u0440\u0442\u044b,")

# ---- M5/M6: ЗаполнитьТЧПланаРабот call sites (10,1) and (10,2)
for args, smen in [("10, 1);", 1), ("10, 2);", 2)]:
    n = find_line(r"^\t+\u0414\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u041e\u0431\u044a\u0435\u043a\u0442, \u041f\u043e\u0442\u0440\u0435\u0431\u043d\u043e\u0441\u0442\u044c, \u0414\u043e\u0441\u0442\u0443\u043f\u043d\u043e\u0441\u0442\u044c, " + re.escape(args) + r"$")
    lines[n - 2:n - 2] = ["\t\t\t\u0414\u043d\u0435\u0439\u041f\u0435\u0440\u0438\u043e\u0434\u0430\u0422\u0435\u0441\u0442\u0430 = 10;",
                          "\t\t\t\u0421\u043c\u0435\u043d\u0412\u0414\u0435\u043d\u044c\u0422\u0435\u0441\u0442\u0430 = %d;" % smen]
    lines[n - 1] = lines[n - 1].replace("10, %d);" % smen,
                                        "\u0414\u043d\u0435\u0439\u041f\u0435\u0440\u0438\u043e\u0434\u0430\u0422\u0435\u0441\u0442\u0430, \u0421\u043c\u0435\u043d\u0412\u0414\u0435\u043d\u044c\u0422\u0435\u0441\u0442\u0430)")

# ---- M7: строк: 3 / дефицитных: 2
for sub, var, val in [(r"\u0441\u0442\u0440\u043e\u043a: 3", "\u041e\u0436\u0438\u0434\u0430\u0435\u043c\u043e\u0421\u0442\u0440\u043e\u043a\u041f\u043b\u0430\u043d\u0430", 3),
                      (r"\u0434\u0435\u0444\u0438\u0446\u0438\u0442\u043d\u044b\u0445: 2", "\u041e\u0436\u0438\u0434\u0430\u0435\u043c\u043e\u0414\u0435\u0444\u0438\u0446\u0438\u0442\u043d\u044b\u0445\u0421\u0442\u0440\u043e\u043a", 2)]:
    rx = re.compile(sub)
    hits = [i for i, l in enumerate(lines, 1) if rx.search(l)]
    req(len(hits) == 1, "M7 anchor %r: got %r" % (sub[:12], hits))
    n = hits[0]
    indent = re.match(r"^[\t ]*", lines[n - 1]).group(0)
    lines[n - 1:n - 1] = [indent + var + " = %d;" % val]
    req("= %d," % val in lines[n + 1], "M7 expr unexpected: %r" % lines[n + 1][:70])
    lines[n + 1] = lines[n + 1].replace("= %d," % val, "= " + var + ",")

# ---- M8: bounds x5 (1.499/1.501 x3, 1.999/2.001 x2)
BOUNDS = [(r"\u041a = 6/4 = 1\.5", "1.499", "1.501"),
          (r"\u041a = 3/2 = 1\.5 \(\u0448\u0438\u0440\u0438\u043d\u0430 1\.5x\)", "1.499", "1.501"),
          (r"\u041a \u043f\u043e \u043c\u043e\u0449\u043d\u043e\u0441\u0442\u0438 = 150/100 = 1\.5", "1.499", "1.501"),
          (r"\u041a \u043f\u043e \u0433\u0440\u0443\u0437\u043e\u043f\u043e\u0434\u044a\u0435\u043c\u043d\u043e\u0441\u0442\u0438 = 10/5 = 2", "1.999", "2.001"),
          (r"\u041a \u043f\u043e \u0432\u043c\u0435\u0441\u0442\u0438\u043c\u043e\u0441\u0442\u0438 \u043f\u0440\u0438\u0446\u0435\u043f\u043e\u0432 = 20/10 = 2", "1.999", "2.001")]
LO = "\u041d\u0438\u0436\u043d\u044f\u044f\u0413\u0440\u0430\u043d\u0438\u0446\u0430\u0414\u043e\u043f\u0443\u0441\u043a\u0430"
HI = "\u0412\u0435\u0440\u0445\u043d\u044f\u044f\u0413\u0440\u0430\u043d\u0438\u0446\u0430\u0414\u043e\u043f\u0443\u0441\u043a\u0430"
for sub, lo, hi in BOUNDS:
    rx = re.compile(sub)
    hits = [i for i, l in enumerate(lines, 1) if rx.search(l) and l.lstrip().startswith("\u041f\u0440\u043e\u0432\u0435\u0440\u0438\u0442\u044c")]
    req(len(hits) == 1, "M8 anchor %r: got %r" % (sub[:20], hits))
    n = hits[0]
    indent = re.match(r"^[\t ]*", lines[n - 1]).group(0)
    vlo, vhi = float(lo), float(hi)
    lines[n - 1:n - 1] = [indent + LO + " = %s;" % lo,
                          indent + HI + " = %s;" % hi]
    req(lo in lines[n + 2] and hi in lines[n + 2], "M8 expr missing bounds: %r" % lines[n + 2][:80])
    lines[n + 2] = lines[n + 2].replace(lo, LO).replace(hi, HI)

# ---- I1: Если МодельСХ = Неопределено ИЛИ ... Тогда (Сцепка)
n1 = find_line(r"^\t\t\u0415\u0441\u043b\u0438 \u041c\u043e\u0434\u0435\u043b\u044c\u0421\u0425 = \u041d\u0435\u043e\u043f\u0440\u0435\u0434\u0435\u043b\u0435\u043d\u043e \u0418\u041b\u0418 \u041c\u043e\u0434\u0435\u043b\u044c\u0410\u0432\u0442\u043e = \u041d\u0435\u043e\u043f\u0440\u0435\u0434\u0435\u043b\u0435\u043d\u043e$")
req("\u0422\u043e\u0433\u0434\u0430" in lines[n1], "I1: no Тогда on continuation line: %r" % lines[n1][:80])
lines[n1 - 1:n1 + 1] = ["\t\t\u0415\u0441\u0442\u044c\u041d\u0435\u0441\u043e\u0437\u0434\u0430\u043d\u043d\u044b\u0435\u041c\u043e\u0434\u0435\u043b\u0438 = \u041c\u043e\u0434\u0435\u043b\u044c\u0421\u0425 = \u041d\u0435\u043e\u043f\u0440\u0435\u0434\u0435\u043b\u0435\u043d\u043e \u0418\u041b\u0418 \u041c\u043e\u0434\u0435\u043b\u044c\u0410\u0432\u0442\u043e = \u041d\u0435\u043e\u043f\u0440\u0435\u0434\u0435\u043b\u0435\u043d\u043e",
                        "\t\t\t\u0418\u041b\u0418 \u041e\u0431\u043e\u0440\u0443\u0434\u043e\u0432\u0430\u043d\u0438\u0435\u0421\u0425 = \u041d\u0435\u043e\u043f\u0440\u0435\u0434\u0435\u043b\u0435\u043d\u043e \u0418\u041b\u0418 \u041f\u0440\u0438\u0446\u0435\u043f = \u041d\u0435\u043e\u043f\u0440\u0435\u0434\u0435\u043b\u0435\u043d\u043e;",
                        "\t\t\u0415\u0441\u043b\u0438 \u0415\u0441\u0442\u044c\u041d\u0435\u0441\u043e\u0437\u0434\u0430\u043d\u043d\u044b\u0435\u041c\u043e\u0434\u0435\u043b\u0438 \u0422\u043e\u0433\u0434\u0430"]

out = NL.join(lines) + NL
data = out.encode("utf-8")
if bom:
    data = b"\xef\xbb\xbf" + data
open(PATH, "wb").write(data)
print("WROTE part 2. lines=%d" % len(lines))
