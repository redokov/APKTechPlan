# ИТОГОВЫЙ ПРОМТ: возобновление имплементации spec-003 (после решения по статусам)

Дата: 2026-11-09. Режим: оркестратор (SubagentWorkflow), субагенты ПОСЛЕДОВАТЕЛЬНО,
модели ТОЛЬКО провайдера erpband:
- анализ/линзы/гейты — `erpband/deepseek-ai/deepseek-v4.1-flash-1017`
- синтез/архитектор/финальные решения — `erpband/zai/glm-5.3:NVFP4`
- запасные (если основная недоступна): `erpband/qwen/qwen3.8:27b`,
  `erpband/xiaomi/mimo-v2.6-pro`

ЗАПРЕЩЕНЫ модели семейств anthropic (claude-*) и chatgpt/openai-gpt
(openai/gpt-6.1-terra, openai/gpt-oss:120b, anthropic/*) — НИ В ОДНОМ субагенте,
НИ ПРИ КАКОМ fallback. Если ни одна разрешённая модель не отвечает — стоп и отчёт,
а не тихая замена на запрещённую.

Каждый субагент: max_turns 6-8, фиксированный формат ответа, только свой контекст.

## DECISION-2026-11-09 (решение владельца, снять всеambiguity)

Пользователь подтвердил: 2026-11-08 в чате одобрено ОБА:
(a) SDD-конверт spec-003 (документы) И
(b) safe source fixes + проверка сценариев/E2E на тест-ИБ `localhost\dev_erpapk_demo`.

Следствия:
- `.status = implementation:in-progress` — ЛЕГИТИМЕН, не менять.
- Все самоназвания «documentation-only» в теле spec-003 — УСТАРЕЛИ, подлежат правке.
- Q-001..Q-008 остаются открытыми и продолжают блокировать задачи,
  зависящие от бизнес-решений. Одобрение (b) НЕ закрывает ни один Q.
- Граница авторизации: правки BSL/XML/скриптов, подтверждённые исходниками и
  не требующие выбора бизнес-семантики (safe lane), + статические гейты +
  загрузка расширения в dev_erpapk_demo + unit/VA/E2E на тест-ИБ.
  Запрещено как и прежде: прод-ИБ, мутация ролей без маркера/снапшота,
  Vanessa/Chrome/Designer без отдельного гейта, деструктивные операции.

## ФАЗА 0 — Реконсиляция артефактов spec-003 (documentation edits, авторизовано)

Оркестратор правит сам (точечно, diff в отчёт), без субагентов:
1. Шапки requirements.md / design.md / tasks.md →
   `> Status: Approved (user approval 2026-11-08; implementation lane authorized;
   reaffirmed by owner decision 2026-11-09)`.
2. design.md §8.1 «Documentation-only scope» → заменить на «Reconciled scope»:
   верификация артефактов + разрешённого safe lane; продукт-гейты §8.2 без изменений.
3. В tasks.md §2 таблицу readiness: строку «Implementation authorization: Partial»
   → «Authorized (safe lane, decision 2026-11-09); Q-001..Q-008 block dependent
   business-rule tasks».
4. ДОБАВИТЬ в tasks.md раздел «Authorization matrix» — механически из существующих
   Q-гейтов задач: для каждой задачи SRV-01..04 / TEST-01..02 / UI-01 —
   `unlocked` (ни один из её named questions не входит в открытые Q-001..Q-008
   и не требует бизнес-решения) или `blocked-by-Qx..`. Задачи safe lane из
   синтеза кросс-ревью (контракт результата раннера, строгий парсинг статуса,
   числовой СтрНайти, логирование) пометить `unlocked (safe lane)`.
   Матрицу НЕ изобретать: только вывод из уже записанных гейтов.
5. INDEX.md: оставить [x]-апрувы, добавить строку:
   `- [x] DECISION-2026-11-09: owner confirmed approval of safe source fixes +
   test-IB E2E (variant 2); documentation-only self-description superseded`.
6. tasks.md, Execution rules: строка «Use only model `erpband/openai/gpt-6.1-terra`»
   ЗАМЕНЕНА (модель запрещена владельцем 2026-11-09) на:
   «Use only models `erpband/deepseek-ai/deepseek-v4.1-flash-1017` (analysis) and
   `erpband/zai/glm-5.3:NVFP4` (synthesis); anthropic and openai/gpt models
   are prohibited». Заодно проверить, что ссылок на claude-fable/gpt-terra в
   спеке не осталось (grep).
7. Одна строка в heartbeat/night.log: `2026-11-09 | decision | variant 2 confirmed;
   spec-003 status contradiction resolved by owner decision`.

Гейт фазы 0: пять носителей (.status, INDEX, 3 файла спеки) рассказывают одну
историю; grep 'documentation-only' в spec-003 → 0 вхождений в статусных секциях;
grep запрещённых моделей (gpt-6.1-terra, claude) в spec-003 → 0 вхождений.

## ФАЗА 1 — Починка воркфлоу-скриптов (PROMPT-A, см. orchestrator-prompts-2026-11-09.md)

Два дефекта, дважды сорвавших прогон:
1) статус-контракт: `r.status === 'PASS'` vs свободный текст ('completed',
   'completed_with_blocker') → оборванные фазы;
2) вердикт: `synth.verdict === 'BLOCKED'` не матчит прозу → Implementation
   стартует вопреки BLOCKED.

Правки в C:/MyProjects/APKTechPlan/.pi/workflows/*.js (3 файла):
a) WORK_SCHEMA.status → строгий enum 'PASS' | 'FAIL' | 'BLOCKED'; в промпты
   агентов добавить "return status as exactly one of: PASS, FAIL, BLOCKED";
   нормализация (trim/upper) + лог сырого ответа при reject;
b) вердикт синтезатора → отдельное поле `blocked: boolean`, сравнение по полю;
c) иная логика фаз не меняется.
Последовательность: субагент A1 (таблица всех точек сравнения, ≤12 строк) →
правки оркестратором → субагент A2 (верификация: все точки закрыты; сценарий
«Implementation при BLOCKED» невозможен; node --check 3 файлов = PASS).
Субагенты A1/A2 — `erpband/deepseek-ai/deepseek-v4.1-flash-1017`.

## ФАЗА 2 — Форензик для архива (PROMPT-B, сокращённый, read-only, опционально по времени)

Один субагент B1 (хронолог): mtime-хронология spec-003 (09:04-09:35) + кто
записал 'Approved/in-progress' (по логам pi-сессий и wf_b3eb3599c9bf.output).
Модель: `erpband/deepseek-ai/deepseek-v4.1-flash-1017`.
Цель — запись в отчёт: подтверждение, что fence агентами не нарушался.
≤15 строк. Запрещено что-либо править.

## ФАЗА 3 — Ре-запуск fix-and-e2e (исправленные скрипты + реконсиляция на диске)

Скрипт: .pi/workflows/apktechplan-fix-and-e2e.js (исправленный в ФАЗЕ 1).
Строгая последовательность, стоп на любом гейте:

1. `preflight gatekeeper` (erpband/deepseek-ai/deepseek-v4.1-flash-1017):
   перечитать 5 артефактов spec-003 + INDEX + git state. ОЖИДАЕМ PASS —
   противоречие снято ФАЗОЙ 0. Любой FAIL → стоп и отчёт, без ретраев вслепую.
2. `offline remediation engineer` (erpband/zai/glm-5.3:NVFP4):
   ТОЛЬКО задачи из Authorization matrix с пометкой unlocked. Каждая правка:
   - минимальный diff, подтверждённый строками исходников;
   - запрет выбора бизнес-семантики (период, доступность, Принят, организация,
     количество/мощность, SKIP-политика, UX) — это территория Q-001..Q-008;
   - после каждой правки: python scripts/pre_load_validate.py →
     bsl_analyze (целевые каталоги, НЕ «0 файлов») → v8std при доступности.
3. `static release gatekeeper` (erpband/deepseek-ai/deepseek-v4.1-flash-1017):
   все три гейта зелёные по ВСЕМ изменённым файлам; иначе стоп.
4. Фаза IB/E2E (только после зелёного п.3; все запуски — nohup + лог + tail,
   одноразовый bash-вызов обрывается ~100 c):
   - загрузка расширения: scripts/load_extension.py (dev_erpapk_demo,
     «ПланированиеТехникиАПК»); -UpdateDB по правилу AGENTS.md;
   - unit: scripts/run_unit_tests.py — базовый уровень 20/20;
   - VA-сценарии 01-09: scripts/run_va_feature.py (эталонный EPF).
     Сессия интерактивная (подтверждено владельцем 2026-11-09) — VA-блок
     выполняется штатно, вопрос о GUI не задавать;
   - round-trip: загрузка в тест-ИБ → выгрузка в НОВЫЙ каталог →
     scripts/compare_dump_dirs.py → REAL diff = 0.
5. `final verifier` (erpband/zai/glm-5.3:NVFP4): сверить всё с Acceptance
   spec-003 (FR-008 non-regression: модельный план, идентичность документа
   доступности, posted-baseline, семантика коэффициентов, контракты форм/доков,
   ролевое поведение T13). Итог: PASS/FAIL + список незакрытых Q.

Heartbeat: одна строка на каждый завершённый шаг в heartbeat/night.log.

## Критерии готовности (все обязательны)
1. Пять носителей статуса согласованы (гейт ФАЗЫ 0).
2. node --check 3 скриптов = PASS; таблица дефектов A1 полностью закрыта.
3. Статические гейты зелёные по каждому изменённому файлу (bsl_analyze не «0 файлов»).
4. unit ≥ 20/20; VA-набор выполненных сценариев PASS; RT-compare REAL=0.
5. Незакрытые Q-001..Q-008 перечислены в финальном отчёте с тем, что именно
   блокирует каждая.
6. Финальный отчёт оркестратора ≤ 40 строк + приложение-diff.
