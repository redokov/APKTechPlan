#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T9: сборка зондирующего EPF «Тх_ЗондОткрытияФормы».

/Execute открывает форму зонда, её ПриОткрытии программно открывает форму
обработки расширения «Тх_ФормированиеПланаРаботТехники» (команды в разделе
ещё нет - T10). Кириллица не проходит через bash-argv: все вызовы инструментов
через subprocess (список аргументов, W-API), файлы - UTF-8 (BOM где канон).

Шаги: epf-init -> form-add (Object, default) -> правка Form.xml (без
атрибутов, заголовок) -> модуль ПриОткрытии -> epf-build (временная база).
"""
import pathlib
import subprocess
import sys

SK = pathlib.Path(r"C:/MyProjects/PiPack/skills/1c")
SRC = pathlib.Path("src/epf")
OUT = pathlib.Path("build")
NAME = "\u0422\u0445_\u0417\u043e\u043d\u0434\u041e\u0442\u043a\u0440\u044b\u0442\u0438\u044f\u0424\u043e\u0440\u043c\u044b"
V8 = r"C:\Program Files\1cv8\8.5.4.1683\bin"

def run(cmd, **kw):
    print("+", " ".join(str(c) for c in cmd[:3]), "...")
    r = subprocess.run([str(c) for c in cmd], capture_output=True, timeout=900, **kw)
    out = r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")
    print("  rc=%s tail=%s" % (r.returncode, out[-400:].replace("\n", " | ")))
    if r.returncode != 0:
        sys.exit("FAILED step")
    return out

MODULE = (
    "\ufeff&\u041d\u0430\u041a\u043b\u0438\u0435\u043d\u0442\u0435\n"
    "\u041f\u0440\u043e\u0446\u0435\u0434\u0443\u0440\u0430 \u041f\u0440\u0438\u041e\u0442\u043a\u0440\u044b\u0442\u0438\u0438(\u041e\u0442\u043a\u0430\u0437)\n"
    "\n"
    "\t// T9 UI-\u0437\u043e\u043d\u0434: /Execute \u043e\u0442\u043a\u0440\u044b\u0432\u0430\u0435\u0442 \u044d\u0442\u0443 \u0444\u043e\u0440\u043c\u0443, \u043e\u043d\u0430 \u043e\u0442\u043a\u0440\u044b\u0432\u0430\u0435\u0442 \u0444\u043e\u0440\u043c\u0443\n"
    "\t// \u043e\u0431\u0440\u0430\u0431\u043e\u0442\u043a\u0438 \u0440\u0430\u0441\u0448\u0438\u0440\u0435\u043d\u0438\u044f \u0438 \u043e\u0441\u0442\u0430\u0451\u0442\u0441\u044f \u0432 \u0444\u043e\u043d\u0435.\n"
    "\t\u041e\u0442\u043a\u0440\u044b\u0442\u044c\u0424\u043e\u0440\u043c\u0443("
    "\"\u041e\u0431\u0440\u0430\u0431\u043e\u0442\u043a\u0430."
    "\u0422\u0445_\u0424\u043e\u0440\u043c\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435\u041f\u043b\u0430\u043d\u0430\u0420\u0430\u0431\u043e\u0442\u0422\u0435\u0445\u043d\u0438\u043a\u0438."
    "\u0424\u043e\u0440\u043c\u0430\");\n"
    "\n"
    "\u041a\u043e\u043d\u0435\u0446\u041f\u0440\u043e\u0446\u0435\u0434\u0443\u0440\u044b\n")

def main():
    # 1. init
    run([sys.executable, SK / "epf-init/scripts/init.py",
         "-Name", NAME, "-Synonym", NAME, "-SrcDir", SRC])
    root_xml = SRC / (NAME + ".xml")
    assert root_xml.exists(), "root xml not found after init: %s" % root_xml
    print("root xml:", root_xml)

    # 2. form-add
    run([sys.executable, SK / "form-add/scripts/form-add.py",
         "-ObjectPath", root_xml, "-FormName",
         "\u0424\u043e\u0440\u043c\u0430", "-Synonym",
         "\u0424\u043e\u0440\u043c\u0430", "-Purpose", "Object", "-SetDefault"])

    # 3. правка Form.xml: убрать блок Attributes, добавить Title
    form_xml = SRC / NAME / "Forms" / "\u0424\u043e\u0440\u043c\u0430" / "Ext" / "Form.xml"
    assert form_xml.exists(), form_xml
    b = form_xml.read_bytes()
    if b[:3] == b"\xef\xbb\xbf":
        b = b[3:]
    t = b.decode("utf-8")
    # удалить Attributes-блок (реквизит Объект от form-add не нужен)
    import re
    t2 = re.sub(r"\t*<Attributes>.*?</Attributes>\n?", "", t, flags=re.S)
    assert t2 != t, "Attributes block not found"
    # Title перед AutoCommandBar
    if "<Title>" not in t2:
        t2 = t2.replace("<AutoCommandBar",
                        "<Title><v8:item><v8:lang>ru</v8:lang>"
                        "<v8:content>" + NAME + "</v8:content></v8:item></Title>\n\t\t<AutoCommandBar", 1)
    form_xml.write_bytes(b"\xef\xbb\xbf" + t2.encode("utf-8"))
    print("form xml patched")

    # 4. модуль формы (канонический путь: Ext/Form/Module.bsl, CRLF)
    mod = SRC / NAME / "Forms" / "\u0424\u043e\u0440\u043c\u0430" / "Ext" / "Form" / "Module.bsl"
    mod.parent.mkdir(parents=True, exist_ok=True)
    mod.write_bytes(MODULE.replace("\n", "\r\n").encode("utf-8"))
    stray = mod.parent.parent / "Module.bsl"
    if stray.exists():
        stray.unlink()
    print("module written:", mod)

    # 5. build
    OUT.mkdir(exist_ok=True)
    out_epf = OUT / (NAME + ".epf")
    run([sys.executable, SK / "epf-build/scripts/epf-build.py",
         "-V8Path", V8, "-SourceFile", root_xml, "-OutputFile", out_epf])
    assert out_epf.exists() and out_epf.stat().st_size > 1000, "epf too small"
    print("OK:", out_epf, out_epf.stat().st_size, "bytes")

if __name__ == "__main__":
    main()
