# Промты оркестратора — пост-ночной прогон 2026-11-09

Общие правила для обоих промтов:
- Субагенты строго ПОСЛЕДОВАТЕЛЬНО, каждый получает только свой файл/вопрос.
- Модели ТОЛЬКО провайдера wormsoft: анализ — `wormsoft/deepseek-ai/deepseek-v4.1-flash-1017`
  (glm-5.3-flash 08.11 отдавал 500), тяжёлый синтез — `wormsoft/zai/glm-5.3:NVFP4`.
- max_turns: 6-8, формат ответа фиксированный, read-only если не сказано иное.
- Запрещено: 1С/Designer/COM/Vanessa/браузер/ИБ; правки `src/`, спеки-003 и heartbeat.

---

## PROMPT-A: починка дефектов воркфлоу-скриптов

Цель: устранить 2 дефекта, дважды сорвавшие ночной прогон, и проверить скрипты
сухим прогоном (dry-run), не запуская ни одного агента над реальными задачами.

Контекст для оркестратора:
- Ночной прогон 08-09.11.2026 оборвался дважды на одном и том же:
  1) ДЕФЕКТ-КОНТРАКТ: скрипты ждут `r.status === 'PASS'` (строгий enum),
     агенты возвращают свободный текст: 'completed', 'completed_with_blocker'.
     Итог: воркфлоу обрывается на первой/третьей задаче, verify-фаза не запускается.
  2) ДЕФЕКТ-ВЕРДИКТ: `if (synth.verdict === 'BLOCKED')` не матчит прозу
     синтезатора вида "BLOCKED for implementation..." -> фаза Implementation
     стартует вопреки вердикту BLOCKED.
- Файлы (untracked, в проекте):
  - C:/MyProjects/APKTechPlan/.pi/workflows/apktechplan-crossreview-fix.js
  - C:/MyProjects/APKTechPlan/.pi/workflows/apktechplan-fix-and-e2e.js
  - C:/MyProjects/APKTechPlan/.pi/workflows/apktechplan-remediation-night.js
  Эталон исполненных прогонов (для сверки сценариев):
  C:/Users/r.edokov/AppData/Local/Temp/pi-subagents-0/MyProjects-APKTechPlan/
  01a1bc94-2a77-71b0-a2e5-4d642b7a0564/tasks/wf_35b866cd902c.workflow.js (+.jsonl)

Оркестратор: модифицируй workflow-скрипты сам (точечные правки, diff до/после),
затем запусти ПОСЛЕДОВАТЕЛЬНО двух субагентов:

Субагент A1 (аналитик, wormsoft/deepseek-ai/deepseek-v4.1-flash-1017, max_turns 6):
  Прочитай три .js в .pi/workflows/. Найди ВСЕ места, где статус/вердикт агента
  сравнивается со строкой-константой. Верни таблицу: файл:строка — что сравнивается —
  какие варианты текста агента её ломают. Максимум 12 строк.

Действие оркестратора: внести правки:
  a) WORK_SCHEMA.status -> strict enum: 'PASS' | 'FAIL' | 'BLOCKED', в промптах
     агентов явно указать "return status as exactly one of: PASS, FAIL, BLOCKED";
     в скрипте нормализовать ввод (toUpperCase+trim, reject unknown) и логировать
     сырой ответ при reject.
  b) verdict синтезатора -> отдельное булево/enum поле (например blocked: true),
    сравнение по полю, а не по подстроке прозы.
  c) Никаких иных изменений логики фаз.

Субагент A2 (верификатор, wormsoft/deepseek-ai/deepseek-v4.1-flash-1017, max_turns 6):
  Прочитай изменённые скрипты. Верни: (1) перечислены ли все сравнения статусов
  из отчёта A1; (2) есть ли сценарий, при котором фаза Implementation стартует
  при BLOCKED; (3) node --check <файл> для каждого .js — PASS/FAIL.
  Максимум 10 строк.

Критерий готовности: оба дефекта закрыты, node --check зелёный, diff приложен
к ответу (только изменённые строки).

---

## PROMPT-B: форензик-аудит правок спеки-003

Цель: установить, кто и когда фактически записал противоречивые статусы, и
проверить содержательные заявления fix-агентов против диска.

Контекст: fix-агенты SAFE-SDD-001..003 (воркфлоу wf_35b866cd902c, 07:54-09:04)
заявили «reconciled to Draft/BLOCKED» + PASS-гейты; на диске .status =
'implementation:in-progress' (mtime 09:09), requirements/design/tasks mtime
09:31 — ПОЗЖЕ конца воркфлоу. Спека-003 untracked, git-истории нет.

Оркестратор: только анализ, никаких правок. ПОСЛЕДОВАТЕЛЬНО:

Субагент B1 (хронолог, wormsoft/deepseek-ai/deepseek-v4.1-flash-1017, max_turns 8):
  1) Сними точные mtime (birth/change) пяти файлов спеки-003 и INDEX.md:
     powershell.exe -NoProfile -Command "Get-Item '<file>' | Select Name,CreationTime,LastWriteTime"
  2) Из логов сессий pi за 09:04-09:35 найди, кто писал в spec-003:
     grep -l "003-remediation" в сессиях
     C:/Users/r.edokov/.pi/agent/sessions/--C--MyProjects-APKTechPlan--/2026-11-09T*.jsonl
     затем в найденных - grep контекста write/edit у spec-003 файлов (tool_use с
     file_path). Тот же поиск поwf_b3eb3599c9bf (09:23-09:29) и его .output.
  3) Из heartbeat/night.log возьми строки 09:05-09:35.
  Верни хронологическую таблицу: время — актор — действие с файлом. Максимум 15 строк.

Субагент B2 (контент-ревьюер, wormsoft/deepseek-ai/deepseek-v4.1-flash-1017,
max_turns 8):
  Сравни ЗАЯВЛЕННОЕ (тексты fix-агентов в wf_35b866cd902c.workflow.jsonl,
  записи idx 4,5,6 — читай фрагментами по 2500 символов) с ФАКТИЧЕСКИМ
  содержанием requirements.md/design.md/tasks.md/.status/INDEX.md
  (C:/MyProjects/APKTechPlan/.ai/sdd/specs/003-remediation-code-review/).
  Для каждого SAFE-SDD-001/002/003: заявлено vs найдено на диске vs ОТСУТСТВУЕТ.
  Особо: матрица 11 блоков cross-reference, Q-002 narrowing, FR-008/US-001..004,
  GATE-01, DEC-02 (inventory.md существует?). Максимум 15 строк.

Критерий готовности: атрибуция противоречивых статусов (кто записал 'Approved/
in-progress' и когда) либо доказана, либо честно признана недоказуемой;
перечень расхождений заявлений агентов с диском.
