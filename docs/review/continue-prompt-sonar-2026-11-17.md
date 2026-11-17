# Продолжение: Sonar-fix волны 2–4 (APKTechPlan) — состояние на 2026-11-17, 19:00

Скопируй блок «ПРОМТ» ниже целиком в новую сессию pi, запущенную в
`C:\MyProjects\APKTechPlan`. Он самодостаточен.

---

## ПРОМТ (копировать отсюда)

Работай в репозитории `C:\MyProjects\APKTechPlan` (расширение CFE
`ПланированиеТехникиАПК`, исходники `src/cfe/ПланированиеТехникиАПК/`, тестовая ИБ
`dev_erpapk_demo` на `localhost`, пользователь `Администратор (ОрловАВ)`, пароль пустой).
Задача — **завершить** ночной прогон Sonar-fix (волны 2–4): довести верификацию до конца,
закоммитить и обновить отчёт. Кодовая часть уже сделана в предыдущей сессии —
**не переделывать**, только проверить и завершить.

### 0. Что уже сделано (не повторять)

Все **52** открытых замечания SonarQube из
`C:\MyProjects\ERPBandCIPipeline\build_logs\sonar_remaining_52_2026-11-16.json` закрыты в коде
(волна 2 — прод + тест-инфра, волна 4 — CI-конфиг). Рабочее дерево **не закоммичено**.

Изменённые файлы (`git status`):

```
 M jobConfiguration.json                                    (waitForQualityGate false -> true)
 M CommonModules/Тх_Тесты/Ext/Module.bsl                    (+15/-1)
 M CommonModules/Тх_ТехникаСервер/Ext/Module.bsl            (+912/-316)
 M DataProcessors/Тх_ЗапускVanessa/Ext/ObjectModule.bsl     (+3/-3)
 M DataProcessors/Тх_ПодготовкаТестовыхДанных/...bsl        (+8)
 M DataProcessors/Тх_РаннерТестов/Ext/ObjectModule.bsl      (+2/-2)
 M DataProcessors/Тх_ФормированиеПланаРаботТехники/…/Form/Module.bsl (+19/-2)
 M Reports/Тх_ДефицитТехники/Ext/ObjectModule.bsl           (+15/-2)
```

Новые файлы (untracked): `scripts/sonar_target_check.py`, `scripts/sonar_ls_diff.py`,
`docs/review/sonar-fix-night-run-2026-11-17.md` (итоговый отчёт, заполнен частично —
раздел §5 «Vanessa» пуст), артефакты в `tmp/night/` (в .gitignore или удалить перед коммитом).

### 1. Результаты уже выполненных проверок (переиспользовать, не перезапускать зря)

| Гейт | Результат | Где лог |
|---|---|---|
| BSL LS: целевые правила | все закрыты, **ни одно правило не выросло** | `scripts/sonar_ls_diff.py` → `tmp/night/lsbase`, `tmp/night/lsreport` |
| `bsl_balance_check.py` | `checked=17 broken=0` | — |
| `pre_load_validate.py` | `All CFE XML validated OK (29 files)` | — |
| Загрузка CFE + `UpdateDBCfg` | `OK: loaded + UpdateDBCfg` | `tmp/night/gateC_load.log` |
| Юнит-тесты | **31/31 PASS**, 0 SKIP, 0 FAIL (ожидаемое число тестов = **31**, не 20) | `tmp/night/gateC_unit.log` |
| Round-trip | файлов 46=46, сирот 0, `content REAL diffs = 2` — **предсуществующие** артефакты S10, не от правок | `tmp/night/rt_compare.log` |
| Vanessa (9 фич) | **НЕ ЗАВЕРШЕНО** — см. п.3 | `tmp/night/va_all.log` |
| Jenkins + Quality Gate | **недоступно** (VPN) | — |

Ключевые числа для отчёта: BSL LS диагностик было 448, стало 392;
`CognitiveComplexity 6→1` (осталась `РассчитатьДефицит` 22 — она **не входила** в 52),
`MagicNumber 7→0`, `Typo 10→5` (остались предсуществующие вне 52),
`QueryParseError 4→3` (остались предсуществующие вне 52), `DeprecatedMethodCall 2→0`,
`CyclomaticComplexity 2→0`, `JoinWithVirtualTable 1→0`, `LineLength 2→0`, `UsageWriteLogEvent 3→0`.

### 2. Переменные окружения и особенности машины (проверено, не переоткрывать)

- Платформа: автодетект `scripts/v8conf.py` → **`C:\Program Files\1cv8\8.5.4.2028\bin`**.
  Каталог `8.5.4.1683\bin` **выпотрошен** (только `sm-searcher`) — путь из `AGENTS.md` нерабочий.
- **COM-коннектор**: починен в этой сессии — `regsvr32` для
  `C:\Program Files\1cv8\8.5.4.2028\bin\comcntr.dll`
  (реестр `HKLM\SOFTWARE\Classes\TypeLib\{88511CA9-…}\1.0\0\win64` указывал на несуществующий
  `…1683\bin\comcntr.dll` → `TYPE_E_CANTLOADLIBRARY`). Если юнит-тесты снова падают с этой
  ошибкой — повторить `regsvr32`.
- **Всегда** `PYTHONIOENCODING=utf-8` и `PYTHONUTF8=1` для скриптов с кириллицей
  (иначе `UnicodeEncodeError: 'charmap'`).
- Одноразовый bash-вызов обрывается ~100 с → длинные операции только отсоединённо
  (`Start-Process` / фон) + короткие `tail`.
- Vanessa требует **интерактивного десктопа** (TestClient). Сессия интерактивная.
- Взвод автопродолжения (`~/.pi/agent/pi-billing-window-arms.json`) привязан к **сессии**:
  в новой сессии его надо взвести заново
  `python C:/Tools/pi-billing-window/scripts/arm_cont_after_reset.py "$PI_SESSION_FILE" --repeat 5 --ttl 20`.

### 3. Что осталось сделать (по порядку)

1. **Догнать Vanessa (9 фич).** Прогон дважды не доживал до конца: первый раз упал на
   `UnicodeEncodeError` (не был задан `PYTHONIOENCODING`), второй — `ensure_roles` не успевал
   (ему нужно >2 мин; `run_va_feature.py` даёт ему `timeout=300`, внешний `timeout` рвал).
   Фича 01 при этом **фактически прошла**: `heartbeat/va_status_01-zameshchenie-po-shirine.log`
   = BOM + `0`, а `va_1c_01-...log` = «Выполнение сценариев закончено. Ошибок не было.»
   Запускать так (отсоединённо, без обрыва по таймауту):

   ```bash
   cd /c/MyProjects/APKTechPlan
   rm -f tmp/night/va_all.log tmp/night/va_all.err
   powershell.exe -NoProfile -Command "\$env:PYTHONIOENCODING='utf-8'; \$env:PYTHONUTF8='1'; Start-Process -FilePath 'C:\Python312\python.exe' -ArgumentList '-u','scripts\run_all_va.py' -WorkingDirectory 'C:\MyProjects\APKTechPlan' -RedirectStandardOutput 'C:\MyProjects\APKTechPlan\tmp\night\va_all.log' -RedirectStandardError 'C:\MyProjects\APKTechPlan\tmp\night\va_all.err' -WindowStyle Hidden"
   ```

   Затем периодически (каждые 2–3 мин) `python -c "print(open('tmp/night/va_all.log','rb').read().decode('utf-8','replace')[-800:])"`.
   Прогноз: 9 фич × 2–6 мин ≈ 20–60 мин. Засчитывать строго по артефактам
   `heartbeat/va_status_<stem>.log` (BOM+`0` = PASS) и `heartbeat/va_1c_<stem>.log`
   («Ошибок не было»), НЕ по коду возврата процесса.
   Если фича падает — сначала проверить, не из-за ли окружения (роли `Тх_Чтение`/
   `Тх_Редактирование` сбрасываются БСП; `va_assign_roles_direct.py`), и только потом
   подозревать кодовые правки. При реальном регрессе — `git stash`/`git checkout` по
   конкретной функции и фиксация в отчёте.

2. **Заполнить §5 «Vanessa» в `docs/review/sonar-fix-night-run-2026-11-17.md`**
   (таблица stem → PASS/FAIL + суммарно `N/9`), затем обновить §4.

3. **Закоммитить** (3 коммита, стиль репозитория — `тип(скоуп): описание`):
   - `fix(sonar): замечания волны 2 в BSL (52 -> 0 в новом коде)` — 7 файлов `src/cfe/...`;
     в теле: что закрыто по правилам, что подавлено директивами и почему.
   - `fix(ci): ждать Quality Gate и не удалять report-task.txt` — `jobConfiguration.json`.
   - `docs(sonar): итоговый отчёт ночного прогона + скрипты сверки` — отчёт и
     `scripts/sonar_target_check.py`, `scripts/sonar_ls_diff.py`.
   Перед коммитом: `git status` (никакого `tmp/night/` и секретов), `git diff --check`.

4. **При подключённом VPN** — перезапустить пайплайн и подтвердить гейт:
   `POST /job/APKTechPlan/job/master/build` через
   `sys.path.insert(0, 'C:/MyProjects/ERPBandCIPipeline/scripts'); import jenkins_rest`,
   затем `GET /api/qualitygates/project_status?projectKey=APKTechPlan&branch=master`
   (Sonar `http://192.168.200.52:9090`, токен в
   `C:\MyProjects\ERPBandCIPipeline\secrets.sonar.env`, авторизация `auth=(token, '')`).
   Ожидание `new_violations = 0`. Если на изменённых строках всплывут
   `QueryToMissingMetadata` / `QueryParseError` по объектам **основной** конфигурации —
   помечать false positive (`POST /api/issues/bulk_change`, `do_transition=falsepositive`),
   это политика волны 1.

### 4. Жёсткие правила

- **Не переделывать** закрытые замечания и не «улучшать» заново отрефакторенные функции.
- **Не менять поведение** продовых функций: правки — только косметика/декомпозиция.
- **Не трогать** резолюции закрытых в волне 1 замечаний (wontfix / false positive / SAFE).
- **`jenkins-lib` не менять** (общая библиотека для всех пайплайнов): причина WARN
  `report-task.txt` — в проекте (`waitForQualityGate: false` → библиотека удаляла
  `.scannerwork` и не включала `-Dsonar.qualitygate.wait=true`); уже исправлено в
  `jobConfiguration.json` проекта.
- Подавления `// BSLLS:<Rule>-off/-on` в коде — осознанные и обоснованы в комментариях
  (динамические имена метаданных; намеренно сломанный запрос в тесте; мягкие ветки ЖР
  с уровнем «Предупреждение» по решению владельца; ручная компоновка отчёта). Не удалять.
- Длинные 1С-операции — только отсоединённо; не убивать `1cv8*` посреди эксклюзивных
  операций (skill `1c-destructive-ops-guard`).

### 5. Справочно: что именно закрыто (для отчёта)

- `DeprecatedMethods8317` (8) — `Краткое/ПодробноеПредставлениеОшибки` →
  `ОбработкаОшибок.*` (МенеджерОбработкиОшибок); `DeprecatedFind` → `СтрНайти`.
- `QueryParseError` (4) — ложные на динамических именах метаданных + намеренно
  сломанный запрос в тесте; подавлены директивами, тексты запросов не менялись.
- `CognitiveComplexity`/`CyclomaticComplexity`/`NestedStatements` (7) — декомпозиция:
  `ПостроитьКэшРеквизитовМоделей`, `ДоступныеМоделиПодразделения`, `ПодобратьЗамещение`,
  `ЗаполнитьТЧПланаРабот`, `ДоступностьСтрокиДвумяУровнями` (+ вспомогательные не-Экспорт
  подфункции; `КлючПодр` → `КлючПодразделения`).
- `JoinWithVirtualTable` — пакетный запрос: `ПОМЕСТИТЬ … ИНДЕКСИРОВАТЬ ПО` + соединение
  с временной таблицей (результат идентичен).
- `MagicNumber`/`MagicDate` — именованные переменные (`ТочностьОкругленияСмен`,
  `МиллисекундВСекунде`, `МаксимальнаяДатаПлана = Дата(3999,12,31)`, `СекундВСутках`).
- `LineLength`, `NestedFunctionInParameters`, `NumberOfValuesInStructureConstructor`,
  `CodeOutOfRegion`/`EventHandlerOutsideEventRegion` (области в отчёте `Тх_ДефицитТехники`),
  `StyleElementConstructors`, `Typo`, `UsageWriteLogEvent` — см. отчёт §2.

---

## ПРОМТ закончился

