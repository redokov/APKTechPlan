# -*- coding: utf-8 -*-
# T11: flatten СКД settings of Тх_ДефицитТехники (detail fields can't be
# used inside groupings -> «Поле 'Дней периода' не может быть использовано
# в группировке 'Модель техники'»). Flat detail table, all columns + marks.
import io

f = 'src/cfe/ПланированиеТехникиАПК/Reports/Тх_ДефицитТехники/Templates/ОсновнаяСхемаКомпоновкиДанных/Ext/Template.xml'
d = io.open(f, encoding='utf-8').read()

start = d.find('\t\t\t<dcsset:item xsi:type="dcsset:StructureItemGroup">')
end = d.find('\t\t</dcsset:settings>')
assert start > 0 and end > start, (start, end)

def fld(name):
    return ('\t\t\t\t\t\t<dcsset:item xsi:type="dcsset:SelectedItemField">\n'
            '\t\t\t\t\t\t\t<dcsset:field>%s</dcsset:field>\n'
            '\t\t\t\t\t\t</dcsset:item>\n' % name)

fields = ['Подразделение', 'ПериодНачала', 'ПериодОкончания', 'ВидРаботы',
          'МодельТехники', 'ВидТехники', 'ПотребностьСмен', 'ДоступноСмен',
          'НехватаетСмен', 'ДнейПериода', 'СменВДень',
          'ПометкаКоэффициента', 'ПометкаПлана']

sel = ''.join(fld(x) for x in fields)

new_block = (
    '\t\t\t<dcsset:item xsi:type="dcsset:StructureItemGroup">\n'
    '\t\t\t\t<dcsset:order>\n'
    '\t\t\t\t\t<dcsset:item xsi:type="dcsset:OrderItemAuto"/>\n'
    '\t\t\t\t</dcsset:order>\n'
    '\t\t\t\t<dcsset:selection>\n'
    + sel +
    '\t\t\t\t</dcsset:selection>\n'
    '\t\t\t</dcsset:item>\n'
)

d = d[:start] + new_block + d[end:]
io.open(f, 'w', encoding='utf-8', newline='').write(d)
print('SKD settings flattened')
