# SDD Index

## Upstream Handoffs

- `.ai/strategy/handoff/strategy-brief.md`: missing

## Plan

- `.ai/sdd/PLAN.md`: missing (roadmap не требуется — один фиче-спека)

## Ideas

| ID | Name | Status | Path |
|----|------|--------|------|
| 001 | Анализ дефицита техники по технологическим картам | design:approved (устарела в части форм/типов) | .ai/sdd/specs/001-analiz-defitsita-tekhniki/ |
| 002 | Редизайн «Планирования техники АПК» — расчёт потребности по техкартам | idea:captured | .ai/sdd/ideas/002-redesign-planirovaniia-tekhniki.md |

## Feature Workspace

| Field | Value | Notes |
|-------|-------|-------|
| Next Feature ID | 001 | |
| Numbering Issues | none | (пустая папка specs/001 удалена 2026-10-07) |

## Specs

| ID | Feature | Status | Requirements | Design | Tasks | Review |
|----|---------|--------|--------------|--------|-------|--------|
| 001 | Анализ дефицита техники | superseded (заменена спекой 002; частично реализована в релизе 001, факты — справочник; ревью не проводилось, т.к. всё ценное переделано и проверено в 002) | approved (ночной прогон, ревью утром; Q-001..Q-007 открыты с рекомендациями) | approved (ночной прогон, ревью утром; Q-001..Q-007 закрыты в дизайне, см. §18 Requirements feedback) | approved (ночной прогон, ревью утром; Фаза A офлайн + Фаза B после подъёма кластера) | pending |
| 002 | Редизайн планирования техники (расчёт потребности) | review:done | approved (D-001..D-008) | approved (TD-001..TD-008, FAQ Q1–Q4 ок) | done (T1–T13, все гейты зелёные, поколение 6693e570) | approved with follow-ups (2026-10-10; Findings: Low×2 — сцепка структурно, фичи 05/06 stale) |

## Handoff

- `.ai/sdd/handoff/sdd-brief.md`: ready (контракт реализации; Фаза A — сейчас, Фаза B — после подъёма кластера)

## Next Actions

- [x] Инициализация .ai/ (ночной прогон 2026-10-07, автономно — Open Questions в artifacts)
- [x] specs/001-analiz-defitsita-tekhniki/requirements.md (sdd-prd, approved автономно по standing-инструкции)
- [x] specs/001-analiz-defitsita-tekhniki/design.md (sdd-spec, approved автономно по standing-инструкции; ревью утром — §17 Open Questions, §18 Requirements feedback)
- [x] specs/001-analiz-defitsita-tekhniki/tasks.md (sdd-tasks, approved автономно по standing-инструкции; 21 задача: A1–A13 офлайн + B1–B8 после кластера; ревью утром)
- [ ] Реализация Фазы A (A1→A13, офлайн-авторинг) — sdd-exec
- [ ] Фаза B: B1 подъём кластера (админ) → B2 загрузка → B3 ФАКТ-1 → B4 round-trip → B5 тесты → B6/B7/B8
- [ ] Утреннее ревью: Q-001..Q-007 из requirements.md + tasks.md
- [x] specs/002-redesign-planirovaniia-tekhniki/requirements.md — APPROVED (2026-10-09; D-001..D-008, все Q закрыты) — sdd-prd
- [x] specs/002-redesign-planirovaniia-tekhniki/design.md — APPROVED (TD-001..TD-008; источники: АпкМеханизированныеРаботыПоГодовомуПлану + АпкТранспортныеРаботыПоГодовомуПлану Turnovers, доступность через АпкПланТехническихРесурсов → ТС.АпкМодель) — sdd-spec

- [x] specs/002-redesign-planirovaniia-tekhniki/tasks.md — APPROVED (T1–T13, порядок T1..T13) — sdd-tasks
