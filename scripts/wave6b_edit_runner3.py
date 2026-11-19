#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wave 6b: surgical line-based edits for Txh_RunnerTestov ObjectModule.bsl.

All Cyrillic is written as \\uXXXX escapes so the script source is pure ASCII
(inline Cyrillic in tool args proved unreliable for exact matching).

Operations (applied bottom-up so 1-based line numbers stay valid):
  - CEL x4: collapse blank runs 175-183, 246-247, 583-584, 626-627 to 1 blank
  - NonStandardRegion suppression pair around '#Область ВызовТестов' (L153)
  - Typo suppression pairs x6 around test-name comments/literals
    (L248, L256, L542, L550, L563, L571)
Every anchor line is asserted before mutation; any mismatch aborts untouched.
"""
import sys

PATH = ("src/cfe/\\u041f\\u043b\\u0430\\u043d\\u0438\\u0440\\u043e\\u0432\\u0430"
        "\\u043d\\u0438\\u0435\\u0422\\u0435\\u0445\\u043d\\u0438\\u043a\\u0438"
        "\\u0410\\u041f\\u041a/DataProcessors/\\u0422\\u0445_\\u0420\\u0430"
        "\\u043d\\u043d\\u0435\\u0440\\u0422\\u0435\\u0441\\u0442\\u043e\\u0432"
        "/Ext/ObjectModule.bsl")
PATH = PATH.encode().decode("unicode_escape")

# ---- escaped constants ------------------------------------------------
E_OBL = "\\u041e\\u0431\\u043b\\u0430\\u0441\\u0442\\u044c".encode().decode("unicode_escape")          # Область
E_VYZOV_TESTOV = ("\\u0412\\u044b\\u0437\\u043e\\u0432\\u0422\\u0435\\u0441"
                  "\\u0442\\u043e\\u0432").encode().decode("unicode_escape")                            # ВызовТестов
E_KONEC_PROC = ("\\u041a\\u043e\\u043d\\u0435\\u0446\\u041f\\u0440\\u043e\\u0446"
                "\\u0435\\u0434\\u0443\\u0440\\u044b").encode().decode("unicode_escape")                # КонецПроцедуры
E_OBERT = ("\\u041e\\u0431\\u0451\\u0440\\u0442\\u043a\\u0430 \\u0432\\u044b"
           "\\u0437\\u043e\\u0432\\u0430 \\u0442\\u0435\\u0441\\u0442\\u0430"
           ).encode().decode("unicode_escape")                                                          # Обёртка вызова теста
E_IMYA = "\\u0418\\u043c\\u044f\\u0422\\u0435\\u0441\\u0442\\u0430 = ".encode().decode("unicode_escape")# ИмяТеста = 

OFF_C = ("// BSLLS:Typo-off (\\u0438\\u043c\\u044f \\u0442\\u0435\\u0441\\u0442"
         "\\u0430 \\u0432 \\u043a\\u043e\\u043c\\u043c\\u0435\\u043d\\u0442"
         "\\u0430\\u0440\\u0438\\u0438 - \\u0442\\u0440\\u0430\\u0441\\u0441"
         "\\u0438\\u0440\\u043e\\u0432\\u043a\\u0430 \\u043d\\u0430 \\u0441"
         "\\u0446\\u0435\\u043d\\u0430\\u0440\\u0438\\u0439 \\u043f\\u0440"
         "\\u043e\\u0433\\u043e\\u043d\\u0430)").encode().decode("unicode_escape")

OFF_L1 = ("\t// BSLLS:Typo-off (\\u044d\\u0442\\u0430\\u043b\\u043e\\u043d"
          "\\u043d\\u044b\\u0439 \\u043b\\u0438\\u0442\\u0435\\u0440\\u0430"
          "\\u043b \\u0438\\u043c\\u0435\\u043d\\u0438 \\u0442\\u0435\\u0441"
          "\\u0442\\u0430 - \\u0432\\u043d\\u0435\\u0448\\u043d\\u0438\\u0439"
          " \\u043a\\u043e\\u043d\\u0442\\u0440\\u0430\\u043a\\u0442,"
          ).encode().decode("unicode_escape")
OFF_L2 = ("\t// \\u0438\\u043c\\u044f \\u044d\\u043a\\u0441\\u043f\\u043e"
          "\\u0440\\u0442\\u043d\\u043e\\u0433\\u043e \\u043c\\u0435\\u0442"
          "\\u043e\\u0434\\u0430 \\u0422\\u0445_\\u0422\\u0435\\u0441\\u0442"
          "\\u044b \\u043c\\u0435\\u043d\\u044f\\u0442\\u044c \\u043d\\u0435"
          "\\u043b\\u044c\\u0437\\u044f)").encode().decode("unicode_escape")
ON = "// BSLLS:Typo-on"
ON_L = "\t// BSLLS:Typo-on"
ON_R = "// BSLLS:NonStandardRegion-on"

OFF_R1 = ("// BSLLS:NonStandardRegion-off (\\u043e\\u0431\\u0451\\u0440\\u0442"
          "\\u043a\\u0438 \\u0432\\u044b\\u0437\\u043e\\u0432\\u0430 \\u0442"
          "\\u0435\\u0441\\u0442\\u043e\\u0432 - \\u043d\\u0435-\\u044d\\u043a"
          "\\u0441\\u043f\\u043e\\u0440\\u0442\\u043d\\u044b\\u0435 \\u043c"
          "\\u0435\\u0442\\u043e\\u0434\\u044b;").encode().decode("unicode_escape")
OFF_R2 = ("// \\u0441\\u0442\\u0430\\u043d\\u0434\\u0430\\u0440\\u0442\\u043d"
          "\\u043e\\u0435 \\u0438\\u043c\\u044f \\u043e\\u0431\\u043b\\u0430"
          "\\u0441\\u0442\\u0438 \\u0421\\u043b\\u0443\\u0436\\u0435\\u0431"
          "\\u043d\\u044b\\u0435\\u041f\\u0440\\u043e\\u0446\\u0435\\u0434"
          "\\u0443\\u0440\\u044b\\u0418\\u0424\\u0443\\u043d\\u043a\\u0446"
          "\\u0438\\u0438 \\u0443\\u0436\\u0435 \\u0437\\u0430\\u043d\\u044f"
          "\\u0442\\u043e \\u0432 \\u044d\\u0442\\u043e\\u043c \\u043c\\u043e"
          "\\u0434\\u0443\\u043b\\u0435,").encode().decode("unicode_escape")
OFF_R3 = ("// \\u043f\\u043e\\u0432\\u0442\\u043e\\u0440 \\u0434\\u0430\\u0435"
          "\\u0442 DuplicateRegion, \\u043f\\u0435\\u0440\\u0435\\u0438\\u043c"
          "\\u0435\\u043d\\u043e\\u0432\\u0430\\u043d\\u0438\\u0435 \\u043b"
          "\\u043e\\u043c\\u0430\\u0435\\u0442 \\u0440\\u0443\\u0431\\u0440"
          "\\u0438\\u043a\\u0430\\u0446\\u0438\\u044e)").encode().decode("unicode_escape")

raw = open(PATH, "rb").read()
bom = raw.startswith(b"\xef\xbb\xbf")
text = raw.decode("utf-8-sig")
NL = "\r\n" if "\r\n" in text else "\n"
assert "\r" not in text.replace("\r\n", ""), "stray CR"
text = text.replace("\r\n", "\n")
lines = text.split("\n")
if lines and lines[-1] == "":
    lines.pop()  # trailing newline marker; re-add on save


def L(n):  # 1-based get
    return lines[n - 1]


def check(cond, msg):
    if not cond:
        print("ANCHOR FAIL: " + msg)
        sys.exit(1)


# ---- anchors -----------------------------------------------------------
check(L(153) == "#" + E_OBL + " " + E_VYZOV_TESTOV, "L153 region header")
check(L(174) == E_KONEC_PROC, "L174")
for n in range(175, 184):
    check(L(n) == "", "L%d blank" % n)
check(L(184).startswith("// " + E_OBERT), "L184 comment")
check(L(245) == E_KONEC_PROC, "L245")
check(L(246) == "" and L(247) == "", "L246-247")
check(L(248).startswith("// " + E_OBERT), "L248 comment")
check(E_IMYA in L(256), "L256 literal")
check(L(542).startswith("// " + E_OBERT), "L542 comment")
check(E_IMYA in L(550), "L550 literal")
check(L(563).startswith("// " + E_OBERT), "L563 comment")
check(E_IMYA in L(571), "L571 literal")
check(L(583) == "" and L(584) == "", "L583-584")
check(L(585).startswith("// " + E_OBERT), "L585 comment")
check(L(626) == "" and L(627) == "", "L626-627")
check(L(628).startswith("// " + E_OBERT), "L628 comment")

# ---- operations (bottom-up) --------------------------------------------
def ins_before(n, new_lines):
    lines[n - 1:n - 1] = new_lines


def ins_after(n, new_lines):
    lines[n:n] = new_lines


def delete(n):
    del lines[n - 1]


# CEL 626-627
delete(627)
# CEL 583-584
delete(584)
# Typo pair around L571 literal
ins_after(571, [ON_L])
ins_before(571, [OFF_L1, OFF_L2])
# Typo pair around L563 comment
ins_after(563, [ON])
ins_before(563, [OFF_C])
# Typo pair around L550 literal
ins_after(550, [ON_L])
ins_before(550, [OFF_L1, OFF_L2])
# Typo pair around L542 comment
ins_after(542, [ON])
ins_before(542, [OFF_C])
# Typo pair around L256 literal
ins_after(256, [ON_L])
ins_before(256, [OFF_L1, OFF_L2])
# Typo pair around L248 comment
ins_after(248, [ON])
ins_before(248, [OFF_C])
# CEL 246-247
delete(247)
# CEL 175-183 -> keep 175
for n in range(176, 184):
    delete(176)
# Region pair around L153
ins_after(153, [ON_R])
ins_before(153, [OFF_R1, OFF_R2, OFF_R3])

out = NL.join(lines) + NL
data = out.encode("utf-8")
if bom:
    data = b"\xef\xbb\xbf" + data
open(PATH, "wb").write(data)
print("OK: edits applied, lines now=%d" % (len(lines) + 1))
