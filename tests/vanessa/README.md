# Тесты Vanessa Automation (BDD)

Прогон одной фичи: `python scripts/run_va_feature.py tests/vanessa/<имя>.feature`
(скрипт принимает ровно один файл — без каталогов и тег-фильтров, см. `run_va_feature.py:49-55`).

VA-smoke входит в финальный гейт **только при интерактивной сессии (GUI)**.
В headless-сессии VA полностью исключается из гейтов (иначе ложные «регрессы»).

## Регресс: фичи, входящие в обязательный прогон

| Фича | Что проверяет | Приоритет |
|---|---|---|
| `01-zameshchenie-po-shirine.feature` | Замещение моделей по ширине обработки (FR-004) | smoke |
| `02-zameshchenie-po-moshchnosti.feature` | Замещение моделей по мощности (FR-004) | regression |
| `03-plan-tehresursov-prinyatye-tc.feature` | План техресурсов: только принятые ТС (FR-007) | regression |
| `04-preduprezhdenie-ts-dva-podrazdeleniya.feature` | Предупреждение о приёмке ТС в двух подразделениях | regression |
| `05-raschet-deficita-i-filtry-otcheta.feature` | Расчёт дефицита и фильтры отчёта | regression |
| `06-otchet-tolko-defitsitnye-stroki.feature` | Отчёт: только дефицитные строки | regression |
| `07-pometka-koeffitsient-ne-zadan.feature` | Пометка «коэффициент не задан» (FR-011) | regression |
| `08-formirovanie-plana-rabot-tekhniki.feature` | Формирование плана работ техники (FR-003) | regression |
| `09-prava-agronom.feature` | Права роли «Агроном» | regression |

## Архив (не входит в регресс)

Файлы в `archive/` — диагностические и разовые фичи, сохранены для истории.
Запускать вручную по одному при отладке соответствующей подсистемы.

| Фича | Причина изоляции |
|---|---|
| `archive/00-diag-choiceshot.feature` | Диагностический зонд (скриншоты выбора) |
| `archive/00-diag-drop.feature` | Диагностический зонд (drag&drop) |
| `archive/00-diag-form.feature` | Диагностический зонд (форма записи; ссылается на удалённый регистр) |
| `archive/00-diag-roli.feature` | Диагностический зонд (роли) |
| `archive/00-diag-typtype.feature` | Диагностический зонд (типы значений) |
| `archive/08-polzovatel-bez-rolej-ne-vidit.feature` | Разовый тест «без ролей не видит»; вынесен из регресса |

Теги `@skip` намеренно НЕ вводятся: `run_va_feature.py` не фильтрует по тегам
и каталогам (`sys.argv[1]` = один файл), архивация каталогом надёжнее.
