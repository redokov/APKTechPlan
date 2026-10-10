# -*- coding: utf-8 -*-
# T11: switch Тх_ДефицитТехники СКД from query parameters (broken
# «&П ЕСТЬ NULL» semantics on 8.5) to settings filters (отборы).
# - query: drop the whole ГДЕ block (9 param conditions)
# - schema: drop <parameters> (9 params)
# - settings: drop <dcsset:dataParameters>, insert <dcsset:filter> with
#   user-setting filters incl. enabled «НехватаетСмен > 0» (ТолькоДефицит)
import io, re

f = 'src/cfe/ПланированиеТехникиАПК/Reports/Тх_ДефицитТехники/Templates/ОсновнаяСхемаКомпоновкиДанных/Ext/Template.xml'
d = io.open(f, encoding='utf-8').read()

# 1. Remove ГДЕ block from the dataset query
i = d.find(u'ГДЕ\n')
j = d.find(u'</query>', i)
assert i > 0 and j > i, (i, j)
# remove trailing newline before </query> as well
seg = d[i:j]
d = d[:i] + d[j:]
print('query ГДЕ removed (%d chars)' % len(seg))

# 2. Remove flat schema <parameter> blocks (no <parameters> wrapper in this
# serialization form: parameters are top-level elements before <settingsVariant>)
i = d.find('<parameter>')
j = d.find('<settingsVariant>')
assert i > 0 and j > i, (i, j)
d = d[:i] + d[j:]
print('schema parameters removed')

# 3. Remove <dcsset:dataParameters> from settings
i = d.find('<dcsset:dataParameters>')
j = d.find('</dcsset:dataParameters>', i) + len('</dcsset:dataParameters>')
assert i > 0 and j > i
d = d[:i] + d[j:]
print('settings dataParameters removed')

# 4. Insert <dcsset:filter> right after <dcsset:settings ...> opening tag
m = re.search(r'<dcsset:settings[^>]*>', d)
assert m
insert_at = m.end()

def item(field, cmp, guid, use=True, right=None):
    s = ('\t\t\t<dcsset:item xsi:type="dcsset:FilterItemComparison">\n'
         '\t\t\t\t<dcsset:use>%s</dcsset:use>\n'
         '\t\t\t\t<dcsset:left xsi:type="dcscor:Field">%s</dcsset:left>\n'
         '\t\t\t\t<dcsset:comparisonType>%s</dcsset:comparisonType>\n' % ('true' if use else 'false', field, cmp))
    if right is not None:
        s += '\t\t\t\t<dcsset:right xsi:type="xs:decimal">%s</dcsset:right>\n' % right
    s += ('\t\t\t\t<dcsset:userSettingID>%s</dcsset:userSettingID>\n'
          '\t\t\t</dcsset:item>\n' % guid)
    return s

items = (
    item('Организация',          'Equal',          'a1b2c3d4-1111-4a11-9a11-000000000001', use=False) +
    item('Подразделение',        'Equal',          'a1b2c3d4-1111-4a11-9a11-000000000002', use=False) +
    item('СценарийПланирования', 'Equal',          'a1b2c3d4-1111-4a11-9a11-000000000003', use=False) +
    item('ПериодНачала',         'GreaterOrEqual', 'a1b2c3d4-1111-4a11-9a11-000000000004', use=False) +
    item('ПериодОкончания',      'LessOrEqual',    'a1b2c3d4-1111-4a11-9a11-000000000005', use=False) +
    item('ВидРаботы',            'Equal',          'a1b2c3d4-1111-4a11-9a11-000000000006', use=False) +
    item('МодельТехники',        'Equal',          'a1b2c3d4-1111-4a11-9a11-000000000007', use=False) +
    item('ВидТехники',           'Equal',          'a1b2c3d4-1111-4a11-9a11-000000000008', use=False) +
    item('НехватаетСмен',        'Greater',        'a1b2c3d4-1111-4a11-9a11-000000000009', use=True, right='0')
)

filter_block = '\n\t\t\t<dcsset:filter>\n' + items + '\t\t\t</dcsset:filter>'

d = d[:insert_at] + filter_block + d[insert_at:]
print('settings filter inserted (%d chars)' % len(filter_block))

io.open(f, 'w', encoding='utf-8', newline='').write(d)
print('SKD: params -> filters done')
