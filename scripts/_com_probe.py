import sys
import win32com.client

CONN_STRING = (
    "Srvr='localhost';Ref='dev_erpapk_demo';"
    "Usr='Администратор (ОрловАВ)';Pwd='';"
)

agent = win32com.client.Dispatch("V85.COMConnector").Connect(CONN_STRING)
print("[com] connected")

md = agent.Метаданные
procs = md.Обработки
print("total data processors:", procs.Количество())
names = []
for i in range(procs.Количество()):
    name = procs.Получить(i).Имя
    names.append(name)
tkh = [n for n in names if 'Тх' in n or 'Tkh' in n]
print("Tkh processors:", tkh)

# generic sanity: our other objects
for coll, key in (('РегистрыСведений', None), ('Документы', None), ('Отчеты', None), ('ОбщиеМодули', None)):
    try:
        c = getattr(md, coll)
        cnt = c.Количество()
        found = []
        for i in range(cnt):
            nm = c.Получить(i).Имя
            if 'Тх' in nm:
                found.append(nm)
        print(coll, cnt, 'Tkh:', found)
    except Exception as e:
        print(coll, 'ERR', e)
