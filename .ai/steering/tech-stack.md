# Tech Stack

- Платформа 1С:Предприятие 8.5 (8.5.4.1683), сервер localhost.
- База разработки: Srvr="localhost";Ref="dev_erpapk_demo"; пользователь Администратор, без пароля.
- Конфигурация = 1С:ERP (исходники C:/MyProjects/ERPsrc) + модуль АПК 2.5
  (исходники C:/MyProjects/APKModSrc). Полной выгрузки ЕРП АПК нет — используем оба набора.
- Продукт = расширение конфигурации (CFE), исходники в src/cfe/<ИмяРасширения>/ проекта.
- Пайплайн правки: pre_load_validate.py → bsl-ls (MCP) → db-load-xml (Designer batch,
  -Extension <имя> -UpdateDB) → round-trip verify.
- Тесты: модульные (серверные, headless через COM/ Automation), сценарные (Vanessa BDD,
  .feature + step definitions), e2e (веб-клиент через Chrome DevTools, публикация Apache).
- Вики по функциональности АПК: C:/MyProjects/APKTechPlan/wiki (raw/md — 261 страница ИТС apkmod25).
- 1cv8.exe: C:\Program Files\1cv8\8.5.4.1683\bin
