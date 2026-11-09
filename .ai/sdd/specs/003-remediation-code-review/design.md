# Design: SAFE-SDD-003 executable gates for APKTechPlan remediation

> Requirements: `requirements.md`
> Baseline: spec-002 `002-redesign-planirovaniia-tekhniki`, T13, generation `6693e570`
> Dependency: SAFE-SDD-002 (documentation-only remediation baseline)
> Status: Approved (user approval in chat; 2026-11-08); implementation in progress (owner reaffirmed variant 2, 2026-11-09)
> Review evidence: `docs/review/review-report-2026-11-07.md`, commit `1d0f34c`

## 1. Design intent

Spec-003 is an anchored remediation delta, not a successor redesign. Spec-002 remains the approved behavioral baseline. The comparison point is spec-002 T13 at generation `6693e570`; the review findings dated 2026-11-07 identify candidate defects or verification gaps against that baseline.

A delta is actionable only when:

1. the finding is confirmed in the review evidence;
2. all required factual and business questions are answered by an explicit future owner decision;
3. the change preserves inherited behavior outside the finding scope;
4. separate implementation authorization exists.

No type configuration object or main-configuration change is part of SAFE-SDD-003. Approved safe implementation tasks may change only the explicitly listed CFE BSL/forms/scripts; runtime and database operations remain separate authorized phases.

## 2. Classification model

Each overlapping topic is labelled in this design:

- **Inherited:** preserve spec-002 behavior and contracts. This includes D-006/TD-007 availability identity, posted `Документ.АпкПланТехническихРесурсов` as the current source, model-level planning, approved model-coefficient behavior, and T13-tested rights/form behavior outside a confirmed finding.
- **Confirmed review delta:** remediate only the concrete issue recorded in the 2026-11-07 report. Examples: P0-1 result-property mismatch, P0-2 unscoped cleanup, P1-1/P1-2/P1-3 error handling, P1-4 N+1 access, P1-5/P1-6/P1-7 test safety and cleanup, and P2 findings.
- **Still open:** do not select semantics where the review or full configuration cannot establish them. Q-001..Q-008 remain open.

## 3. Baseline contract and non-regression envelope

### 3.1 Availability identity

The availability source identity is inherited from spec-002 D-006 and TD-007:

- current baseline source: posted `Документ.АпкПланТехническихРесурсов`;
- model bridge and model-level planning remain inherited from spec-002 T8/T9;
- `АпкИсторияТранспортныхСредств` is not a silent fallback or replacement source;
- the similarly named CFE document `Тх_ПланТехническихРесурсов` is not substituted for the approved availability document.

The internal structure of the source is not re-decided here. Q-002 is a read-only factual/semantic confirmation of tabular parts, `Принят`, organization, subdivision, and quantity/capacity behavior.

### 3.2 Other inherited behavior

Unless a future owner decision explicitly supersedes it, preserve:

- spec-002 D-001..D-008 and TD-001..TD-008;
- spec-002 T1..T13 acceptance behavior at generation `6693e570`;
- approved model-level plan and coefficient semantics;
- existing public contracts outside the precise review finding;
- no changes to type configuration objects or the main configuration.

### 3.3 Scope rule

A remediation task may narrow an implementation defect but may not introduce an undocumented business rule. If a proposed fix changes period scope, availability identity, hierarchy matching, accepted filtering, duplicate handling, quantity/capacity, test boundary, SKIP policy, or UX semantics, it is BLOCKED until the relevant question is explicitly decided.

## 4. Availability confirmation design

Q-002 is intentionally narrower than the former question. It does not reopen source identity. Its read-only confirmation record shall use this matrix:

| Fact/semantic to confirm | Required confirmation | Baseline constraint | Status |
|---|---|---|---|
| Canonical TЧ | Relevant TЧ for each model/vehicle category | Must be within `АпкПланТехническихРесурсов` | open |
| `Принят` | Whether/how accepted rows filter each relevant TЧ | Must not silently remove the approved source | open |
| Organization | Matching and scope rule | Organization remains an approved scope dimension unless superseded | open |
| Subdivision | Equality/hierarchy and whether demand/availability use same rule | Do not broaden/narrow silently | open |
| Quantity/capacity | Meaning of `Количество`; duplicate physical vehicles and capacity | No dedup/sum rule selected | open |

The confirmation is read-only and factual. It may refine the implementation contract only after owner acceptance; it does not itself close Q-002 or Q-003.

## 5. Remediation architecture by finding

### 5.1 P0 result contract

**Finding:** review P0-1; UI reads `Результат.Прошёл`, producer returns `Статус`.

**Delta:** align the consumer with the inherited producer contract and preserve explicit `PASS|FAIL|SKIP` states. Do not infer SKIP policy here. TEST-01/02/08 remain blocked on Q-007 where policy affects terminal verdicts.

**Traceability:** spec-002 T12/T13; requirements FR-005; tasks TEST-01, TEST-02, TEST-08.

### 5.2 P0 period cleanup

**Finding:** review P0-2; cleanup selection does not include date scope.

**Delta:** make deletion and write use the same owner-approved scope. The design intentionally does not select exact, overlap, or full-scenario semantics. Q-001 is required before SRV-01.

**Traceability:** spec-002 T13; requirements FR-004; tasks SRV-01.

### 5.3 Error handling and model properties

P1-1/P1-2/P1-3 are confirmed review deltas. Future implementation may repair logging argument construction, numeric substring checks, and catch boundaries, but may not select the missing-property/infrastructure error contract before Q-005.

**Traceability:** review P1-1/P1-2/P1-3; spec-002 T5/T9/T13; tasks SRV-05/SRV-06.

### 5.4 N+1 model-property access

P1-4 is a confirmed performance delta. A future implementation may batch/cache properties only with a proof that approved results remain equivalent. It must preserve the model coefficient rules from D-003/TD-003 and must not invent a fallback source.

**Traceability:** review P1-4; spec-002 D-003, TD-003, T5/T9; task SRV-07.

### 5.5 Test safety, truthfulness, and cleanup

P1-5/P1-6/P1-7 are confirmed test-safety/quality deltas. Runtime boundary, dedicated role, test marker, cleanup scope, and SKIP terminal policy remain decisions under Q-006/Q-007. No offline artifact grants permission to mutate roles or an IB.

**Traceability:** review P1-5/P1-6/P1-7; spec-002 T12/T13; tasks TEST-03..TEST-09.

### 5.6 UI and diagnostics

P2-1..P2-5 are confirmed review findings to be assessed against existing form contracts. P2-6 remains still open because organization scope is a business-rule question. UI-01..UI-06 cannot select behavior that conflicts with Q-008 or inherited spec-002 contracts.

**Traceability:** review P2-1..P2-6; spec-002 T3/T9/T11/T12; Q-008; tasks UI-01..UI-06.

## 6. Requirements mapping

| Requirement | Design coverage |
|---|---|
| FR-001 baseline anchor | §§1–3; T13/6693e570 |
| FR-002 availability identity | §3.1; D-006/TD-007; T8/T9 |
| FR-003 narrowed Q-002 | §4; Q-002/Q-003 |
| FR-004 period gate | §5.2; Q-001; SRV-01 |
| FR-005 result contract | §5.1; P0-1; TEST-01/02/08 |
| FR-006 error semantics | §5.3; Q-005; SRV-05/06 |
| FR-007 test safety | §5.5; Q-006/Q-007; TEST-03..09 |
| FR-008 non-regression | §§3.2–3.3; all lanes |
| FR-009 task traceability | §7; tasks traceability table |
| NFR-001 no type changes | §§1, 3.2 |
| NFR-002 offline safety | §8 |
| NFR-003 future static gates | §8.2 |
| NFR-004 open questions | §9 |
| NFR-005 heartbeat | §8.3 |

## 7. Decision and task traceability rules

Every task in `tasks.md` must include:

- a direct reference to one or more spec-002 decisions/tasks (`D-*`, `TD-*`, `T*`), and/or
- a direct reference to one or more dated review findings (`P0-*`, `P1-*`, `P2-*` from 2026-11-07);
- the exact closed-question gate required before execution, or an explicit `BLOCKED` state;
- one or more user-story IDs (`US-001`..`US-004`).

If a task would alter an inherited decision, its status is BLOCKED and it must name the future owner decision required. The 2026-11-07 finding alone cannot supersede D-006/TD-007 or any other spec-002 decision.

### 7.1 DEC-02 — Read-only full-configuration inventory

`DEC-02` is the only preparation permitted before semantic approval. It is a read-only inventory of the full configuration, limited to facts needed to answer Q-002, Q-006, and Q-008 and to construct the change manifest. It may inspect metadata, modules, forms, roles, and existing tests, but it may not edit them, close questions, or authorize implementation. It does not permit business-dependent BSL/XML, role, information-base, UI, or Vanessa work.

Traceability: US-002, US-003, US-004; FR-003, FR-007, FR-011; Q-002/Q-006/Q-008; SAFE-SDD-002 dependency; SAFE-SDD-003.

### 7.2 GATE-01 — Manifest scope guard

`GATE-01` is a documentation/checking control, not a source or metadata mutation. Before any future implementation task, inspect the declared change manifest and reject the change if it contains either:

1. any type configuration object change (including a type object itself, its properties, or its generated/type metadata); or
2. any unrelated main-configuration object change outside the approved extension/remediation scope.

The rejection is independent of `pre_load_validate.py`, `bsl_analyze`, and `v8std`: static-analysis PASS cannot override a scope violation. GATE-01 runs before those gates and must remain PASS for the implementation lane to proceed. This task changes only SDD documentation and therefore has no implementation manifest.

Traceability: US-001, US-003, US-004; FR-001, FR-008, FR-012; NFR-001.

### 7.3 Question gate manifest

| Gate | Exact prerequisite | Tasks it gates | Verification outcome |
|---|---|---|---|
| GATE-02-PERIOD | Q-001 closed | SRV-01 | period scope and non-regression PASS |
| GATE-02-AVAILABILITY | Q-002 and Q-003 closed | SRV-02 | availability contract PASS |
| GATE-02-CONCURRENCY | Q-004 closed | SRV-01 | concurrency/non-regression contract PASS |
| GATE-02-ERROR | Q-005 closed | SRV-03, SRV-04 | error contract PASS |
| GATE-03-TEST | Q-006 and Q-007 closed | TEST-01, TEST-02 | test boundary and result/SKIP PASS |
| GATE-04-UI | Q-008 closed | UI-01 | UI contract PASS |

No gate is closed by this documentation update. Every business-dependent BSL/XML, role, information-base, UI, or Vanessa task remains BLOCKED until its exact gate and separate implementation authorization are both closed.

### 7.4 User-story traceability

| User story | Requirements | Design/decision | Tasks | Verification |
|---|---|---|---|---|
| US-001 | FR-001, FR-002, FR-008, FR-012 | §§1–3; GATE-01 | SAFE-002-A, SAFE-002-D, TEST-01 | GATE-01; GATE-02 non-regression |
| US-002 | FR-003, FR-011 | §4; DEC-02 | SAFE-002-C, DEC-02 | DEC-02 inventory review; GATE-02-AVAILABILITY |
| US-003 | FR-004..FR-009, FR-010 | §§5–7; question gate manifest | SRV-01..SRV-04, TEST-01..TEST-04, UI-01 | exact question-gate review; GATE-02/03/04 |
| US-004 | FR-009..FR-013, NFR-001..NFR-005 | DEC-02; GATE-01 | DEC-02, GATE-01, all future tasks | manifest review; static gates only after GATE-01 |

## 8. Verification and gates

### 8.1 This task

Reconciled scope (owner decision 2026-11-09, variant 2): the documentation artifacts are approved and the safe implementation lane is authorized; verify exact scope fence, baseline references, finding references, open-question status, Q-002 wording, non-regression obligation, the question-to-task matrix, DEC-02, GATE-01, and US-001..US-004 traceability. Product static gates apply to every safe-lane BSL/XML change per 8.2; no product static gate was applicable to the completed documentation tasks because no BSL/XML was changed by them.

### 8.2 Future BSL/XML work

For every future BSL/XML edit, run, in order, and stop on failure:

1. `GATE-01` manifest scope check;
2. `python scripts/pre_load_validate.py`;
3. targeted non-empty `bsl_analyze` for changed directories/files;
4. `v8std` when available;
5. only then any separately authorized offline/DB/UI gate.

A static-analysis result never closes a question or overrides GATE-01. Database, Designer, COM, Vanessa, Chrome, role mutation, and destructive operations are permitted only in the separately authorized phase after the offline static gate; unresolved business-dependent tasks remain blocked.

### 8.3 Progress artifact

Append one concise result line to `C:/MyProjects/APKTechPlan/heartbeat/night.log` after verification. Do not treat the heartbeat as a substitute for the durable SDD traceability.

## 9. Decision status

Q-001..Q-008 are still open. DEC-02 permits only read-only inventory; GATE-01 is documentation/checking only. SAFE-SDD-003 makes no domain, security, availability, quantity, period, SKIP, or UX decision. All dependent implementation tasks remain BLOCKED. Spec-002 baseline behavior is inherited outside confirmed review deltas.
