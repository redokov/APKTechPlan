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
| 001 | Анализ дефицита техники | tasks:approved | approved (ночной прогон, ревью утром; Q-001..Q-007 открыты с рекомендациями) | approved (ночной прогон, ревью утром; Q-001..Q-007 закрыты в дизайне, см. §18 Requirements feedback) | approved (ночной прогон, ревью утром; Фаза A офлайн + Фаза B после подъёма кластера) | pending |
| 002 | Редизайн планирования техники (расчёт потребности) | requirements:approved | approved (2026-10-09; D-001..D-008) | — | — | — |

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
