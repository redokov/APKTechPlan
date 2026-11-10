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

**Status:** DECIDED (owner decision 2026-11-09, chat): overlapping-interval cleanup.
Clearing removes every register row whose period intersects the requested
range by at least one day, and the demand selection is made by the same
intersection rule so every removed row is rewritten. Register semantics:
"always reflects the last calculation over the whole affected range".
Non-regression obligation: January/February rows must survive a March-only
recalculation unless they intersect March. SRV-01 remains additionally gated
by Q-004 (concurrency) per the 8a matrix.

### Q-002: Availability facts and semantics

**Status:** DECIDED (owner decision 2026-11-09, chat; facts per inventory.md):
- source: main-config Документ.АпкПланТехническихРесурсов ONLY; extension
  document Тх_ПланТехническихРесурсов is excluded entirely and its metadata
  object will be REMOVED from the CFE (test fixtures migrate to the
  main-config document);
- unit: one row = one physical vehicle (state number); no Количество column;
- "Принят" filter: removed — a row of a POSTED document is accepted by
  definition;
- calculation (2-а = A2, two-level): level 1 — demand of a subdivision is
  first covered by vehicles ATTACHED to that subdivision; level 2 — the
  remainder is covered by the shared pool of ALL organizations of the
  scenario (2-б = B2: the pool crosses organization boundaries). The deficit
  register stores TWO numbers: "shortage after own vehicles" and "final
  deficit after the shared pool"; the report shows required moves
  (attachment org/subdivision -> demand org/subdivision);
- categories (2-в = V1): all four tabular parts are canonical (Техника,
  Оборудование, Автотранспорт, Прицепы); the extension enum gets a fourth
  value "Прицеп"; trailer deficit is computed like vehicle deficit;
- demand side unchanged: yearly-plan turnover registers (fed by
  АпкТехнологическиеКартыНаКультуру) already provide org/subdivision/field/
  period/model/shifts; model matching via ТранспортноеСредство.АпкМодель;
  substitution by converted power remains.
Decisions recorded earlier (narrowing by SAFE-SDD-002) remain in force.

Provide read-only confirmation against the full configuration of:

- which tabular parts of the already-approved `Документ.АпкПланТехническихРесурсов` are canonical for each model/vehicle category;
- whether and how `Принят` filters rows in each relevant tabular part;
- whether organization is part of the availability scope and how it is matched;
- whether subdivision matching is equality or hierarchy and whether the same rule applies to demand and availability;
- whether `Количество` is allocated capacity, physical-vehicle count, or another quantity, and how duplicate vehicle rows are interpreted.

This question did **not** ask whether the source is `Тх_ПланТехническихРесурсов` or
`АпкПланТехническихРесурсов`: D-006/TD-007 preserve the latter as the current
baseline. The factual sub-questions were answered read-only and are recorded in
`inventory.md`; the semantic part is closed by the decision above.

### Q-003: Duplicate vehicles and attachment period

**Status:** DECIDED (owner decision 2026-11-09, chat; facts per inventory.md and
read-only probes `scripts/q003_probe_readonly*.py`):

- **duplicates — no action** (owner: "ничего не делаем"). Units are counted per
  PHYSICAL VEHICLE taken from the posted plan documents of the scenario: a
  repeated row of the same `ТранспортноеСредство` does not increase
  availability. No deduplication flag, no warning and no posting lock is added.
  Recorded consequence: demo document `НВЦБ-000001` lists
  "John Deer, Гос.№ВК30-64ВН3" twice, so the model counts 3 units, not 4;
- **attachment source is changed**: which subdivision/organization a machine
  belongs to is NO LONGER read from the plan document. The source of truth is
  `РегистрСведений.АпкИсторияТранспортныхСредств` (periodicity Day, independent,
  dimension `ТранспортноеСредство`, resources `Организация` and
  `ЭксплуатирующееПодразделение`);
- **slice rule (variant П2)**: `СрезПоследних` is taken ONCE for the whole
  calculation, at the START of the calculated period (`ДатаНачала`); when
  `ДатаНачала` is empty — at the plan document date. Interval/time-weighted
  accounting (variant П3) is NOT introduced: a machine transferred inside the
  period is attributed to the slice subdivision for the whole period;
- a machine without a history record receives no level-1 attachment: it
  contributes to the shared scenario pool (level 2) only;
- the plan document keeps its Q-002 role — it defines the SET of machines
  available to the scenario; the organization/subdivision placement of each
  machine comes from the slice;
- category consistency confirmed read-only: every tabular part matches the
  `АпкМодель` type (`Техника`↔СХТехники, `Оборудование`↔СХОборудования,
  `Автотранспорт`↔Автотранспорта, `Прицепы`↔Прицепов) and no machine appears in
  two parts.

Derived consequences for SRV-02 (implementation notes, not new decisions):

- the document tabular part `Подразделения` no longer scopes availability;
  availability rows are built per machine from the slice, so availability
  filters by organization/subdivision apply to the slice values, not to the
  document header;
- `Исправно` (a periodic resource of the same register) is NOT used for
  availability in this decision and stays out of scope until separately decided;
- the earlier demo-data shape (early history records with an empty organization)
  is why the slice must be `СрезПоследних`, not a first record.

Decisions recorded for Q-002 remain in force.

### Q-004: Concurrency

**Status:** DECIDED (owner decision 2026-11-09, chat; facts from a read-only code
review of `Тх_ТехникаСервер.РассчитатьДефицит`):

- **scheme С1 — dimension locking with all reads inside the transaction.** The
  demand read, the plan-document read and the history-register slice move INSIDE
  the transaction, after the write set is known and the managed lock is
  acquired. There is no "read outside, write inside" window;
- **exact key set, not a coarse group.** The lock element uses
  `ИсточникДанных` (a query result) with `ИспользоватьИзИсточникаДанных`, so the
  lock covers exactly the register keys of the affected set: rows that will be
  deleted by the period-overlap cleanup plus the keys that will be written.
  `УстановитьЗначение` remains only where a single dimension value is fixed by
  the launch parameters;
- **bounded wait, then cancel.** A lock wait limit is set; on expiry the
  transaction is rolled back completely, the platform text is not shown, and the
  user gets an explicit message ("parallel calculation for this scope is running,
  run the calculation again when convenient"). **No automatic retry** — the owner
  restarts the calculation himself;
- **plan documents are NOT locked** for the duration of the calculation. A plan
  document posted concurrently can change availability between reads; this
  residual risk is accepted and is corrected by the next recalculation;
- implementation note (not a new decision): after the lock is acquired, the
  delete-set selection is re-queried (cheap) so that a row committed by a
  competing calculation inside the narrow window between the first selection and
  the lock is not lost.

The approved spec-002 behavior outside this defect scope is unchanged: the
calculation still writes the result in one transaction and still fails without
partial changes.

### Q-005: Dynamic model-property error contract

**Status:** DECIDED (owner decision 2026-11-09, chat; facts from a read-only code
review of `Тх_ТехникаСервер`):

- **variant Р1 — classification by metadata, not by exception text.** Whether a
  model requisite exists is checked against the catalog metadata before the
  query. No parsing of platform error text is allowed (locale- and
  version-fragile);
- **absent requisite in metadata = version-mismatch situation**: write a journal
  entry of level "Warning", treat the property as unfilled, and CONTINUE the
  calculation. Read-only check of the current configuration shows that every
  attribute the code requests exists in all four model catalogs, so this outcome
  can only mean an АПК version mismatch, not ordinary data;
- **infrastructure failure** (no rights, broken query, disabled module, execution
  error) = incident: journal entry of level "Error", STOP the whole calculation
  with a clear user message that references the journal entry, and no partial
  register rows (the transaction is rolled back). An unknown failure is NEVER
  converted to zero;
- **no third state in the result.** The owner confirmed that a separate result
  mark "property unavailable" is not required — the journal entry is enough. The
  existing `КоэффициентНеЗадан` mark keeps its approved business meaning ("no
  filled requisite"), and its triggers are unchanged;
- the present swallowing points are removed: `ЗначениеРеквизитаМодели` no longer
  catches every exception into 0, and the non-reference branch of
  `ИмяСправочникаПоТипуСсылки` no longer degrades silently;
- SRV-04 stays bound to this contract: batch/cache loading must preserve the same
  classification and must prove numerical equivalence of substitution
  coefficients to the current behavior.

The approved spec-002 coefficient and fallback semantics are unchanged.

### Q-006: Test runner boundary

**Status:** DECIDED (owner decision 2026-11-09, chat; the owner adopted the
recommended combination and added a deferred work item):

- **runner placement — К1б now, К1а deferred.** The runner (`Тх_РаннерТестов`)
  and the test module (`Тх_Тесты`) stay in the working CFE for this development
  phase, but gain a hard guard: every test entry point and every writing test
  helper refuses to run unless the test-infobase marker is set, and raises a
  clear exception otherwise. Extracting the runner and the test module into a
  SEPARATE test extension (К1а) is registered as future work **after this
  development phase is finished** (task TEST-03, explicitly deferred);
- **test-infobase marker — К2а + К2в.** A boolean CFE constant (proposed name
  `Тх_ТестоваяБаза`, default False) holds the in-database marker and is set only
  in the test infobase; as an additional independent line the launch scripts also
  verify the target infobase reference before running anything. A session
  parameter (К2б) is NOT used because the platform cannot set it from the command
  line without reworking the launch pipeline;
- **roles — К3а.** Only the external script may assign or remove roles; the script
  must restore the original role state on ANY exit (guaranteed block, not a
  trailing statement), must verify the restoration at the end, and a failed
  restoration is a VISIBLE run failure. Scenarios inside 1C must not change roles;
- **cleanup — К4а.** Every run keeps a registry of created objects (catalogs and
  documents); cleanup runs from that registry on any exit; a failed cleanup is a
  VISIBLE run failure with the list of leftovers written to an artifact file next
  to the logs; scenario fixtures are additionally swept by their name masks
  (`Тх_Тест…`, `Тх_Тест4…`, `Тх_VA_…`). A journal entry of level "Information"
  is not an acceptable substitute for visibility.

Read-only facts behind the decision: the runner executes all 20 tests
unconditionally; the CFE contains no test-infobase marker of any kind; cleanup
failures are currently swallowed at "Information" level with the comment "the
next run will remove the leftovers", while grouping-test fixtures carry unique
identifiers that cannot be found by mask; the role-restore step in the T12 driver
is not in a guaranteed block, so an early `return` leaves the user's roles
changed.

### Q-007: SKIP policy

**Status:** DECIDED (owner decision 2026-11-09, chat): **variant Ж1 — a SKIP is
always a failure, everywhere.**

- the terminal verdict of a run is failure whenever any test did not actually
  pass; SKIP is not a separate acceptable outcome;
- `run_unit_tests.py`: the "exit code 2 = SKIP-only, not a failure" contract is
  RETIRED. Any SKIP produces a failing run (exit 1) with an explicit message.
  The skip counter and the reason remain printed and stored in the artifact —
  visibility stays, only the "not a failure" interpretation is removed;
- `run_va_feature.py` already treats anything not provably PASS as a failure;
  the two runners now follow one policy instead of two;
- the strict status parsing stays: an unrecognized or missing status remains a
  failure (fail-closed), and the expected-total check (20 tests) stays;
- mandatory consequence (obligation of TEST-01/TEST-02, not a new decision): the
  current baseline "19 PASS + 1 SKIP" becomes a RED run. The skipped test must
  lose its skip cause — either the required data is guaranteed before the run or
  the test is rewritten so that its conditions always hold. Deleting or disabling
  the test to obtain green is not allowed, and the T13 non-regression baseline
  must be re-established as 20 PASS, not as "green with one skip".

### Q-008: Form UX and platform events

**Status:** DECIDED (owner decision 2026-11-09, chat; facts from a read-only review
of the forms, the report data-composition template and the form modules):

- **empty result — variant (b).** The report still opens (the current behavior is
  kept, the P2-1 recommendation to terminate the procedure is NOT adopted), but a
  "no data" text is configured in the data-composition scheme, so a report opened
  from the section no longer shows a blank sheet without explanation. The
  zero-record user message in the calculation form stays as well;
- **stale values — variant (c), full form.** The calculation moment is stored and
  the report detects whether the sources changed after it, marks the data as stale
  and offers a recalculation. This adds the scope of tracking changes of the
  demand and availability sources; the exact detection mechanism is an engineering
  choice to be settled during implementation (candidate mechanisms: a stored
  per-row calculation moment compared with the latest change moment of the demand
  registers and of the availability documents, with the standard "change dates"
  facility preferred when available). The factual constraint is recorded: the
  deficit register is non-periodical and currently carries NO calculation
  timestamp, so staleness cannot be detected without adding one;
- **client-side input validation — variant (a).** Before the server call the form
  checks: period boundaries are filled, the start is not later than the end, and
  "shifts per day" is greater than zero; failures are shown as a message, not as a
  platform exception;
- **supported platform events — variant (a).** A closed list of supported events is
  fixed in the specification — `ПриИзменении`, `НачалоВыбора`,
  `ПередНачаломДобавления`, `ПриСозданииНаСервере`, and form commands — with the
  rule that handlers outside this list must not be added without verifying them on
  platform 8.5. Read-only check confirmed the live forms contain no dead handler
  bindings; the document-form counter defect (P2-3) disappears together with the
  CFE document removed by Q-002;
- **write-error diagnostics — variant (a).** In the work-plan form the "no data"
  branch and the "write/access operation failed" branch are separated, the original
  error is journaled and the user sees a meaningful message instead of the
  misleading "техкарты не найдены".

Approved spec-002 form and public contracts outside these findings are unchanged.

## 8a. Question-to-gate matrix

All questions are closed as of 2026-11-09 (owner decisions recorded in chat); the column below records each gate state. The following matrix is normative: an implementation task is executable only after every question in its gate column is explicitly closed by an owner decision. `DEC-02` is the sole pre-approval preparation lane; it is read-only and cannot close a question. The "Status" column below records the gate state as of 2026-11-09.

| Question | Exact requirements | Implementation tasks blocked | Verification gate blocked | Pre-approval preparation | Status 2026-11-09 |
|---|---|---|---|---|---|
| Q-001 | FR-004, FR-008 | SRV-01 | GATE-02 period-scope/non-regression | DEC-02 inventory only | DECIDED (overlap-interval cleanup) |
| Q-002 | FR-003, FR-008, FR-011 | SRV-02, UI-01 | GATE-02 availability-contract | DEC-02 inventory only | DECIDED (availability contract) |
| Q-003 | FR-003, FR-008 | SRV-02 | GATE-02 availability-contract | DEC-02 inventory only | DECIDED (per-machine count; attachment from АпкИсторияТранспортныхСредств, slice last, once at period start) |
| Q-004 | FR-008 | SRV-01 | GATE-02 concurrency/non-regression | DEC-02 inventory only | DECIDED (С1; exact-key managed lock via source data; bounded wait then cancel, no retry; plan documents not locked) |
| Q-005 | FR-006, FR-008 | SRV-03, SRV-04 | GATE-02 error-contract | DEC-02 inventory only | DECIDED (Р1 metadata-based split; absent requisite = Warning + continue; infrastructure = Error + stop; no third result state) |
| Q-006 | FR-007, FR-008, FR-011 | TEST-02 | GATE-03 test-boundary | DEC-02 inventory only | DECIDED (runner stays + guard, extraction deferred to TEST-03; marker = CFE constant + script check; roles only by script with guaranteed restore; cleanup by registry, visible failure) |
| Q-007 | FR-005, FR-007, FR-008 | TEST-01, TEST-02 | GATE-03 result/SKIP | DEC-02 inventory only | DECIDED (Ж1: SKIP is always a failure; exit-code 2 retired; visibility kept; skipped test must lose its cause) |
| Q-008 | FR-008, FR-011 | UI-01 | GATE-04 UI-contract | DEC-02 inventory only | DECIDED (no-data text in DCS while the report still opens; full staleness marking with stored calculation moment; client-side input checks; closed list of supported events; split no-data from write failures) |

No matrix row grants implementation permission. A static-analysis PASS cannot bypass an unresolved question or GATE-01.

## 9. Decision status

No new business decision is made by SAFE-SDD-003 itself. Spec-002 D-006/TD-007 remain inherited. Confirmed review findings are remediation deltas only.

Owner decisions recorded in chat on 2026-11-09: Q-001 (overlap-interval cleanup), Q-002 (availability contract), Q-003 (per-machine count and attachment from `АпкИсторияТранспортныхСредств`, slice last taken once at period start), Q-004 (concurrency: exact-key managed lock, all reads inside the transaction, bounded wait then cancel without retry), Q-005 (error contract: metadata-based classification, Warning and continue for an absent requisite, Error and stop for infrastructure failure), Q-006 (test boundary: guarded runner, CFE marker plus script check, script-only role changes with guaranteed restore, registry-based cleanup with visible failure; separate test extension deferred to TEST-03), Q-007 (SKIP is always a failure), Q-008 (form behaviour and supported events). **All eight questions are now closed.** Closing a question does not grant implementation permission: SRV-01..SRV-04, TEST-01, TEST-02 and UI-01 are READY (their gate questions are closed) and stay unauthorised until the owner gives an explicit implementation approval; TEST-03 stays deferred until this development phase ends. GATE-01 applies to every implementation lane.
