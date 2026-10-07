import sys
import win32com.client
sys.stdout.reconfigure(encoding='utf-8')
CONN = "Srvr='localhost';Ref='dev_erpapk_demo';Usr='Администратор (ОрловАВ)';Pwd='';"
agent = win32com.client.Dispatch("V85.COMConnector").Connect(CONN)
print('connected')

try:
    rs = agent.РегистрыСведений.ТестКроссСсылок_Регистр.СоздатьНаборЗаписей()
    print('ТестКроссСсылок_Регистр object: OK')
except Exception as e:
    print('ТестКроссСсылок_Регистр FAIL:', repr(e))

try:
    r = agent.Обработки.Тх_РаннерТестов.Создать()
    print('Тх_РаннерТестов: OK ->', r)
except Exception as e:
    print('Тх_РаннерТестов FAIL:', repr(e))

try:
    exts = agent.Метаданные.РасширенияКонфигурации
    print('extensions collection count:', exts.Количество())
    for i in range(exts.Количество()):
        ext = exts.Получить(i)
        print('  ext:', ext.Имя)
except Exception as e:
    print('extensions collection:', repr(e))
