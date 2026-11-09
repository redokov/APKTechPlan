export const meta = {
  name: 'apktechplan-crossreview-fix',
  description: 'Кросс-ревью SDD и безопасное исправление подтверждённых дефектов',
  whenToUse: 'После явного запроса на кросс-ревью и начало исправлений APKTechPlan',
  phases: [
    { title: 'Cross-review', detail: 'Независимо проверить согласованность SDD и готовность исправлений' },
    { title: 'Synthesis', detail: 'Отделить безопасные исправления от решений, требующих доменного ответа' },
    { title: 'Implementation', detail: 'Последовательно исправить только подтверждённые задачи' },
    { title: 'Verification', detail: 'Запустить статические гейты и подготовить отчёт' }
  ]
}

const model = 'erpband/deepseek-ai/deepseek-v4.1-flash-1017'
const modelSynth = 'erpband/zai/glm-5.3:NVFP4'
const project = 'C:/MyProjects/APKTechPlan'
const spec = `${project}/.ai/sdd/specs/003-remediation-code-review`
const report = `${project}/docs/review/review-report-2026-11-07.md`
const heartbeat = `${project}/heartbeat/night.log`

const REVIEW_SCHEMA = {
  type:'object', properties:{
    lens:{type:'string'}, verdict:{type:'string'}, blockers:{type:'array',items:{type:'string'}},
    safe_fixes:{type:'array',items:{type:'object',properties:{id:{type:'string'},title:{type:'string'},files:{type:'array',items:{type:'string'}},evidence:{type:'string'},acceptance:{type:'array',items:{type:'string'}},verification:{type:'array',items:{type:'string'}}},required:['id','title','files','evidence','acceptance','verification']}},
    conflicts:{type:'array',items:{type:'string'}}, missing:{type:'array',items:{type:'string'}}
  }, required:['lens','verdict','blockers','safe_fixes','conflicts','missing']
}
const SYNTH_SCHEMA = {
  type:'object', properties:{
    verdict:{type:'string'}, blocked:{type:'boolean'}, blockers:{type:'array',items:{type:'string'}},
    approved_safe_tasks:{type:'array',items:{type:'object',properties:{id:{type:'string'},title:{type:'string'},goal:{type:'string'},files:{type:'array',items:{type:'string'}},depends_on:{type:'array',items:{type:'string'}},acceptance:{type:'array',items:{type:'string'}},verification:{type:'array',items:{type:'string'}},role:{type:'string'}},required:['id','title','goal','files','depends_on','acceptance','verification','role']}},
    blocked_tasks:{type:'array',items:{type:'object',properties:{id:{type:'string'},reason:{type:'string'},needed_decision:{type:'string'}},required:['id','reason','needed_decision']}},
    sdd_changes:{type:'array',items:{type:'string'}}, report_summary:{type:'string'}
  }, required:['verdict','blocked','blockers','approved_safe_tasks','blocked_tasks','sdd_changes','report_summary']
}
const WORK_SCHEMA = { type:'object', properties:{status:{type:'string',enum:['PASS','FAIL','BLOCKED']},changed:{type:'array',items:{type:'string'}},gates:{type:'array',items:{type:'string'}},blockers:{type:'array',items:{type:'string'}},summary:{type:'string'}}, required:['status','changed','gates','blockers','summary'] }
const norm = s => typeof s === 'string' ? s.trim().toUpperCase() : s

const common = `Project: ${project}. Use ONLY model ${model} from provider erpband. Read-only unless the task explicitly says implementation. Do not run 1C database, Designer, COM, Vanessa, Chrome, role mutation, or destructive operations during offline implementation. Never modify type configuration objects. All BSL/XML edits require pre_load_validate.py, targeted bsl_analyze on a non-empty scope, and v8std when available. If an SDD question is unresolved, classify the dependent work BLOCKED; do not invent business semantics. Write progress to ${heartbeat}. Return status fields as EXACTLY the enum values allowed by your output tool (PASS, FAIL, BLOCKED), never prose.`

const lenses = [
  {key:'sdd', prompt:`${common}\nYou are the SDD consistency reviewer. Read completely: ${spec}/requirements.md, ${spec}/design.md, ${spec}/tasks.md, .ai/sdd/INDEX.md, .ai/steering/*.md, and ${report}. Check traceability, statuses, contradictions with completed spec 002, missing approvals, task dependencies, and whether the requested remediation can start without answering each open question. Identify only safe fixes that do not choose a business rule. Do not edit files. Return structured output.`},
  {key:'bsl', prompt:`${common}\nYou are the 1C technical cross-reviewer. Read the remediation SDD plus the existing review and inspect the exact referenced BSL/XML files. Verify which findings are reproducible from source and which require full configuration or domain decisions. Focus on runner contract, failed assertion status, query exception logging, caught model-property errors, period deletion, availability source, lock scope, and N×M queries. Do not edit files. Return structured output with exact files and conservative safe-fix boundaries.`},
  {key:'ops', prompt:`${common}\nYou are the release/test safety cross-reviewer. Read the remediation SDD, existing review, scripts, Vanessa features and runner/roles. Check whether offline fixes can be safely implemented now, what requires test-IB authorization, and whether proposed task gates/rollback rules are executable. Confirm safe runner/CI/form fixes separately from destructive or business-rule-dependent tasks. Do not edit files. Return structured output.`}
]
const reviews = await parallel(lenses.map(l => () => agent(l.prompt, {label:`cross:${l.key}`, phase:'Cross-review', agentType:'general-purpose', model, effort:'high', schema:REVIEW_SCHEMA})))
const usable = reviews.filter(Boolean)
const synth = await agent(`${common}\nYou are the lead SDD synthesizer. Reconcile these independent cross-review results:\n${JSON.stringify(usable)}\n\nProduce a conservative execution decision. The user explicitly asked to cross-review and then start fixing, so select only safe, source-confirmed, offline-editable tasks that do not require choosing open business rules or running an IB. Typical safe candidates may include the result-contract mismatch, failed-assertion status derivation, query-error logging, and an unambiguous zero-result form return, but include them only if reviews confirm them. Do not mark requirements/design/tasks approved and do not silently close Q-001..Q-008. For every blocked item give the exact missing decision. Ensure selected tasks do not edit the same file in parallel; order them. Return structured output. Set the boolean field blocked=false ONLY when you approve at least one safe task and no open question blocks that offline safe-lane work; set blocked=true when NO implementation may proceed (no safe tasks approved or evidence insufficient). Open business questions do not by themselves force blocked=true if the approved tasks require none of them. Return status fields as EXACTLY the enum values allowed by your output tool, never prose.`, {label:'cross:synthesis', phase:'Synthesis', agentType:'Plan', model:modelSynth, effort:'xhigh', schema:SYNTH_SCHEMA})
if (!synth || synth.blocked !== false || !Array.isArray(synth.approved_safe_tasks) || !synth.approved_safe_tasks.length) return {status:'BLOCKED', reviews:usable, synthesis:synth}

const results=[]
const safeTasks = synth.approved_safe_tasks.filter(t => !String(t.id).startsWith('SAFE-00'))
for (const task of safeTasks) {
  const prompt = `${common}\nYou are implementing approved safe remediation task ${task.id}: ${task.title}.\nGoal: ${task.goal}\nEvidence/acceptance:\n${task.acceptance.join('\n- ')}\nVerification:\n${task.verification.join('\n- ')}\nDependencies: ${task.depends_on.join(', ') || 'none'}\n\nScope fence — you may modify ONLY:\n${task.files.map(x=>'- '+x).join('\n')}\nDo not modify any other file or create unrelated files. Do not load the database. Implement the smallest production-safe change, preserve existing public contracts unless this task explicitly updates one, and add/update only the focused offline test/artifact needed by the acceptance criteria. Run the required static gates and report exact results. Stop on any gate failure.`
  const r=await agent(prompt,{label:`fix:${task.id}`,phase:'Implementation',agentType:'general-purpose',model,effort:'high',schema:WORK_SCHEMA})
  results.push({id:task.id,result:r})
  if(!r || norm(r.status)!=='PASS') return {status:'BLOCKED',reviews:usable,synthesis:synth,results}
}

const gate = await agent(`${common}\nYou are the final offline release gatekeeper. Do not edit files. Inspect git diff and all files changed by this workflow. Run: python scripts/pre_load_validate.py; targeted bsl_analyze for every changed BSL scope with a non-zero file count; v8std where available; relevant offline script tests; XML/handler consistency checks. Do not run any IB/UI operation. Produce a manifest and classify PASS only if all required gates pass and no changed file is outside synthesized safe tasks.`, {label:'verify:offline',phase:'Verification',agentType:'general-purpose',model,effort:'high',schema:WORK_SCHEMA})
return {status:gate && norm(gate.status)==='PASS'?'READY_FOR_USER_IB_AUTHORIZATION':'BLOCKED',reviews:usable,synthesis:synth,synthesisBlocked:synth.blocked,results,gate}
