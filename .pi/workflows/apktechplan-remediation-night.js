export const meta = {
  name: 'apktechplan-remediation-night',
  description: 'Автономно исправить дефекты CFE по утверждённому SDD-плану',
  whenToUse: 'Только после явного разрешения пользователя и закрытия SDD-блокеров',
  phases: [
    { title: 'Preflight', detail: 'Проверить SDD approvals, git state, model and environment' },
    { title: 'Offline implementation', detail: 'Последовательно применить задачи с файловыми gate' },
    { title: 'Static gate', detail: 'Проверить итог и подготовить manifest без загрузки' },
    { title: 'Authorized operations', detail: 'Загрузить и проверить только подтверждённую test IB' },
    { title: 'Final report', detail: 'Сохранить evidence, rollback status and handoff' }
  ]
}

const argsObj = args || {}
const userAuthorization = argsObj.userAuthorization === true
const project = 'C:/MyProjects/APKTechPlan'
const spec = `${project}/.ai/sdd/specs/003-remediation-code-review`
const heartbeat = `${project}/heartbeat/night.log`
const model = 'erpband/deepseek-ai/deepseek-v4.1-flash-1017'

function agentPrompt(text, files, role) {
  return `You are the ${role} in an unattended 1C BSL remediation run for ${project}. Use model provider erpband only.\n\nTask:\n${text}\n\nRead first:\n- ${spec}/requirements.md\n- ${spec}/design.md\n- ${spec}/tasks.md\n\nScope fence:\nYou may modify only these files:\n${files.map(x => `- ${x}`).join('\n')}\nYou may create only explicitly named test/artifact files in this task. Do not touch unrelated files, the database, roles, Designer, Vanessa or Chrome unless the task explicitly says so. Never modify type configuration objects.\n\nRules:\n- Respect SDD status gates and unresolved BLOCKED questions. Do not invent business semantics.\n- Return the structured status field as EXACTLY one of the enum values allowed by your output tool (PASS, FAIL, BLOCKED; READY for gatekeeper decisions). Never put prose in the status field.\n- If a required decision/inventory is missing, stop with BLOCKED; do not implement a guess.\n- Do not run the database or UI in offline tasks.\n- After edits, run exactly the relevant local static gates: pre_load_validate.py, targeted bsl_analyze on a non-empty scope, v8std when available, and relevant offline tests.\n- If any gate fails, stop and report the exact command/output; do not retry the same approach more than twice.\n- Write progress/evidence to ${heartbeat}.\n\nReturn <=15 lines:\n## Done\n- ...\n## Tests\n- command and result\n## Files\n- modified/created\n## Blockers\n- none or exact blocker\n\nStop immediately after the task and its gates are complete.`
}

const DECISION_SCHEMA = { type:'object', properties:{ status:{type:'string',enum:['READY','BLOCKED','FAIL']}, blockers:{type:'array',items:{type:'string'}}, files:{type:'array',items:{type:'string'}}, summary:{type:'string'} }, required:['status','blockers','files','summary'] }
const WORK_SCHEMA = { type:'object', properties:{ status:{type:'string',enum:['PASS','FAIL','BLOCKED']}, changed:{type:'array',items:{type:'string'}}, gates:{type:'array',items:{type:'string'}}, blockers:{type:'array',items:{type:'string'}}, summary:{type:'string'} }, required:['status','changed','gates','blockers','summary'] }
const norm = s => typeof s === 'string' ? s.trim().toUpperCase() : s

const preflight = await agent(`Verify without editing: .status files for spec 003 must be requirements:approved, design:approved, tasks:approved; inspect whether Q-001..Q-008 are resolved in requirements.md; verify git status and required scripts/tools; verify exact model ${model} is available under erpband. No database/UI operations.`, [], 'SDD release gatekeeper', { schema: DECISION_SCHEMA, label:'preflight', phase:'Preflight', model })
if (!preflight || norm(preflight.status) !== 'READY' || !userAuthorization) {
  return { status: 'BLOCKED', reason: !preflight ? 'preflight failed' : (!userAuthorization ? 'explicit user authorization missing' : preflight.blockers), preflight }
}

const tasks = [
  { id:'SRV-01', text:'Implement approved period-scoped deficit-register replacement and its regression tests.', files:[`${project}/src/cfe/ПланированиеТехникиАПК/CommonModules/Тх_ТехникаСервер/Ext/Module.bsl`, `${project}/src/cfe/ПланированиеТехникиАПК/CommonModules/Тх_Тесты/Ext/Module.bsl`], role:'server data-correctness engineer' },
  { id:'SRV-02', text:'Unify availability source and table semantics according to DEC-01/DEC-02.', files:[`${project}/src/cfe/ПланированиеТехникиАПК/CommonModules/Тх_ТехникаСервер/Ext/Module.bsl`, `${project}/src/cfe/ПланированиеТехникиАПК/Documents/Тх_ПланТехническихРесурсов/Ext/ObjectModule.bsl`], role:'server query architect' },
  { id:'SRV-03', text:'Implement approved vehicle duplicate/capacity semantics and accepted filtering.', files:[`${project}/src/cfe/ПланированиеТехникиАПК/CommonModules/Тх_ТехникаСервер/Ext/Module.bsl`, `${project}/src/cfe/ПланированиеТехникиАПК/Documents/Тх_ПланТехническихРесурсов/Ext/ObjectModule.bsl`], role:'server domain-rule engineer' },
  { id:'SRV-04', text:'Implement approved consistency/lock strategy for source reads and output replacement.', files:[`${project}/src/cfe/ПланированиеТехникиАПК/CommonModules/Тх_ТехникаСервер/Ext/Module.bsl`], role:'1C concurrency engineer' },
  { id:'SRV-05', text:'Fix query exception classification and logging while preserving original errors.', files:[`${project}/src/cfe/ПланированиеТехникиАПК/CommonModules/Тх_ТехникаСервер/Ext/Module.bsl`], role:'BSL error-handling engineer' },
  { id:'SRV-06', text:'Separate absent business model properties from infrastructure/permission/module failures.', files:[`${project}/src/cfe/ПланированиеТехникиАПК/CommonModules/Тх_ТехникаСервер/Ext/Module.bsl`], role:'BSL metadata engineer' },
  { id:'SRV-07', text:'Batch-load and cache approved model properties to remove N×M dynamic queries.', files:[`${project}/src/cfe/ПланированиеТехникиАПК/CommonModules/Тх_ТехникаСервер/Ext/Module.bsl`], role:'BSL performance engineer' },
  { id:'UI-01', text:'Batch/cache vehicle autofill and deduplicate warnings.', files:[`${project}/src/cfe/ПланированиеТехникиАПК/Documents/Тх_ПланТехническихРесурсов/Forms/Тх_ФормаДокумента/Ext/Form/Module.bsl`], role:'managed-form engineer' },
  { id:'UI-02', text:'Remove stale model/хозномер according to approved UX.', files:[`${project}/src/cfe/ПланированиеТехникиАПК/Documents/Тх_ПланТехническихРесурсов/Forms/Тх_ФормаДокумента/Ext/Form/Module.bsl`], role:'managed-form UX engineer' },
  { id:'UI-03', text:'Move counters to client and support only confirmed row events.', files:[`${project}/src/cfe/ПланированиеТехникиАПК/Documents/Тх_ПланТехническихРесурсов/Forms/Тх_ФормаДокумента/Ext/Form/Module.bsl`,`${project}/src/cfe/ПланированиеТехникиАПК/Documents/Тх_ПланТехническихРесурсов/Forms/Тх_ФормаДокумента/Ext/Form.xml`], role:'managed-form platform engineer' },
  { id:'UI-04', text:'Implement approved zero-result deficit report behavior.', files:[`${project}/src/cfe/ПланированиеТехникиАПК/DataProcessors/Тх_РасчетДефицита/Forms/Форма/Ext/Form/Module.bsl`], role:'form UX engineer' },
  { id:'UI-05', text:'Separate no-data, unavailable-document and save-error diagnostics.', files:[`${project}/src/cfe/ПланированиеТехникиАПК/DataProcessors/Тх_ФормированиеПланаРаботТехники/Forms/Форма/Ext/Form/Module.bsl`], role:'form diagnostics engineer' },
  { id:'UI-06', text:'Add approved client validation for period and numeric parameters.', files:[`${project}/src/cfe/ПланированиеТехникиАПК/DataProcessors/Тх_ФормированиеПланаРаботТехники/Forms/Форма/Ext/Form/Module.bsl`,`${project}/src/cfe/ПланированиеТехникиАПК/DataProcessors/Тх_ФормированиеПланаРаботТехники/Forms/Форма/Ext/Form.xml`], role:'form validation engineer' },
  { id:'TEST-01', text:'Unify PASS/FAIL/SKIP result contract and remove executable Прошёл dependency.', files:[`${project}/src/cfe/ПланированиеТехникиАПК/CommonModules/Тх_Тесты/Ext/Module.bsl`,`${project}/src/cfe/ПланированиеТехникиАПК/DataProcessors/Тх_РаннерТестов/Ext/ObjectModule.bsl`,`${project}/src/cfe/ПланированиеТехникиАПК/DataProcessors/Тх_РаннерТестов/Forms/Форма/Ext/Form/Module.bsl`], role:'test harness contract engineer' },
  { id:'TEST-02', text:'Make failed assertions authoritative FAIL and add offline contract tests.', files:[`${project}/src/cfe/ПланированиеТехникиАПК/CommonModules/Тх_Тесты/Ext/Module.bsl`,`${project}/src/cfe/ПланированиеТехникиАПК/DataProcessors/Тх_РаннерТестов/Ext/ObjectModule.bsl`], role:'test correctness engineer' },
  { id:'TEST-03', text:'Guarantee fixture cleanup and expose cleanup failures.', files:[`${project}/src/cfe/ПланированиеТехникиАПК/CommonModules/Тх_Тесты/Ext/Module.bsl`], role:'test isolation engineer' },
  { id:'TEST-04', text:'Make Vanessa fixture setup/teardown token-scoped.', files:[`${project}/tests/vanessa/03-plan-tehresursov-prinyatye-tc.feature`,`${project}/tests/vanessa/04-preduprezhdenie-ts-dva-podrazdeleniya.feature`,`${project}/tests/vanessa/08-formirovanie-plana-rabot-tekhniki.feature`], role:'Vanessa isolation engineer' },
  { id:'TEST-05', text:'Add runtime safety gate for test runner.', files:[`${project}/src/cfe/ПланированиеТехникиАПК/DataProcessors/Тх_РаннерТестов/Ext/ObjectModule.bsl`,`${project}/src/cfe/ПланированиеТехникиАПК/CommonModules/Тх_Тесты/Ext/Module.bsl`], role:'1C test security engineer' },
  { id:'TEST-06', text:'Align dedicated role and delivered configuration.', files:[`${project}/src/cfe/ПланированиеТехникиАПК/Roles/Тх_Чтение/Ext/Rights.xml`,`${project}/src/cfe/ПланированиеТехникиАПК/Roles/Тх_Редактирование/Ext/Rights.xml`,`${project}/src/cfe/ПланированиеТехникиАПК/Configuration.xml`], role:'1C role engineer' },
  { id:'TEST-07', text:'Separate target-user authorization evidence from admin preparation.', files:[`${project}/scripts/run_va_feature.py`,`${project}/scripts/va_assign_roles_direct.py`,`${project}/tests/vanessa/README.md`], role:'authorization test engineer' },
  { id:'TEST-08', text:'Make Vanessa verdict consume strict JSON artifact.', files:[`${project}/scripts/run_va_feature.py`,`${project}/scripts/run_all_va.py`,`${project}/tests/vanessa/README.md`], role:'CI driver engineer' },
  { id:'TEST-09', text:'Snapshot and exactly restore roles on every outcome.', files:[`${project}/scripts/run_t12_roles.py`,`${project}/scripts/va_assign_roles_direct.py`], role:'role-state safety engineer' }
]

const results = []
for (const task of tasks) {
  const r = await agent(agentPrompt(task.text, task.files, task.role), {
    label: `exec:${task.id}`,
    phase: 'Offline implementation',
    agentType: 'general-purpose',
    model,
    effort: 'high',
    schema: WORK_SCHEMA
  })
  results.push({ id: task.id, result: r })
  if (!r || norm(r.status) !== 'PASS') return { status:'BLOCKED', failedTask:task.id, results }
}

const gate = await agent(agentPrompt('Run the complete offline/static gate over all changed artifacts only; do not edit files and do not load the database. Produce a manifest, list every command and exit/result, and mark blockers.', [`${project}/src/cfe/ПланированиеТехникиАПК`,` ${project}/scripts`,` ${project}/tests/vanessa`], 'release gatekeeper'), {
  label:'gate:static', phase:'Static gate', agentType:'general-purpose', model, effort:'high', schema:WORK_SCHEMA
})
if (!gate || norm(gate.status) !== 'PASS') return { status:'BLOCKED', stage:'static-gate', gate, results }

if (!userAuthorization) return { status:'READY_FOR_AUTHORIZATION', gate, results }
const db = await agent(agentPrompt('Execute only the authorized disposable/test IB operations described in DB-01..DB-06 and OPS-UI/OPS-TEST. Before each destructive operation verify snapshot, run token, authenticated user and rollback path. Stop and restore on any anomaly. Do not use production/shared IB.', [], 'authorized 1C operator'), { label:'ops:authorized', phase:'Authorized operations', agentType:'general-purpose', model, effort:'high', schema:WORK_SCHEMA })
return { status: db && norm(db.status) === 'PASS' ? 'PASS' : 'BLOCKED', gate, results, db }
