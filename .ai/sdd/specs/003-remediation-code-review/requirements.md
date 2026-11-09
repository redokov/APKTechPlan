# SAFE-SDD-003: Исполняемые гейты ремедиации код-ревью APKTechPlan

> Status: Approved (user approval in chat; 2026-11-08; implementation lane authorized — reaffirmed by owner decision 2026-11-09, variant 2)
> Dependency: SAFE-SDD-002 — documentation-only remediation baseline
> Baseline: spec-002 `002-redesign-planirovaniia-tekhniki`, T13, generation `6693e570`.
> Review source: `docs/review/review-report-2026-11-07.md` (read-only review, commit `1d0f34c`).
> Scope: remediation deltas only; spec-002 is not reopened or rewritten.

## 1. Baseline and governing rule

Spec-003 is a remediation delta against the approved spec-002 baseline, specifically against T13 and generation `6693e570`. The approved behavior of spec-002 remains in force unless a future, explicit owner decision records a superseding decision. A review finding is evidence of a defect or verification gap; it is not, by itself, authorization to change a spec-002 decision or to implement a new business semantic.

The following baseline identity is preserved:

- spec-002 D-006: availability is taken from the availability document `Документ.АпкПланТехническихРесурсов`; the plan is by models and attached equipment, and internal names are not changed;
- spec-002 TD-007: availability is based on posted `АпкПланТехническихРесурсов`; `АпкИсторияТранспортныхСредств` is not a replacement source;
- spec-002 T8/T9: the existing availability and plan-building behavior is inherited pending factual/semantic confirmation, not silently replaced;
- spec-002 T13: the implementation and gates at generation `6693e570` are the comparison point for non-regression.

## 2. Delta classification

Overlapping topics are classified explicitly:

- **Inherited:** approved spec-002 behavior remains the baseline and is not changed by this remediation envelope. This includes D-006/TD-007 availability document identity, model-level planning, the posted-document baseline, and all behavior outside confirmed finding scope.
- **Confirmed review delta:** a finding from the 2026-11-07 review identifies a concrete defect or verification gap that may be remediated after its required decision gate. The finding does not determine unresolved business semantics.
- **Still open:** a question requiring factual or owner confirmation. It remains open and blocks dependent implementation; this spec does not close it.

## 3. Goal and boundaries

The goal is to make the remediation delta traceable to spec-002, separate confirmed code-review findings from unresolved domain semantics, and define safe follow-up work without changing production sources in this task.

This task modifies only the three spec-003 SDD artifacts. It does not modify BSL, XML, type configuration objects, tests, roles, databases, or runtime state. No database, Designer, COM, Vanessa, Chrome, role mutation, or destructive operation is authorized.

## 4. User stories

### US-001: Preserve approved planning behavior

As the owner of the planning feature, I want remediation to preserve spec-002 behavior outside a confirmed finding scope, so that a defect fix does not become an undocumented redesign.

Acceptance:

- [ ] spec-002 T13 / generation `6693e570` is the explicit baseline;
- [ ] every remediation task has traceability to a spec-002 decision/task or a dated review finding;
- [ ] no task changes a spec-002 decision without a future explicit owner decision;
- [ ] D-006/TD-007 availability document identity is retained.

### US-002: Clarify the availability contract without reopening identity

As a reviewer, I want read-only confirmation of the already-identified availability contract, so that implementation can distinguish facts from semantics without replacing the approved source document.

Acceptance:

- [ ] Q-002 requests confirmation of tabular parts, accepted filtering, organization/subdivision scope, and quantity/capacity semantics;
- [ ] Q-002 does not ask the owner to choose between `Тх_ПланТехническихРесурсов` and `АпкПланТехническихРесурсов`;
- [ ] Q-002 remains open until factual and semantic confirmation is supplied;
- [ ] no fallback source or silent alternative is introduced.

### US-003: Remediate confirmed review findings safely

As a maintainer, I want confirmed findings separated from open business decisions, so that P0/P1/P2 remediation can be implemented only after the correct owner gate.

Acceptance:

- [ ] P0-1 and P0-2 are recorded as confirmed review deltas;
- [ ] security, cleanup, SKIP, error-classification, batching, and UI findings retain their review references;
- [ ] unresolved period, physical-TS, error, test-boundary, SKIP, and UX semantics remain open;
- [ ] implementation remains blocked while its dependency questions are open.

### US-004: Enforce executable task gates and scope safety

As the maintainer of the remediation plan, I want every implementation task to name its exact closed-question prerequisite and a manifest scope guard, so that unresolved semantics cannot reach executable work and type configuration objects cannot be changed accidentally.

Acceptance:

- [ ] Q-001..Q-008 map to exact FRs, implementation tasks, and verification gates;
- [ ] DEC-02 read-only inventory is the only full-configuration preparation allowed before semantic approval;
- [ ] business-dependent BSL/XML, role, information-base, UI, and Vanessa work is explicitly BLOCKED until its own gate closes;
- [ ] US-001..US-004 are present in requirement, task, decision, and verification traceability;
- [ ] GATE-01 rejects type configuration object changes and unrelated main-configuration object changes independently of static-analysis results.

## 5. Functional requirements

### FR-001: Baseline anchoring — Must Have

The remediation specification SHALL reference spec-002 T13 and generation `6693e570` as the baseline and SHALL state that approved behavior remains inherited unless explicitly superseded by a future owner decision.

Traceability: spec-002 T13; 2026-11-07 review P0-1/P0-2; SAFE-SDD-002; SAFE-SDD-003; US-001.

### FR-002: Availability identity preservation — Must Have

The remediation specification SHALL preserve spec-002 D-006 and TD-007: the current availability identity is posted `Документ.АпкПланТехническихРесурсов`, with the approved model-level planning behavior. `АпкИсторияТранспортныхСредств` SHALL NOT become an implicit replacement source.

Traceability: spec-002 D-006, TD-007, T8, T9; review §7 and P2-6.

### FR-003: Read-only availability confirmation — Must Have

Q-002 SHALL remain open and SHALL request only read-only confirmation of:

1. the canonical tabular parts (`табличных частей`) of the already-approved availability document;
2. the accepted filter (`Принят`) and whether it applies to each relevant tabular part;
3. organization scope;
4. subdivision scope, including hierarchy/equality semantics;
5. quantity/capacity semantics, including how duplicate physical vehicles and allocated quantity are treated.

Q-002 SHALL not reopen document identity and SHALL not close any question.

Traceability: spec-002 D-006, TD-007, T8/T9; review P0-2, P2-4, P2-6; Q-002.

### FR-004: Period replacement remains a decision gate — Must Have

The remediation SHALL record the 2026-11-07 P0-2 finding that cleanup can remove rows outside the requested date range. It SHALL NOT choose exact-match, overlap, or full-scenario replacement semantics. That choice remains Q-001 and requires an explicit owner decision before SRV-01 implementation.

Traceability: spec-002 T13 baseline; review P0-2; Q-001; SRV-01.

### FR-005: Result contract delta — Must Have

The remediation SHALL record the confirmed P0-1 result-contract mismatch: the UI reads `Результат.Прошёл`, while the runner returns `Статус`. PASS, FAIL, and SKIP SHALL remain distinguishable; the exact SKIP policy remains Q-007.

Traceability: spec-002 T12/T13 test baseline; review P0-1 and P1-6; Q-007; TEST-01/TEST-02/TEST-08.

### FR-006: Error and model-property semantics remain open — Must Have

The remediation SHALL record P1-1, P1-2, and P1-3 as confirmed review deltas, while leaving the distinction between absent business requisites and infrastructure/permission/module failures open under Q-005. No remediation task may silently turn an infrastructure error into zero or choose a new error contract before owner confirmation.

Traceability: spec-002 T5/T9/T13; review P1-1/P1-2/P1-3; Q-005; SRV-05/SRV-06.

### FR-007: Test safety and cleanup are deltas, not authorization — Must Have

The remediation SHALL record P1-5, P1-6, and P1-7 as confirmed safety/quality findings. Test-IB boundary, role, marker, and SKIP policy remain open under Q-006/Q-007. No test task may mutate roles or an information base in this offline remediation task.

Traceability: spec-002 T12/T13; review P1-5/P1-6/P1-7; Q-006/Q-007; TEST-03..TEST-09.

### FR-008: Non-regression obligation — Must Have

Any future remediation implementation SHALL preserve approved spec-002 behavior outside the confirmed finding scope, including model-level plan behavior, the availability document identity and posted-document baseline, approved coefficient semantics, accepted document/form contracts, and rights behavior validated by spec-002 T13. A proposed change that affects an inherited behavior SHALL be blocked until an explicit future owner decision records the supersession and its scope.

Traceability: spec-002 D-001..D-008, TD-001..TD-008, T1..T13; review report; all remediation tasks.

### FR-009: Traceability of every remediation task — Must Have

Every task in `tasks.md` SHALL name at least one spec-002 decision/task or one finding from `docs/review/review-report-2026-11-07.md`. A task with no such reference is invalid. References do not authorize implementation.

Traceability: spec-002 T1..T13; review P0-1..P2-6; SAFE-SDD-002; US-001; US-003; US-004.

### FR-010: Per-question execution gates — Must Have

Every implementation task SHALL name the exact question IDs it requires and SHALL remain `BLOCKED` until every named question is explicitly closed by a future owner decision. A task SHALL NOT become executable merely because a read-only inventory, review finding, static analysis result, or implementation authorization exists.

Traceability: US-003; US-004; Q-001..Q-008.

### FR-011: Safe preparation boundary — Must Have

Before semantic approval, `DEC-02` SHALL permit only a read-only full-configuration inventory needed to establish facts. No business-dependent BSL/XML, role, information-base, UI, or Vanessa work may proceed until its own question gate closes. The inventory is preparation and SHALL NOT close a question or authorize implementation.

Traceability: US-002; US-003; US-004; Q-002; Q-006; Q-008.

### FR-012: Type-object and main-configuration scope guard — Must Have

`GATE-01` SHALL inspect the declared change manifest and reject any type configuration object change or any unrelated main-configuration object change, regardless of whether static analysis passes. `GATE-01` is a documentation/checking control only in this task; it does not mutate sources, metadata, roles, or runtime state.

Traceability: US-001; US-003; US-004; NFR-001.

### FR-013: Complete TEST-01 acceptance contract — Must Have

`TEST-01` acceptance SHALL cover all FR-008 non-regression fields: model-level plan behavior; availability document identity; posted-document baseline; approved coefficient semantics; accepted document/form contracts; and rights behavior validated by spec-002 T13. It SHALL NOT invent missing exception-schema details.

Traceability: US-001; US-003; US-004; FR-008; TEST-01.

## 6. Non-functional requirements

### NFR-001: No type-configuration changes

No remediation artifact may authorize modification of type configuration objects or the main configuration. Spec-002's direct type decisions remain inherited and are outside this task.

### NFR-002: Read-only and offline safety

The preparation phase is read-only with respect to product/runtime artifacts. After explicit user approval, the safe implementation lane may modify only source-confirmed BSL/forms/scripts listed in approved tasks; database, Designer, COM, Vanessa, Chrome, role mutation, and destructive operations remain separate authorized gates.

### NFR-003: Static-gate discipline

Every approved BSL/XML change SHALL run `pre_load_validate.py`, targeted non-empty `bsl_analyze`, and `v8std` when available, stopping on any failure. Safe implementation tasks must record these gates before load or runtime verification.

### NFR-004: Questions remain open

Q-001..Q-008 SHALL remain open. The presence of a baseline, review evidence, or this remediation specification SHALL NOT be treated as a decision or implementation approval.

### NFR-005: Traceability and heartbeat

Progress and gate results for this task SHALL be recorded in `heartbeat/night.log`; the three SDD artifacts SHALL contain the durable traceability needed to resume without relying on chat history.

## 7. Scope of remediation deltas

Confirmed review deltas are limited to the findings in the 2026-11-07 report:

- P0-1: UI runner/result contract;
- P0-2: period-scoped cleanup;
- P1-1/P1-2/P1-3: error logging, classification, and model-property exception handling;
- P1-4: N+1 model-property access;
- P1-5/P1-6/P1-7: test safety, SKIP truthfulness, and fixture cleanup;
- P2-1..P2-6: report/error/counter/batching/path/organization-scope follow-ups.

The review findings do not supersede spec-002 decisions. P2-6 is explicitly still open as a business-rule confirmation, not an approved organization-scope change.

## 8. Questions

### Q-001: Period replacement scope

**Status:** open. Confirm whether cleanup is exact interval, overlapping interval, or full-scenario replacement. This remains a prerequisite for SRV-01.

### Q-002: Availability facts and semantics

**Status:** open; narrowed by SAFE-SDD-002 and gated by SAFE-SDD-003.

Provide read-only confirmation against the full configuration of:

- which tabular parts of the already-approved `Документ.АпкПланТехническихРесурсов` are canonical for each model/vehicle category;
- whether and how `Принят` filters rows in each relevant tabular part;
- whether organization is part of the availability scope and how it is matched;
- whether subdivision matching is equality or hierarchy and whether the same rule applies to demand and availability;
- whether `Количество` is allocated capacity, physical-vehicle count, or another quantity, and how duplicate vehicle rows are interpreted.

This question does **not** ask whether the source is `Тх_ПланТехническихРесурсов` or `АпкПланТехническихРесурсов`: D-006/TD-007 preserve the latter as the current baseline. Q-002 remains open and is not closed by this document.

### Q-003: Duplicate vehicles and quantity

**Status:** open. Keep separate from the factual part of Q-002 until the owner confirms whether availability is physical uniqueness, allocated quantity, or another capacity rule.

### Q-004: Concurrency

**Status:** open. Locking, serialization, or retry/snapshot behavior is not selected.

### Q-005: Dynamic model-property error contract

**Status:** open. Confirm absent business requisites versus infrastructure, permission, module, and query failures.

### Q-006: Test runner boundary

**Status:** open. Operational CFE versus test-only extension, test-IB marker, and role boundary are not selected.

### Q-007: SKIP policy

**Status:** open. Confirm whether SKIP is a CI failure for all tests or only mandatory integration suites.

### Q-008: Form UX and platform events

**Status:** open. Confirm zero-result report behavior, stale values, period validation, and supported row events.

## 8a. Question-to-gate matrix

All questions remain open. The following matrix is normative: an implementation task is executable only after every question in its gate column is explicitly closed by an owner decision. `DEC-02` is the sole pre-approval preparation lane; it is read-only and cannot close a question.

| Question | Exact requirements | Implementation tasks blocked | Verification gate blocked | Pre-approval preparation |
|---|---|---|---|---|
| Q-001 | FR-004, FR-008 | SRV-01 | GATE-02 period-scope/non-regression | DEC-02 inventory only |
| Q-002 | FR-003, FR-008, FR-011 | SRV-02, UI-01 | GATE-02 availability-contract | DEC-02 inventory only |
| Q-003 | FR-003, FR-008 | SRV-02 | GATE-02 availability-contract | DEC-02 inventory only |
| Q-004 | FR-008 | SRV-01 | GATE-02 concurrency/non-regression | DEC-02 inventory only |
| Q-005 | FR-006, FR-008 | SRV-03, SRV-04 | GATE-02 error-contract | DEC-02 inventory only |
| Q-006 | FR-007, FR-008, FR-011 | TEST-02 | GATE-03 test-boundary | DEC-02 inventory only |
| Q-007 | FR-005, FR-007, FR-008 | TEST-01, TEST-02 | GATE-03 result/SKIP | DEC-02 inventory only |
| Q-008 | FR-008, FR-011 | UI-01 | GATE-04 UI-contract | DEC-02 inventory only |

No matrix row grants implementation permission. A static-analysis PASS cannot bypass an unresolved question or GATE-01.

## 9. Decision status

No new business decision is made by SAFE-SDD-003. Spec-002 D-006/TD-007 remain inherited. Confirmed review findings are remediation deltas only. Q-001..Q-008 remain open, and implementation-dependent work remains BLOCKED until the relevant future owner decisions and separate implementation authorization exist.
