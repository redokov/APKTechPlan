#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check form handler bindings: every handler method in Form/Module.bsl must be
referenced in Form.xml (event handler property or handlerName)."""
import re, glob, sys, io
sys.stdout = io.open('tmp_handlers.txt', 'w', encoding='utf-8')

for mod in glob.glob('src/cfe/ПланированиеТехникиАПК/**/Forms/*/Ext/Form/Module.bsl', recursive=True):
    form_xml = mod.replace('Form/Module.bsl', 'Form.xml')
    bsl = open(mod, encoding='utf-8-sig').read()
    xml = open(form_xml, encoding='utf-8').read()
    procs = re.findall(r'(?:Процедура|Функция)\s+([A-ЯA-Za-z_]\w+)', bsl)
    handlers = [p for p in procs if re.search(r'При(Изменении|Создании)|Перед(Записью|Открытием)|При(Открытии|Закрытии|Записи)|ПослеЗаписи|ОбработкаЗаполнения|НачалоВыбора|АвтоПодбор', p)]
    missing = []
    for h in handlers:
        if h not in xml:
            missing.append(h)
    print(('OK  ' if not missing else 'MISS') + ' ' + mod.replace('src/cfe/ПланированиеТехникиАПК/', '') + ('' if not missing else ' -> missing in xml: ' + ', '.join(missing)))
sys.stdout.close()
out = open('tmp_handlers.txt', encoding='utf-8').read()
import os, sys as s2
os.remove('tmp_handlers.txt')
s2.__stdout__.write(out.encode('ascii', 'backslashreplace').decode() + chr(10))
