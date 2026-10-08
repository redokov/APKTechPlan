# SDD Handoff Brief: Редизайн «Планирования техники АПК» — расчёт потребности по техкартам

> Status: Approved
> Readiness: Ready for implementation (все гейты approved, открытых вопросов нет)
> Updated: 2026-10-09
> Supersedes: `.ai/sdd/handoff/sdd-brief.md` спеки 001 (частично реализована; устарела в части форм/типов — использовать только как справочник фактов релиза 001)

## Metadata

- **Spec ID:** `002-redesign-planirovaniia-tekhniki`
- **Spec Path:** `.ai/sdd/specs/002-redesign-planirovaniia-tekhniki/`
- **Current .status:** `tasks:approved`
- **Source Inputs:** `docs/redesign-prompt-2026-10-09.md` (самодостаточный промт пользователя); `.ai/sdd/ideas/002-redesign-planirovaniia-tekhniki.md`; `.ai/sdd/PLAN.md`: missing (одна фича-спека)

## Product / Feature Summary

- **User / Audience:** агроном-планировщик; руководители агрохолдинга; пользователь ИБ «Агроном» (правовые тесты).
- **Problem:** расширение (CFE Тх_ для 1С:ERP АПК 8.5.4.1683) с generic-типами, рантайм-багом и дублями синонимов; план техники заполняется вручную вместо расчёта по ПРОВЕДЁННЫМ техкартам (АпкТехнологическиеКартыНаПоле).
- **Outcome:** обработка «Формирование плана работ техники» считает потребность в МОДЕЛЯХ (обороты регистров АпкМеханизированныеРаботыПоГодовомуПлану + АпкТранспортныеРаботыПоГодовомуПлану, *_Вер, по подразделению выращивания) и сопоставляет с доступностью из проведённых АпкПланТехническихРесурсов (→ ТС.АпкМодель), с модельными коэффициентами замещения; результат — корректируемый документ «Потребность в технике».
- **Out of Scope (релиз 1):** замены техникой чужих подразделений (расстояния/трал/спецразрешения); переименование внутренних имён; ручные коэффициенты (удалённый регистр заменён реквизитами моделей).

## Requirements Summary

- **Key US:** US-001 (автоформирование), US-002 (сцепка), US-003 (синонимы), US-004 (права/Агроном).
- **Must:** FR-001 типизация всех реквизитов; FR-002 сцепка (СХ-техника↔СХ-оборудование; автотранспорт↔прицепы); FR-003 обработка (5 шагов §design 6.1–6.3); FR-004 коэффициенты замещения (таблица приоритетов, старт по мощности); FR-005 удаление Тх_КоэффициентыПересчетаРабот; FR-006 синонимы; FR-007 права под «Агроном».
- **Decisions:** D-001..D-008 (requirements), TD-001..TD-008 (design). Все Q закрыты; FAQ Q1–Q4 подтверждены.

## Design Summary

- **Подход:** эволюционный; ретайпинг `<v8:TypeId>` → `<v8:Type>cfg:…</v8:Type>` (формат APKModSrc); составной «модель» реализован парами однотипных ТЧ (TD-002).
- **Источники (канонические, rlm-tools-bsl):** потребность — обороты двух регистров накопления Turnovers (техника: Техника/Оборудование/Смен_Вер/Часов_Вер; транспорт: Автомобиль/Прицеп/Смен_Вер/Часов_Вер); доступность — проведённые АпкПланТехническихРесурсов (ТЧ Подразделения В ИЕРАРХИИ → 4 ТЧ ТС → Справочник.ТранспортныеСредства.АпкМодель).
- **Формулы:** К = Реквизит(замены)/Реквизит(оригинала); смены_замены = смены/К; Количество = ОКРВВЕРХ(ПотребностьСмен/(ДнейПериода×СменВдень)).
- **Risks:** NFR-003 (первая загрузка прямых cfg-типов — зонд в T2), 8.5 dot-синтаксис оборотов (паттерн релиза 001), видимость команды раздела (ретест под Агрономом T12).

## Implementation Plan

- **Task Source:** `.ai/sdd/specs/002-redesign-planirovaniia-tekhniki/tasks.md` (approved)
- **Recommended Order:** T1 → T2 → T3 → T4 → T5 → T6 → T7 → T8 → T9 → T10 → T11 → T12 → T13 (T5/T7/T8 аддитивные, между T1–T4 допустимы)
- **Пайплайн каждой задачи:** pre_load_validate → bsl-ls → v8std → db-load-xml Full -UpdateDB → свежий load_log → при структурных правках kill 1cv8* + designer_agent apply → round-trip (dump_extension + compare, content diff REAL = блокер) → VA по необходимости → коммит + heartbeat/night.log.
- **Likely Files:** `src/cfe/ПланированиеТехникиАПК/**` (Documents/Тх_ПланТехническихРесурсов, InformationRegisters/Тх_ДефицитТехники, DataProcessors/Тх_ФормированиеПланаРаботТехники [новый], Тх_РасчетДефицита; −Тх_КоэффициентыПересчетаРабот, −Тх_ЗаполнениеКоэффициентов), CommonModules/Тх_ТехникаСервер + Тх_Тесты, Roles, Subsystems, tests/vanessa/01,02,03,08*,09*.
- **Субагенты:** генерация черновиков XML/BSL/feature-фрагментов — local_qwen, строго последовательно; загрузки/прогоны/коммиты/кириллица-в-argv — НЕ делегировать.

## Verification Plan

```text
Гейты: python scripts/pre_load_validate.py; MCP bsl-ls bsl_analyze (0 файлов = НЕ выполнено); MCP v8std
Загрузка: db-load-xml.ps1 (полная команда в tasks.md) + чтение свежего load_log.txt
Round-trip: scripts/dump_extension.py → compare_dump_dirs.py (only-in-source=0, content diff REAL=0)
VA: PYTHONIOENCODING=utf-8 python scripts/run_va_feature.py <feature> <timeout>; вердикт по строке «Ошибок не было./БЫЛИ ОШИБКИ.»
Unit: python scripts/run_unit_tests.py (серверные, headless COM)
Ожидание: 01/02/03/08/09 PASS (03 — после переименования навигации), unit PASS, 0 Error bsl-ls/v8std
```

## Review / Release Notes

- **Review Artifact:** `review.md` — создаётся фазой sdd-review после T13.
- **Known Follow-ups:** «команда не найдена в панели раздела» (открытая проблема §8 промта) — диагностировать под Агрономом в T12; межподразделенческие замены — roadmap (design FAQ Q9).
- **Baseline:** коммит `144b782` (WIP feature 03: BeforeAddRow-дефолты — переиспользуется в T3).

## Handoff Readiness

- **Ready for Implementation:** yes
- **Ready for QA:** no (после T11/T12)
- **Ready for Release:** no (после sdd-review)
- **Blockers:** нет
- **Recommended Next Action:** sdd-exec, задача T1 (синонимы)
