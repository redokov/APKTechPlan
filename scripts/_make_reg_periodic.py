import io, sys, glob, re
sys.stdout.reconfigure(encoding='utf-8')
p = glob.glob('src/cfe/**/InformationRegisters/Тх_КоэффициентыПересчетаРабот.xml', recursive=True)[0]
t = io.open(p, encoding='utf-8-sig').read()

# 1. remove the "Period" dimension block
i = t.find('<Dimension uuid=')
j = t.find('</Dimension>', i) + len('</Dimension>')
# consume trailing newline
while j < len(t) and t[j] in '\r\n':
    j += 1
block = t[i:j]
assert '<Name>Период</Name>' in block, 'first dimension is not Period: ' + block[:200]
t = t[:i] + t[j:]
print('removed Period dimension block (%d chars)' % len(block))

# 2. periodicity
assert '<InformationRegisterPeriodicity>Nonperiodical</InformationRegisterPeriodicity>' in t
t = t.replace('<InformationRegisterPeriodicity>Nonperiodical</InformationRegisterPeriodicity>',
              '<InformationRegisterPeriodicity>Day</InformationRegisterPeriodicity>')
print('periodicity -> Day')

# 3. main filter on period
assert '<MainFilterOnPeriod>false</MainFilterOnPeriod>' in t
t = t.replace('<MainFilterOnPeriod>false</MainFilterOnPeriod>',
              '<MainFilterOnPeriod>true</MainFilterOnPeriod>')
print('MainFilterOnPeriod -> true')

# 4. comment
old_comment = ('<Comment>Коэффициенты пересчёта работ по моделям техники (design §4.3, TD-004). '
               'Режим записи — независимый, непериодический: «Период» — измерение «действует с».</Comment>')
if old_comment in t:
    new_comment = ('<Comment>Коэффициенты пересчёта работ по моделям техники (design §4.3, TD-004). '
                   'Режим записи — независимый, периодический (день): стандартный реквизит «Период» = «действует с». '
                   'Periodic, т.к. платформа запрещает измерение с именем «Период» (B2, 2026-10-08).</Comment>')
    t = t.replace(old_comment, new_comment)
    print('comment updated')
else:
    print('comment not found verbatim - skip (non-blocking)')

# dimension count check
assert len(re.findall(r'<Dimension uuid=', t)) == 3, 'expected 3 dimensions left'
io.open(p, 'w', encoding='utf-8-sig', newline='').write(t)
print('written; dimensions left:', len(re.findall(r'<Dimension uuid=', t)))
