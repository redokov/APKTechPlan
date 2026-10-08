#!/usr/bin/env python3
"""B6: replace code-fill steps with input+dropdown pattern in scenario 01."""
import io
import re

p = 'tests/vanessa/01-kojefficienty-bazovaya-model.feature'
s = io.open(p, encoding='utf-8', newline='').read()

patf = re.compile(
    r"\tИ я выполняю код встроенного языка\r\n"
    r"\t\| '(РаботаВвод|МодельСХТехники) = Тх_ТехникаСервер\.Тх_СсылкаПоНаименованию\(\"[^\"]+\", \"(Тх_Тест [^\"]+)\"\);' \|")

s = patf.sub(lambda m: (
    "И в поле с именем '%s' я ввожу текст '%s'\r\n"
    "И из выпадающего списка с именем '%s' я выбираю точное значение '%s'"
    % (m.group(1), m.group(2), m.group(1), m.group(2))), s)

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('replaced, remaining code steps:', s.count('Тх_СсылкаПоНаименованию'))
