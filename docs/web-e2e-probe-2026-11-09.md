# Проба веб-клиента (E2E) по целевой ИБ dev_erpapk_demo — 2026-11-09

> Задача: определить, доступна ли опубликованная точка входа веб-клиента 1С для целевой ИБ
> `localhost\dev_erpapk_demo`. Если доступна — прогнать документированные smoke-пути по
> изменённому раннеру/формам и снять скриншоты/логи. Если нет — вернуть `NOT_AVAILABLE`
> с доказательствами. Apache и конфигурацию публикации не менять.
>
> Итоговый статус: **NOT_AVAILABLE** (публикации целевой ИБ нет на этой машине).
>
> Разрешённая зона правок: `C:/MyProjects/APKTechPlan/docs` (+ `heartbeat/night.log`).
> Файлы конфигурации, метаданные, Apache, публикации, БД не изменялись.

## 1. Объект проверки (изменённые артефакты safe-lane spec-003)

Smoke-путь веб-клиента имел смысл только для этих изменённых артефактов (`git diff --stat HEAD`):

| Артефакт | Путь | Проверяемость через веб-клиент |
|---|---|---|
| Раннер VA (host-side) | `scripts/run_va_feature.py` | нет — консольный Python-скрипт |
| Раннер VA suite (host-side) | `scripts/run_all_va.py` | нет — консольный Python-скрипт |
| Раннер юнит-тестов (host-side) | `scripts/run_unit_tests.py` | нет — консольный Python-скрипт |
| Обработка `Тх_РаннерТестов` (объектный модуль) | `src/cfe/ПланированиеТехникиАПК/DataProcessors/Тх_РаннерТестов/Ext/ObjectModule.bsl` | да — форма обработки |
| Форма `Тх_РаннерТестов.Форма` | `.../Forms/Форма/Ext/Form.xml` + `.../Form/Module.bsl` | да — форма обработки |
| Общий модуль `Тх_Тесты` | `.../CommonModules/Тх_Тесты/Ext/Module.bsl` | косвенно (вызывается формой) |
| Общий модуль `Тх_ТехникаСервер` | `.../CommonModules/Тх_ТехникаСервер/Ext/Module.bsl` | косвенно (расчёт) |

Планируемые smoke-пути (не выполнены — точки входа нет, см. §3):
1. Открыть `Обработка.Тх_РаннерТестов.Форма` в веб-клиенте → команда «ВыполнитьТесты» →
   проверить различимость счётчиков PASS/FAIL/SKIP (ремедиация review P0-1/P1-6).
2. Прогнать неархивные сценарии Vanessa 01–09 через веб-клиент (тот же контракт статуса,
   что и в консольном прогоне 9/9 PASS от 2026-11-09).

## 2. Что проверялось (read-only)

Проверки только читающие: службы, слушающие порты, конфигурация запущенного Apache,
наличие файлов публикации `default.vrd`, HTTP-пробы. Команды и фактические ответы приведены
дословно.

```powershell
Get-Service | Where-Object {$_.Name -match 'Apache|1C|postgres'}
# Apache                Running
# Apache2.4             Stopped
# 1C:Enterprise 8.5 Server Agent (x86-64) Running
# pgsql-18.3-5.1C-x64   Running

Get-CimInstance Win32_Service | Where-Object {$_.Name -match 'Apache'} | Select Name,State,PathName
# Apache    Running  "C:\Users\r.edokov\AppData\Roaming\Apache24\bin\httpd.exe" -k runservice
# Apache2.4 Stopped  "c:\apache\bin\httpd.exe" -k runservice
```

Конфигурация **запущенного** Apache (`%APPDATA%\Apache24\conf\httpd.conf`, read-only):

```text
Listen 8081
DocumentRoot "${SRVROOT}/htdocs"
Include conf/extra/httpd-ahssl.conf        # -> Listen 443 https, VirtualHost _default_:443, DocumentRoot ${SRVROOT}/htdocs
ScriptAlias /cgi-bin/ "${SRVROOT}/cgi-bin/"
```

В конфигурации нет ни одного `Alias` на каталог публикаций 1С, нет `Publish`/`vrd`
(проверено `grep -i "publish|vrd|neirodoc|erpapk" httpd.conf` → пусто).
Содержимое document root: `htdocs/index.html` — единственный файл.

Слушающие порты (HTTP-подобные) на машине:

```text
0.0.0.0:443    httpd    (запущенный %APPDATA%\Apache24, SSL)
0.0.0.0:8081   httpd    (тот же процесс 4836)
0.0.0.0:8080   java     (Jenkins 2.375.3: Server: Jetty(10.0.12), HTTP 403 "Authentication required")
0.0.0.0:1540   ragent   } кластер 1С — бинарный протокол,
0.0.0.0:1541   rmngr    } не HTTP-веб-клиент
0.0.0.0:1545   ras      }
0.0.0.0:1560/1561/1562+ rmlic/rphost/dbda
```

Порт 80: слушателя нет (`curl http://localhost/` → код `000`, curl exit 7).
IIS отсутствует: `Get-Service W3SVC` → `NO_IIS`.

Файлы публикации 1С на диске (поиск `*.vrd` в глубину 5 от `C:\`, плюс `C:\MyProjects`, `C:\inetpub`):

```text
C:\1cweb\apache24\publish\erpuh\default.vrd          ib=komus_erpuh
C:\1cweb\apache24\publish\erpuh3\default.vrd         base=/erpuh3, ib=File="C:\MyProjects\bases\komus_test"
C:\1cweb\apache24\publish\komus_test\default.vrd
C:\1cweb\apache24\publish\testlocal\default.vrd
C:\1cweb\apache24_854\publish\{erpuh3,erpuhdemo,komus_test,testlocal}\default.vrd
C:\1cweb\apache24_demo\publish\{erpuh3,erpuhdemo,testlocal}\default.vrd
C:\1cweb\apache24_srv\publish\erpuh3\default.vrd     ib=Srvr="10.10.0.1";Ref="komus_erpuh3"
C:\1cweb\apache24_srv\publish\erpuhdemo\default.vrd
C:\1cweb\apache24_srv\publish\testlocal\default.vrd
C:\1cweb\erpuh3\default.vrd                          ib=komus_erpuh3
C:\Apache\publish\neirodoc\default.vrd               base=/neirodoc, ib=Srvr="localhost";Ref="dev_neirodoc_x"
C:\MyProjects\komus\docs\tools\apache24\publish\erpuh3\default.vrd
```

Ни один `default.vrd` не ссылается на `dev_erpapk_demo`:
`grep -l -i "erpapk" <все найденные *.vrd>` → пусто.
Все каталоги `C:\1cweb\*` не обслуживаются ни одним запущенным веб-сервером
(единственные процессы `httpd.exe` — pid 4836/6204 службы `Apache` из `%APPDATA%\Apache24`).
Служба `Apache2.4` (`c:\apache`, публикация `dev_neirodoc_x`) остановлена.

## 3. HTTP-пробы точек входа (read-only)

```bash
for u in "https://localhost/neirodoc/" "https://localhost/neirodoc/default.vrd" \
         "https://localhost/dev_erpapk_demo/" "https://localhost/erpapk_demo/" \
         "https://localhost/apktechplan/" "https://localhost/PlanirovanieTehnikiAPK/" \
         "http://localhost:8081/neirodoc/" "http://localhost:8081/dev_erpapk_demo/" \
         "https://localhost/erpuh3/" "https://localhost/testlocal/" "https://localhost/erpuhdemo/" \
         "http://localhost:8081/erpuh3/" ; do
  curl -s -k -o /tmp/body.txt -w "%{http_code}\n" --max-time 8 "$u"
done
```

Фактический результат:

| URL | HTTP |
|---|---|
| `https://localhost/dev_erpapk_demo/` | 404 |
| `https://localhost/erpapk_demo/` | 404 |
| `https://localhost/apktechplan/` | 404 |
| `https://localhost/PlanirovanieTehnikiAPK/` | 404 |
| `http://localhost:8081/dev_erpapk_demo/` | 404 |
| `https://localhost/neirodoc/` | 404 |
| `https://localhost/neirodoc/default.vrd` | 404 |
| `http://localhost:8081/neirodoc/` | 404 |
| `https://localhost/erpuh3/`, `/testlocal/`, `/erpuhdemo/` | 404 |
| `http://localhost:8081/erpuh3/` | 404 |
| `http://localhost:8081/` (корень) | 200 — статическая страница Apache (`htdocs/index.html`) |
| `https://localhost/` (корень) | 200 — та же статическая страница |
| `http://localhost/` (порт 80) | нет соединения (curl exit 7) |

Тело всех ответов 404 — стандартная страница Apache `"<h1>Not Found</h1>"` (196 байт),
то есть запрос не доходит до расширения веб-сервера 1С.

## 4. Вывод

**NOT_AVAILABLE.** Причина (цепочка доказательств):

1. Целевая ИБ поднята только на кластере 1С (`Srvr=localhost;Ref=dev_erpapk_demo`,
   порты 1540/1541/1545) — это не HTTP-веб-клиент.
2. На машине нет файла публикации `default.vrd` для `dev_erpapk_demo` ни в одном
   из найденных каталогов публикаций.
3. Единственный запущенный веб-сервер (`%APPDATA%\Apache24`, порты 443/8081) отдаёт
   статический `htdocs` и не имеет `Alias`, `DocumentRoot`-подкаталога или `vrd`,
   ведущих к публикации 1С; любой путь публикации даёт 404.
4. Второй экземпляр (`c:\apache`, публикация `dev_neirodoc_x`) остановлен, и его
   публикация относится к другой ИБ.
5. Порт 80 свободен, IIS отсутствует, порт 8080 занят Jenkins (не 1С).

Проверить изменённую форму `Тх_РаннерТестов` и сценарии 01–09 через веб-клиент физически
невозможно: нет ни одной HTTP-точки входа, обслуживающей `dev_erpapk_demo`.
Статус PASS не заявляется; smoke-пути не выполнялись, скриншоты веб-клиента не снимались
(снимать нечего — 404-страница Apache не является UI 1С).

## 5. Что не выполнялось (сознательно)

- не изменялись `httpd.conf`, `httpd-ahssl.conf`, службы Apache (ни запуск, ни остановка);
- не выполнялись `webinst -publish` / `-delete`, не создавались каталоги публикаций и `default.vrd`;
- не выполнялись вход в веб-клиент, Vanessa-прогоны, COM/Designer/БД-операции;
- не изменялись BSL/XML, метаданные, роли, конфигурация и расширение.

## 6. Что нужно, чтобы веб-E2E стал возможен (решение владельца, не выполнено)

1. Разрешить операцию публикации (отдельный авторизованный шаг, вне текущей зоны правок):
   `webinst -publish -iis -wsdir <site> -dir <path> -connstr "Srvr=\"localhost\";Ref=\"dev_erpapk_demo\";" ...`
   либо публикация через `c:\apache` (`Apache2.4`) с запуском этой службы.
2. После публикации проверить `GET https://localhost/<site>/` → должен отдаться
   стартовый экран 1С (не 404) и `default.vrd` с `Ref="dev_erpapk_demo"`.
3. Затем прогнать smoke-путь §1 и снять скриншоты через chrome-devtools/playwright.

## 7. Артефакты прогона

- этот документ — единственный записанный артефакт пробы;
- строка статуса добавлена в `heartbeat/night.log`;
- консольные логи Vanessa от 2026-11-09 (`heartbeat/va_*`) относятся к ранее выполненному
  desktop-прогону (TestClient/COM), а не к веб-клиенту.
