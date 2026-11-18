# Продолжение: волна 5 Sonar — фиксация + проверка шлюза (VPN) — 2026-11-18

Скопируй блок «ПРОМТ» ниже целиком в новую сессию pi, запущенную в
`C:\MyProjects\APKTechPlan`. Он самодостаточен. **Правки кода УЖЕ СДЕЛАНЫ и
проверены локально** (bsl-ls без роста, загрузка расширения OK, юнит 31/31,
Vanessa 9/9). Осталось: зафиксировать, прогнать CI и подтвердить шлюз (нужен VPN).

Контекст предыдущей сессии: `docs/review/sonar-fix262-2026-11-18.md`.

---

## ПРОМТ (копировать отсюда)

Работай в репозитории `C:\MyProjects\APKTechPlan` (расширение CFE
`ПланированиеТехникиАПК`, исходники `src/cfe/ПланированиеТехникиАПК/`, тестовая ИБ
`dev_erpapk_demo` на `localhost`, пользователь `Администратор (ОрловАВ)`, пароль пустой).
Платформа 8.5.4.2028 (автодетект `scripts/v8conf.py`).

**Контекст (не перепроверяй код заново, он уже проверен):** волна 5 Sonar —
262 замечания «Won't Fix» устранены в коде в 5 файлах `*.bsl`:

- `CommonModules/Тх_Тесты/Ext/Module.bsl` (+485/−179),
- `DataProcessors/Тх_ЗапускVanessa/Ext/ObjectModule.bsl` (+248/−63),
- `DataProcessors/Тх_ПодготовкаТестовыхДанных/Ext/ObjectModule.bsl` (+76/−39),
- `DataProcessors/Тх_РаннерТестов/Ext/ObjectModule.bsl` (+55/−6),
- `CommonModules/Тх_ТехникаСервер/Ext/Module.bsl` (+2/−2, прод).

Проверки предыдущей сессии (повторять НЕ нужно, кроме п.4 ниже):
`scripts/ls_compare.py` → «GREW (0)», bsl-ls 371→176; `scripts/wl_check.py` →
still-matching targets = 0 по всем 5 файлам; `scripts/load_extension.py` →
Load OK + CheckModules passed + UpdateDBCfg OK; `scripts/run_unit_tests_com.py` →
31/31 PASS; `scripts/run_all_va.py` → 9/9 PASS (122.5 мин, артефакты
`heartbeat/va_status_0*.log` = BOM+`0`, `heartbeat/va_1c_0*.log` = «Выполнение
сценариев закончено. Ошибок не было.»). Подробности и остатки —
`docs/review/sonar-fix262-2026-11-18.md`.

### Задача

1. **Проверь состояние дерева** (`git status --short`, `git diff --stat`):
   должно быть 5 изменённых `*.bsl` + новые файлы:
   скрипты `scripts/{bsl_ls_report,bsl_ls_file,ls_compare,wl_check,wl_slice,wl_locate,magic_est}.py`,
   отчёт `docs/review/sonar-fix262-2026-11-18.md`, сам этот промт и
   `docs/review/continue-prompt-sonar-2026-11-18.md`.
   Если чего-то из 5 `*.bsl` нет в diff — СТОП, сообщи владельцу (правки потеряны).
2. **Зафиксируй точку сохранения:**
   `git add -A` →
   `git commit -m "fix(sonar): волна 5 — устранены в коде 262 WONTFIX (подавлений 1)"` →
   `git push` (GitHub доступен без VPN).
3. Попроси владельца подключить VPN (одной строкой: «Готово к шагу Ф, подключай VPN»,
   и жди подтверждения).
4. **Шаг «Ф» после VPN:**
   - `curl -sk -m 8 https://192.168.200.52:8443` и `curl -s -m 8 http://192.168.200.52:9090`
     — оба кода не `000`;
   - перезапуск конвейера: `C:/MyProjects/ERPBandCIPipeline/scripts/jenkins_rest.py`
     (`POST /job/APKTechPlan/job/master/build`); одноразовый bash-вызов обрывается
     ~100 с — используй `nohup` + лог + короткие `tail` (или фоновый субагент-наблюдатель);
   - токен Sonar: `C:\MyProjects\ERPBandCIPipeline\secrets.sonar.env`
     (`auth=(token,'')`), запрос
     `GET http://192.168.200.52:9090/api/qualitygates/project_status?projectKey=APKTechPlan&branch=master`
     → статус OK, `new_violations = 0`;
   - если шлюз красный — разбери новые замечания:
     `api/issues/search?componentKeys=APKTechPlan&branch=master&createdAfter=<дата сборки>`.
     `QueryToMissingMetadata` / `QueryParseError` по объектам основной конфигурации —
     `POST /api/issues/bulk_change` с `do_transition=falsepositive`; прочее — чинить кодом.
5. **Сверь фасет:** «Won't Fix» должно опустеть с 262 до ~0 (исправленные в коде
   закрываются автоматически как FIXED). Отдельно посмотри, не появились ли
   `MagicDate` на новых функциях-датах `ДатаXxx()` в `Тх_Тесты` (в офлайн-снимке
   Sonar такого правила не было, но плагин мог его включить). Если появились —
   замени `Возврат Дата(Год, Месяц, День)` на `Возврат Дата("20990105")` и т.п.
6. **Обнови** `docs/review/sonar-fix262-2026-11-18.md`: номер сборки, итог шлюза,
   сколько WONTFIX осталось и почему; точка сохранения
   `docs(sonar): волна 5 проверена — gate OK, wontfix 262 -> N (сборка #M)`, push.

### Жёсткие правила

- **Код не переписывать** без причины: 262 замечания уже закрыты, все проверки
  зелёные. Любая новая правка — только по конкретному замечанию из сборки.
- Не трогать: 24 FALSE-POSITIVE, 201 OPEN, волны 1–4, метаданные/XML, `jenkins-lib`.
- Поведение тестов и прод-функций не менять: те же утверждения и данные.
- 2-attempt stop: одна и та же ошибка дважды → стоп, классифицировать
  (auth / namespace / headless / VPN), не долбить.
- Кириллица: `PYTHONIOENCODING=utf-8`, `PYTHONUTF8=1`; кириллицу в argv не вставлять.
- Долгие операции (сборка, загрузка расширения, юнит-тесты, Vanessa ~2 ч) —
  `nohup` + лог + короткие `tail`.
- Полезные скрипты этой волны: `scripts/bsl_ls_report.py`, `scripts/bsl_ls_file.py`,
  `scripts/ls_compare.py` (exit 1 при росте правила), `scripts/wl_check.py`.

### Справочные числа

- Снимок замечаний: `tmp/sonar-2026-11-18/` (в git не входит, переживает сессии).
- База: gate OK (`new_violations=0`), сборка #12 SUCCESS, всего 599 замечаний:
  262 WONTFIX / 201 OPEN / 112 FIXED / 24 FALSE-POSITIVE.
- Локальные логи прогонов: `tmp/load_run.log`, `tmp/unit_com_run.log`, `tmp/va_all_run.log`.

## ПРОМТ закончился
