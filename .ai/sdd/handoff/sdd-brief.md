# SDD Handoff Brief: Анализ дефицита техники (по технологическим картам)

> Status: Approved (ночной автономный прогон по standing-инструкции; ревью утром)
> Readiness: Ready for implementation (Фаза A — офлайн-авторинг; Фаза B — после подъёма кластера, админ)
> Updated: 2026-10-07

## Metadata

- **Spec ID:** `001-analiz-defitsita-tekhniki`
- **Spec Path:** `.ai/sdd/specs/001-analiz-defitsita-tekhniki/`
- **Current .status:** `tasks:approved`
- **Source Inputs:**
  - `.ai/strategy/handoff/strategy-brief.md`: missing
  - `.ai/sdd/ideas/...`: N/A
  - `.ai/sdd/PLAN.md`: missing (одна фича-спека, roadmap не требуется)

## Product / Feature Summary

- **User / Audience:** агрономы-планировщики, менеджеры парка, руководители агрохолдинга, администраторы 1С:ERP АПК 2.5.
- **Problem:** типовой АПК не сопоставляет потребность в сменах по техкартам с фактическим парком подразделений и не считает дефицит техники.
- **Outcome:** количественный отчёт «Дефицит техники» («Не хватает смен» по подразделению/периоду/работе/модели) за один запуск.
- **Scope:** расширение CFE «ПланированиеТехникиАПК» (префикс Тх_): регистр коэффициентов пересчёта, документ «План технических ресурсов», двухфазный расчёт + отчёт СКД, 2 роли, подсистема, модульные/Vanessa/e2e тесты.
- **Out of Scope:** модификация типовых объектов, Гант, виртуальная техника, дефицит прицепов/операторов, автоподбор замены, оборудование в расчёте (D-007).

## Requirements Summary

- **Key User Stories:** US-001 (коэффициенты), US-002 (план техресурсов), US-003 (отчёт дефицита), US-004 (роли), US-005 (навигация).
- **Must Have Functional Requirements:** FR-001..FR-017 (FR-018 — Should, покрыт).
- **Important NFRs:** NFR-001 (usability), NFR-002 (отчёт ≤ 30 с, автозаполнение ≤ 5 с), NFR-003 (только CFE, префикс Тх_), NFR-004 (роли только на новые объекты), NFR-005 (детерминизм, пометки вместо ошибок).
- **Acceptance Notes:** строки без коэффициента — явная пометка, не молчаливый 1,00 (FR-011); Q-001..Q-007 закрыты в design §18, формально открыты в requirements — ревью утром.

## Design Summary

- **Approach:** расширение №2 к ERP+АПК; все ссылки на объекты расширения №1 (Апк*) — generic-типы + рантайм-доступ; прямые типы только на core ERP (TD-001). Потребность — из регистров годового плана (TD-002). Отчёт — двухфазная схема: расчёт → регистр Тх_ДефицитТехники → СКД (TD-003).
- **Components / Modules:** 12 объектов design §4.0 (подсистема, enum, 2 регистра, документ, общий модуль Тх_ТехникаСервер, 2 обработки, отчёт, 2 роли, модуль тестов) + раннер тестов.
- **Data / State:** K = смены_аналога/смены_базовой (TD-004); автозаполнение K = Мб/Ма (TD-005); эквивалент доступности = смены_аналога / K; дефицит = max(0, потребность − доступность); дни календарные, СменВДень default 1.
- **APIs / Integrations:** рантайм-запросы к Апк*РаботыПоГодовомуПлануОбороты, справочникам моделей/сценариев, реквизитам ТС; обёртка `ВыполнитьЗапросАПК` с диагностикой «модуль АПК недоступен».
- **Technical Decisions:** TD-001..TD-007 (см. design §14).
- **Risks / Constraints:** ФАКТ-1 не верифицирован эмпирически (кластер упал) — B3; кластер недоступен до утра (ФАКТ-3); GUI для Vanessa не подтверждён; тестовый набор NFR-002 не существует (генерация в B7).

## Implementation Plan

- **Task Source:** `.ai/sdd/specs/001-analiz-defitsita-tekhniki/tasks.md`
- **Recommended Order:**
  Фаза A (офлайн, сейчас): A1 → A2 → A3 → A5 → A4 → A6 → A7 → A8 → A9 → A10 → A11 → A12 → A13
  Фаза B (после подъёма кластера): B1 (админ) → B2 → {B3, B4, B5, B7, B8} → B6 (только GUI)
- **Key Tasks:**
  - `A1–A2` — каркас CFE (cfe-init через `scripts/run_skill.py`), enum + подсистема.
  - `A3` — регистр коэффициентов + контроль ПередЗаписью + форма списка (s02).
  - `A4` — документ плана техресурсов (3 ТЧ, Принят, хоз.номер рантайм).
  - `A5` — Тх_ТехникаСервер: ВыполнитьЗапросАПК, ЧислоДнейПериода, КоэффициентНаДату.
  - `A6` — автозаполнение по мощности (K = Мб/Ма, кейс s02: 0,80).
  - `A7` — алгоритм расчёта + регистр результата (FR-008..FR-012).
  - `A8` — обработка запуска расчёта; `A9` — отчёт СКД (только свой регистр).
  - `A10` — роли + командный интерфейс; `A11` — Тх_Тесты (15 тестов) + раннер.
  - `A12` — Vanessa .feature (8) + e2e чек-лист; `A13` — финальный офлайн-гейт.
  - `B1` — Start-Service ragent + pagefile (АДМИН); `B2` — db-load-xml + UpdateDBCfg.
  - `B3` — верификация ФАКТ-1 (результат (в) = стоп-блокер, эскалация); `B4` — round-trip verify.
  - `B5` — прогон модульных тестов headless; `B6` — Vanessa при GUI; `B7` — e2e + замер ≤ 30 с; `B8` — security + итог.
- **Likely Files / Areas:**
  - `src/cfe/ПланированиеТехникиАПК/` — create (все объекты, префикс Тх_).
  - `tests/vanessa/*.feature`, `tests/e2e/web-checklist.md` — create.
  - `scripts/gen_nfr002_dataset.py` — create (B7).
  - `docs/verification-fact1.md`, `docs/morning-report-<date>.md` — create (B3/B8).

## Verification Plan

```text
Офлайн (каждая правка BSL):
  Command: bsl_analyze (MCP bsl-ls) по изменённым каталогам; python3 C:/MyProjects/1cDevTry/scripts/pre_load_validate.py <src/cfe/ПланированиеТехникиАПК>
  Expected: 0 синтаксических ошибок (список файлов непуст); exit 0

Загрузка (после кластера):
  Command: db-load-xml.ps1 -Mode Full -Extension "ПланированиеТехникиАПК" -UpdateDB (через python-обёртку, кириллица не инлайн)
  Expected: загрузка без ошибок, расширение активно

Round-trip:
  Command: DumpConfigToFiles в новый каталог → compare_dump_dirs.py
  Expected: 0 content diff (REAL), 0 сирот

Тесты в ИБ:
  Command: COM / 1cv8 /Execute раннера Тх_РаннерТестов
  Expected: 15/15 passed

Производительность:
  Command: замер на наборе NFR-002 (scripts/gen_nfr002_dataset.py)
  Expected: расчёт+отчёт ≤ 30 с; автозаполнение ≤ 5 с
```

- **Required Evidence:** логи bsl-ls и pre_load_validate (A-гейты), лог загрузки (B2), заметка ФАКТ-1 (B3), вывод compare (B4), сводка тестов (B5), отчёт Vanessa (B6), заполненный e2e чек-лист + замеры (B7), проверки доступа (B8).
- **Acceptance Coverage:** FR-001..FR-018 → таблица Requirement Coverage в tasks.md; NFR-002 — B7; NFR-004 — A10/B8; NFR-005 — A7/A11/B5.

## Review / Release Notes

- **Review Artifact:** `.ai/sdd/specs/001-analiz-defitsita-tekhniki/review.md` — ещё не создан (после реализации, sdd-review).
- **Review Verdict:** Not reviewed (утреннее ревью пользователя по standing-инструкции).
- **Known Follow-ups:** ревью Q-001..Q-007 и design §17–18 утром; решение по оптимизации generic→прямые типы после B3; подтверждение неблокирующего предупреждения «ТС в двух подразделениях» (FAQ Q5).

## Handoff Readiness

- **Ready for Implementation:** yes — Фаза A (офлайн-авторинг) стартуема немедленно; Фаза B — после B1 (подъём кластера, админ: Start-Service '1C:Enterprise 8.5 Server Agent (x86-64)' + pagefile ≥ 32–48 ГБ или pg-пароль для ibcmd).
- **Ready for QA:** no (после B5–B8).
- **Ready for Release:** no.
- **Blockers:** кластер 1С недоступен до утра (все B-задачи); Vanessa-прогон требует GUI (не подтверждён); тестовый набор NFR-002 не существует (генерация в B7); ФАКТ-1 не верифицирован (B3; негативный исход = эскалация на ревью, стоп B5–B8 в части расчёта).
- **Recommended Next Action:** исполнять Фазу A по порядку A1→A13 (sdd-exec); параллельно утром — B1 (админ), затем B2→B8.
