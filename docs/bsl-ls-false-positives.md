# bsl-ls 1.0.7: ложное срабатывание CommonModuleInvalidType (раскладка Designer-dump)

Дата: 2026-10-08. Задача A11 (атрибуция 2 × Error `Module.bsl:1 [CommonModuleInvalidType]`
в полном прогоне bsl-ls по дереву расширения `src/cfe/ПланированиеТехникиАПК`).

## Вердикт

**Ложное срабатывание bsl-language-server 1.0.7.** Исходники корректны, менять НЕЛЬЗЯ
(раскладка — авторитетный формат Designer 8.5, иного LoadConfigFromFiles не примет).

## Корень

MDClasses (внутри bsl-ls) при наличии `Configuration.xml` ищет метаданные общего модуля
по пути `CommonModules/<Имя>/<Имя>.xml`, а дамп Designer 8.5 кладёт их РЯДОМ с каталогом:
`CommonModules/<Имя>.xml` + `CommonModules/<Имя>/Ext/Module.bsl`. XML не найден → флаги
модуля читаются как «все false» → модуль не server / не ServerCall / не client /
не clientServer → `CommonModuleInvalidType` (по байткоду диагностики: срабатывает ровно
при этом условии — `javap CommonModuleInvalidTypeDiagnostic`, метод `flagsCheck`).

Каскадные артефакты того же корня (только в полном прогоне, исчезают при корректном
контексте): `PrivilegedModuleMethodCall` ×95, `NonStandardRegion` ×10, 
`CommonModuleMissingAPI` ×2, `CommonModuleNameFullAccess` ×1.

## Доказательства (все воспроизводимы)

1. **Байткод**: срабатывание ⟺ `!isServer && !isServerCall && !isClient && !isClientServer`.
2. **Минимальный репродьюс** (Temp/flagtest3): `Configuration.xml` + `CommonModules/TestMod.xml`
   (XML со валидными флагами `Server=true`) рядом с каталогом → 1 Error.
   Тот же XML, перенесённый ВНУТРЬ `TestMod/` → 0 Error. Без `Configuration.xml` → 0 Error.
3. **Наше дерево**: полный прогон с внешней раскладкой = 2 Error; после переноса 2 XML
   внутрь каталогов во временной копии = **0 Error** (17 файлов, 29 Warning).
4. **Флаги в наших XML валидны**: `Server=true, ExternalConnection=true, ServerCall=false`
   у обоих модулей (Тх_ТехникаСервер — Privileged=true, Тх_Тесты — Privileged=false).
5. **Раскладка авторитетна**: реальный дамп Designer 8.5 из базы
   (`C:/MyProjects/APKModSrc/CommonModules/`, `C:/MyProjects/ERPsrc/CommonModules/`) —
   XML «рядом», как у нас. Править исходники = сломать загрузку в ИБ (Фаза B).
6. Пофайловые/подкаталожные прогоны через MCP bsl-ls дают 0 Error лишь потому, что мост
   копирует файлы в ASCII-temp без контекста `Configuration.xml` — там диагностика
   молчит не потому, что «всё хорошо», а потому, что флаги не проверяются вовсе.

## Решение (без правки исходников)

Канонический full-tree гейт: `python scripts/bsl_ls_fulltree.py <cfe-dir>`
— копирует дерево в ASCII-temp, переносит `CommonModules/*.xml` внутрь каталогов
модулей (только в копии), гонит jar, парсит JSON-отчёт, печатает полный путь для
каждой диагностики (атрибуция не теряется), гейт = «файлов > 0 И Error == 0».

Текущий статус: **17 файлов, 0 Error, GATE PASSED** (29 Warning — стилевые ИТС,
не блокируют: MissingParameterDescription/QueryParseError(рантайм-сборка запросов)/
CognitiveComplexity/IfElseIfEndsWithElse).

## Классификация ложных срабатываний bsl-ls (накопительный список)

| Диагностика | Причина | Лечение |
|---|---|---|
| CommonModuleInvalidType | см. выше | `scripts/bsl_ls_fulltree.py`; исходники не трогать |
| UnusedLocalMethod | обработчики форм | `scripts/check_form_handlers.py` |
| QueryToMissingMetadata | объекты основной конфигурации в статическом тексте запроса | динамическая сборка `"ИЗ Справочник." + Имя()` (см. Тх_ТехникаСервер.ДанныеТранспортногоСредства, Тх_Тесты.СценарийСПотребностью) |
| CommonModuleInvalidType (старый кейс) | ServerCall=true + ExternalConnection=true | ServerCall=false у обоих общих модулей (сделано в A11) |
