#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wave 6b round 3 for Тх_Тесты/Ext/Module.bsl.

A. repair mis-placed Typo suppression pairs ([off][on][target] -> [off][target][on])
B. split overlong line 1029
C. ОжидатьЗавершения -> ОжидатьЗавершенияВыполнения x2
D. log lines: spaces after commas + ПодробноеПредставлениеОшибки x2
E. LatinAndCyrillic suppression pair for ТестВалидацииGenericТипов decl
F. CompareWithBoolean x2 -> НЕ
G. MagicNumber x16: named locals for СоздатьЭлемент values
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
        raise SystemExit("FAIL: " + msg)


# ---------- A: repair Typo pairs
ON = "// BSLLS:Typo-on"
fixed = 0
i = 0
while i < len(lines) - 1:
    if "BSLLS:Typo-off" in lines[i] and lines[i + 1] == ON and "BSLLS:" not in lines[i + 2]:
        # [off][on][target] -> [off][target][on]
        lines[i + 1:i + 2] = []
        lines[i + 2:i + 2] = [ON]
        fixed += 1
        i += 3
    else:
        i += 1
req(fixed == 12, "Typo pair repair expected 12, got %d" % fixed)

# ---------- B: split line 1029
rx = re.compile(r"^(\t\t\t.*\u0427\u0438\u0441\u043b\u043e\u0414\u043d\u0435\u0439\u041f\u0435\u0440\u0438\u043e\u0434\u0430\(\u0414\u0430\u0442\u0430\u041d\u0430\u0447\u0430\u043b\u0430\u0422\u0435\u0441\u0442\u043e\u0432\u043e\u0433\u043e\u041f\u0435\u0440\u0438\u043e\u0434\u0430\(\), )(.*)$")
hits = [i for i, l in enumerate(lines) if rx.match(l) and len(l) > 120]
req(len(hits) == 1, "B anchor: %r" % hits)
i = hits[0]
m = rx.match(lines[i])
lines[i:i + 1] = [m.group(1).rstrip(), "\t\t\t\t" + m.group(2)]

# ---------- C: deprecated method
cnt = 0
for i, l in enumerate(lines):
    if ".\u041e\u0436\u0438\u0434\u0430\u0442\u044c\u0417\u0430\u0432\u0435\u0440\u0448\u0435\u043d\u0438\u044f(" in l:
        lines[i] = l.replace("\u041e\u0436\u0438\u0434\u0430\u0442\u044c\u0417\u0430\u0432\u0435\u0440\u0448\u0435\u043d\u0438\u044f(",
                             "\u041e\u0436\u0438\u0434\u0430\u0442\u044c\u0417\u0430\u0432\u0435\u0440\u0448\u0435\u043d\u0438\u044f\u0412\u044b\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u044f(")
        cnt += 1
req(cnt == 2, "C expected 2, got %d" % cnt)

# ---------- D: log lines
D = [("\u041e\u0448\u0438\u0431\u043a\u0430,,, \u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435\u041e\u0448\u0438\u0431\u043a\u0438());",
      "\u041e\u0448\u0438\u0431\u043a\u0430, , , \u041f\u043e\u0434\u0440\u043e\u0431\u043d\u043e\u0435\u041f\u0440\u0435\u0434\u0441\u0442\u0430\u0432\u043b\u0435\u043d\u0438\u0435\u041e\u0448\u0438\u0431\u043a\u0438(\u0418\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f\u041e\u0431\u043e\u0448\u0438\u0431\u043a\u0435()));", 2),
     ("\u0418\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f,,, \u0422\u0435\u043a\u0441\u0442\u0418\u0441\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u044f);",
      "\u0418\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f, , , \u0422\u0435\u043a\u0441\u0442\u0418\u0441\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u044f);", 1),
     ("\u041e\u0448\u0438\u0431\u043a\u0430,,, \u0422\u0435\u043a\u0441\u0442\u041e\u0448\u0438\u0431\u043a\u0438);",
      "\u041e\u0448\u0438\u0431\u043a\u0430, , , \u0422\u0435\u043a\u0441\u0442\u041e\u0448\u0438\u0431\u043a\u0438);", 1)]
for old, new, exp in D:
    cnt = sum(1 for l in lines if old in l)
    req(cnt == exp, "D %r expected %d got %d" % (old[:20], exp, cnt))
    for i, l in enumerate(lines):
        if old in l:
            lines[i] = l.replace(old, new)

# ---------- E: LatinAndCyrillic pair
rx = re.compile(r"^\u0424\u0443\u043d\u043a\u0446\u0438\u044f \u0422\u0435\u0441\u0442\u0412\u0430\u043b\u0438\u0434\u0430\u0446\u0438\u0438Generic\u0422\u0438\u043f\u043e\u0432\(\) \u042d\u043a\u0441\u043f\u043e\u0440\u0442$")
hits = [i for i, l in enumerate(lines) if rx.match(l)]
req(len(hits) == 1, "E anchor %r" % hits)
i = hits[0]
lines[i:i] = ["// BSLLS:LatinAndCyrillicSymbolInWord-off (имя теста - внешний контракт прогона)"]
lines[i + 2:i + 2] = ["// BSLLS:LatinAndCyrillicSymbolInWord-on"]

# ---------- F: CompareWithBoolean
cnt = 0
for i, l in enumerate(lines):
    if l.strip() == "\u0420\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442\u0412\u044b\u0437\u043e\u0432\u0430 = \u041b\u043e\u0436\u044c);":
        lines[i] = l.replace("\u0420\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442\u0412\u044b\u0437\u043e\u0432\u0430 = \u041b\u043e\u0436\u044c", "\u041d\u0415 \u0420\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442\u0412\u044b\u0437\u043e\u0432\u0430")
        cnt += 1
req(cnt == 2, "F expected 2 got %d" % cnt)

# ---------- G: Magic locals
# G1: two-line call sites: anchor line A (call start), value line B (A_idx+1)
def magic_two(var, val, call_rx, attr, expect):
    """call_rx matches the call-start line; value line = next; attr = escaped ИмяРеквизита..."""
    rx = re.compile(call_rx)
    hits = [i for i, l in enumerate(lines) if rx.match(l)
            and attr in lines[i + 1] and (", %s));" % val) in lines[i + 1]]
    req(len(hits) == expect, "G %s: %r" % (var, hits))
    for i in reversed(hits):
        b = lines[i + 1]
        req((", %s));" % val) in b, "G value line: %r" % b[:80])
        indent = re.match(r"^[\t ]*", lines[i]).group(0)
        lines[i:i] = [indent + var + " = %s;" % val]
        lines[i + 2] = lines[i + 2].replace(", %s));" % val, ", %s));" % var)

CE = r"\u0421\u043e\u0437\u0434\u0430\u0442\u044c\u042d\u043b\u0435\u043c\u0435\u043d\u0442\(\u0418\u043c\u044f\u041a\u0430\u0442\u0430\u043b\u043e\u0433\u0430\u041c\u043e\u0434\u0435\u043b\u0435\u0439\u0421\u0425\u0422\u0435\u0445\u043d\u0438\u043a\u0438\(\),$"
SHIR = "\u0418\u043c\u044f\u0420\u0435\u043a\u0432\u0438\u0437\u0438\u0442\u0430\u0428\u0438\u0440\u0438\u043d\u044b\u041e\u0431\u0440\u0430\u0431\u043e\u0442\u043a\u0438"
KOEF = "\u0418\u043c\u044f\u0420\u0435\u043a\u0432\u0438\u0437\u0438\u0442\u0430\u041a\u043e\u044d\u0444\u0444\u0438\u0446\u0438\u0435\u043d\u0442\u0430\u041f\u0435\u0440\u0435\u0432\u043e\u0434\u0430\u0412\u0423\u042d\u0413\u0410"
MOSH = "\u0418\u043c\u044f\u0420\u0435\u043a\u0432\u0438\u0437\u0438\u0442\u0430\u041c\u043e\u0449\u043d\u043e\u0441\u0442\u0438\u0414\u0432\u0438\u0433\u0430\u0442\u0435\u043b\u044f"

# МодельОригинал / МодельЗамены (Ширина 2/3), two identical test scopes
magic_two("\u0428\u0438\u0440\u0438\u043d\u0430\u041e\u0440\u0438\u0433\u0438\u043d\u0430\u043b\u0430", "2",
          r"^\t\t\u041c\u043e\u0434\u0435\u043b\u044c\u041e\u0440\u0438\u0433\u0438\u043d\u0430\u043b = " + CE, SHIR, 2)
magic_two("\u0428\u0438\u0440\u0438\u043d\u0430\u0417\u0430\u043c\u0435\u043d\u044b", "3",
          r"^\t\t\u041c\u043e\u0434\u0435\u043b\u044c\u0417\u0430\u043c\u0435\u043d\u044b = " + CE, SHIR, 1)
# МодельА/МодельБ pairs
magic_two("\u041a\u041f\u0435\u0440\u0435\u0432\u043e\u0434\u0430\u041c\u043e\u0434\u0435\u043b\u0438\u0410", "4",
          r"^\t\t\u041c\u043e\u0434\u0435\u043b\u044c\u0410 = " + CE, KOEF, 1)
magic_two("\u041a\u041f\u0435\u0440\u0435\u0432\u043e\u0434\u0430\u041c\u043e\u0434\u0435\u043b\u0438\u0411", "6",
          r"^\t\t\u041c\u043e\u0434\u0435\u043b\u044c\u0411 = " + CE, KOEF, 1)
magic_two("\u0428\u0438\u0440\u0438\u043d\u0430\u041c\u043e\u0434\u0435\u043b\u0438\u0410", "2",
          r"^\t\t\u041c\u043e\u0434\u0435\u043b\u044c\u0410 = " + CE, SHIR, 1)
magic_two("\u0428\u0438\u0440\u0438\u043d\u0430\u041c\u043e\u0434\u0435\u043b\u0438\u0411", "3",
          r"^\t\t\u041c\u043e\u0434\u0435\u043b\u044c\u0411 = " + CE, SHIR, 1)
# Трактор100/Трактор150
magic_two("\u041c\u043e\u0449\u043d\u043e\u0441\u0442\u044c\u0422\u0440\u0430\u043a\u0442\u043e\u0440\u0430\u0411\u043e\u043b\u044c\u0448\u043e\u0433\u043e", "100",
          r"^\t\t\u0422\u0440\u0430\u043a\u0442\u043e\u0440100 = " + CE, MOSH, 1)
magic_two("\u041c\u043e\u0449\u043d\u043e\u0441\u0442\u044c\u0422\u0440\u0430\u043a\u0442\u043e\u0440\u0430\u0421\u0440\u0435\u0434\u043d\u0435\u0433\u043e", "150",
          r"^\t\t\u0422\u0440\u0430\u043a\u0442\u043e\u0440150 = " + CE, MOSH, 1)
# ОборудованиеШирокое (2-line, literal catalog name)
magic_two("\u0428\u0438\u0440\u0438\u043d\u0430\u041e\u0431\u043e\u0440\u0443\u0434\u043e\u0432\u0430\u043d\u0438\u044f\u0428\u0438\u0440\u043e\u043a\u043e\u0433\u043e", "4",
          r"^\t\t\u041e\u0431\u043e\u0440\u0443\u0434\u043e\u0432\u0430\u043d\u0438\u0435\u0428\u0438\u0440\u043e\u043a\u043e\u0435 = \u0421\u043e\u0437\u0434\u0430\u0442\u044c\u042d\u043b\u0435\u043c\u0435\u043d\u0442\(\"\u0410\u043f\u043a\u041c\u043e\u0434\u0435\u043b\u0438\u0421\u0425\u041e\u0431\u043e\u0440\u0443\u0434\u043e\u0432\u0430\u043d\u0438\u044f\",$", SHIR, 1)
magic_two("\u041a\u041f\u0435\u0440\u0435\u0432\u043e\u0434\u0430\u0420\u0443\u0447\u043d\u043e\u0439\u041c\u043e\u0434\u0435\u043b\u0438", "4",
          r"^\t\t\u041c\u043e\u0434\u0435\u043b\u044c\u0420\u0443\u0447\u043d\u0430\u044f = " + CE, KOEF, 1)
magic_two("\u041c\u043e\u0449\u043d\u043e\u0441\u0442\u044c\u041c\u043e\u0449\u043d\u043e\u0439\u041c\u043e\u0434\u0435\u043b\u0438", "100",
          r"^\t\t\u041c\u043e\u0434\u0435\u043b\u044c\u041c\u043e\u0449\u043d\u0430\u044f = " + CE, MOSH, 1)
# 3947: МодельА Ширина 3 (same var name, different scope)
magic_two("\u0428\u0438\u0440\u0438\u043d\u0430\u041c\u043e\u0434\u0435\u043b\u0438\u0410", "3",
          r"^\t\t\u041c\u043e\u0434\u0435\u043b\u044c\u0410 = " + CE, SHIR, 1)

# G2: one-line call sites (3119/3120/3272)
def magic_one(var, val, target_sub):
    hits = [i for i, l in enumerate(lines) if target_sub in l
            and (", %s));" % val) in l and SHIR in l]
    req(len(hits) == 1, "G1 %s: %r" % (var, hits))
    i = hits[0]
    req((", %s));" % val) in lines[i], "G1 value: %r" % lines[i][:90])
    indent = re.match(r"^[\t ]*", lines[i]).group(0)
    lines[i:i] = [indent + var + " = %s;" % val]
    lines[i + 1] = lines[i + 1].replace(", %s));" % val, ", %s));" % var)

magic_one("\u0428\u0438\u0440\u0438\u043d\u0430\u041e\u0440\u0438\u0433\u0438\u043d\u0430\u043b\u0430", "2",
          "\t\u041e\u0440\u0438\u0433\u0438\u043d\u0430\u043b = " + "\u0421\u043e\u0437\u0434\u0430\u0442\u044c\u042d\u043b\u0435\u043c\u0435\u043d\u0442(")
magic_one("\u0428\u0438\u0440\u0438\u043d\u0430\u0417\u0430\u043c\u0435\u043d\u044b", "3",
          "\t\u0417\u0430\u043c\u0435\u043d\u0430 = " + "\u0421\u043e\u0437\u0434\u0430\u0442\u044c\u042d\u043b\u0435\u043c\u0435\u043d\u0442(")
magic_one("\u0428\u0438\u0440\u0438\u043d\u0430\u041c\u043e\u0434\u0435\u043b\u0438", "2",
          "\t\u041c\u043e\u0434\u0435\u043b\u044c = " + "\u0421\u043e\u0437\u0434\u0430\u0442\u044c\u042d\u043b\u0435\u043c\u0435\u043d\u0442(")

out = NL.join(lines) + NL
data = out.encode("utf-8")
if bom:
    data = b"\xef\xbb\xbf" + data
open(PATH, "wb").write(data)
print("WROTE round 3. lines=%d" % len(lines))
