#!/usr/bin/env python3
"""B6 probe: does RecordManager.Записать() trigger the record-set BeforeWrite
validation? Writes 1 basic row via record SET, then a 2nd basic row via
RECORD MANAGER (same work/period/kind). If set events fire for the manager
write, the 2nd write is rejected (FR-003). Result -> heartbeat/b6_rmprobe3.txt
"""
import datetime

import win32com.client

c = win32com.client.Dispatch("V85.COMConnector")
a = c.Connect(
    "Srvr='localhost';Ref='dev_erpapk_demo';Usr='Администратор (ОрловАВ)';Pwd='';"
)
out = open("heartbeat/b6_rmprobe3.txt", "w", encoding="utf-8")

w = a.Справочники.ВидыРаботСотрудников.НайтиПоНаименованию("Тх_Тест Работа")
mb = a.Справочники.АпкМоделиСХТехники.НайтиПоНаименованию("Тх_Тест Базовая")
ma = a.Справочники.АпкМоделиСХТехники.НайтиПоНаименованию("Тх_Тест Аналог")
vt = a.Перечисления.Тх_ВидыТехники.Схтехника
out.write("refs: work=%s basic=%s analog=%s\n" % (w, mb, ma))

period = datetime.datetime(2025, 1, 1)

# clean slate: delete all rows for the test work
q = a.NewObject(
    "Запрос",
    "ВЫБРАТЬ К.Период, К.МодельТехники, К.Коэффициент, К.БазоваяМодель "
    "ИЗ РегистрСведений.Тх_КоэффициентыПересчетаРабот КАК К ГДЕ К.Работа = &Работа",
)
q.УстановитьПараметр("Работа", w)


def dump_state(tag):
    t = q.Выполнить().Выгрузить()
    out.write("[%s] rows=%d\n" % (tag, t.Количество()))
    for i in range(t.Количество()):
        r = t.Получить(i)
        out.write(
            "  %s | %s | basic=%s k=%s\n"
            % (r.Период, r.МодельТехники, r.БазоваяМодель, r.Коэффициент)
        )


dump_state("before")

# 1) basic row via RECORD SET (validation must set K=1 and accept)
rs = a.РегистрыСведений.Тх_КоэффициентыПересчетаРабот.СоздатьНаборЗаписей()
rs.Отбор.Работа.Установить(w)
rs.Отбор.Период.Установить(period)
rec = rs.Добавить()
rec.Период = period
rec.Работа = w
rec.ВидТехники = vt
rec.МодельТехники = mb
rec.БазоваяМодель = True
rec.Коэффициент = 2.0  # must be forced to 1 by the handler
try:
    rs.Записать()
    out.write("[set write] OK\n")
except Exception as e:
    out.write("[set write] REJECTED: %s\n" % str(e)[:400])
dump_state("after set write")

# 2) second basic row via RECORD MANAGER (same work+period+kind, analog model)
rm = a.РегистрыСведений.Тх_КоэффициентыПересчетаРабот.СоздатьМенеджерЗаписи()
rm.Период = period
rm.Работа = w
rm.ВидТехники = vt
rm.МодельТехники = ma
rm.БазоваяМодель = True
rm.Коэффициент = 1.0
try:
    rm.Записать()
    out.write("[manager write] OK (NOT rejected!)\n")
except Exception as e:
    out.write("[manager write] REJECTED: %s\n" % str(e)[:400])
dump_state("after manager write")

out.close()
print("done")
