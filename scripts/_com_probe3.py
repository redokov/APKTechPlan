import sys
import win32com.client

CONN = "Srvr='localhost';Ref='dev_erpapk_demo';Usr='Администратор (ОрловАВ)';Pwd='';"
agent = win32com.client.Dispatch("V85.COMConnector").Connect(CONN)
print('connected')

# 1) global context member from the session itself
try:
    rs = agent.РегистрыСведений
    print('agent.РегистрыСведений: OK ->', rs)
except Exception as e:
    print('agent.РегистрыСведений FAIL:', repr(e))

# 2) create a record set of our register (extension applied)
try:
    nr = agent.РегистрыСведений.Тх_КоэффициентыПересчетаРабот.СоздатьНаборЗаписей()
    print('СоздатьНаборЗаписей: OK ->', nr)
except Exception as e:
    print('СоздатьНаборЗаписей FAIL:', repr(e))

# 3) does an ExternalConnection common module see it? Тх_Тесты.НовыйКонтекстТеста exists?
try:
    m = agent.Обработки.Тх_РаннерТестов.Создать()
    print('runner: OK')
except Exception as e:
    print('runner FAIL:', repr(e))
