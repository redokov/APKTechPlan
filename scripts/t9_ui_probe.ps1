# T9 UI-проверка формы обработки «Тх_ФормированиеПланаРаботТехники».
# Лог (UTF-8): heartbeat/t9_ui_probe.txt; скриншоты: heartbeat/t9_ui_*.png
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms

$logPath = "C:\MyProjects\APKTechPlan\heartbeat\t9_ui_probe.txt"
$log = New-Object System.Collections.Generic.List[string]
function L([string]$m) { $script:log.Add($m); Write-Output $m }

function Shot([string]$name) {
    $out = "C:\MyProjects\APKTechPlan\heartbeat\" + $name
    $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
    $bmp = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
    $bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose(); $bmp.Dispose()
    L ("SHOT: " + $name)
}

function FindFirst($scope, $like, $types) {
    foreach ($e in $scope.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)) {
        if ($e.Current.Name -like $like) {
            if (-not $types -or $types -contains $e.Current.ControlType.ProgrammaticName) { return $e }
        }
    }
    return $null
}

function Activate($e) {
    try { $e.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke(); return $true } catch {}
    try { $e.GetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern).Select(); return $true } catch {}
    try {
        $ec = $e.GetCurrentPattern([System.Windows.Automation.ExpandCollapsePattern]::Pattern)
        $ec.Expand(); return $true
    } catch {}
    return $false
}

$v8c = "C:\Program Files\1cv8\8.5.4.1683\bin\1cv8c.exe"
$a = "/S localhost\dev_erpapk_demo /N `"Администратор (ОрловАВ)`" /P `"`" /DisableStartupDialogs /DisableStartupMessages"
$proc = Start-Process -FilePath $v8c -ArgumentList $a -PassThru
L ("launched pid=" + $proc.Id)

$root = [System.Windows.Automation.AutomationElement]::RootElement
$main = $null
$deadline = (Get-Date).AddSeconds(150)
while ((Get-Date) -lt $deadline -and -not $main) {
    Start-Sleep -Seconds 5
    if ($proc.HasExited) { L "PROCESS EXITED"; break }
    foreach ($c in $root.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)) {
        if ($c.Current.ProcessId -eq $proc.Id -and $c.Current.ControlType.ProgrammaticName -eq "ControlType.Window") { $main = $c; break }
    }
}
if (-not $main) { L "MAIN WINDOW NOT FOUND"; $log | Out-File $logPath -Encoding UTF8; exit 2 }
L ("main: " + $main.Current.Name)

# 1. «Все функции»
$allf = FindFirst $main "Все функции*" $null
if (-not $allf) {
    # иногда пункт спрятан в выпадающем меню навигационной панели - ищем кнопку с меню
    $allf = FindFirst $main "Все функции" @("ControlType.MenuItem","ControlType.Button","ControlType.TabItem")
}
if (-not $allf) { L "ALLFUNCTIONS NOT FOUND"; Shot "t9_ui_no_allfuncs.png"; $log | Out-File $logPath -Encoding UTF8; exit 3 }
L ("allfuncs: " + $allf.Current.Name + " " + $allf.Current.ControlType.ProgrammaticName)
[void](Activate $allf)
Start-Sleep -Seconds 6

# окно/панель «Все функции» могло открыться; ищем узел «Обработки»
$cur = $main
$obrab = FindFirst $cur "Обработки" @("ControlType.TreeItem")
if (-not $obrab) { $obrab = FindFirst $cur "Обработки*" $null }
if (-not $obrab) { L "OBRABOTKI NODE NOT FOUND"; Shot "t9_ui_allfuncs.png"; $log | Out-File $logPath -Encoding UTF8; exit 4 }
L ("obrabotki: " + $obrab.Current.Name)
try { $obrab.GetCurrentPattern([System.Windows.Automation.ExpandCollapsePattern]::Pattern).Expand() } catch {}
Start-Sleep -Seconds 3

# 2. Наша обработка (по синониму или имени)
$dp = FindFirst $cur "Формирование плана работ техники*" $null
if (-not $dp) { $dp = FindFirst $cur "Тх_ФормированиеПланаРаботТехники*" $null }
if (-not $dp) { L "PROCESSOR NOT FOUND"; Shot "t9_ui_obrabotki.png"; $log | Out-File $logPath -Encoding UTF8; exit 5 }
L ("processor: " + $dp.Current.Name + " " + $dp.Current.ControlType.ProgrammaticName)
[void](Activate $dp)
Start-Sleep -Seconds 4
# если раскрылся дочерний «Форма» - выбрать его
$formNode = FindFirst $cur "Форма*" @("ControlType.TreeItem","ControlType.ListItem")
if ($formNode -and $formNode.Current.Name -eq "Форма") {
    L "subform node found"
    [void](Activate $formNode)
    Start-Sleep -Seconds 5
}
Start-Sleep -Seconds 4

# 3. Окно формы обработки
$formWin = $null
foreach ($c in $root.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)) {
    if ($c.Current.ProcessId -eq $proc.Id -and $c.Current.Name -like "*Формирование плана работ техники*") { $formWin = $c; break }
}
if (-not $formWin) { L "FORM WINDOW NOT FOUND"; Shot "t9_ui_after_open.png"; $log | Out-File $logPath -Encoding UTF8; exit 6 }
L ("form window: [" + $formWin.Current.Name + "]")

Shot "t9_ui_form.png"

# 4. Перечисление ключевых элементов формы
$expect = @(
    "Сценарий планирования*", "Период с*", "Период по*", "Дней в периоде*",
    "Смен в день*", "Текущий документ (перезаполнить)*", "Сформировать*"
)
foreach ($exp in $expect) {
    $el = FindFirst $formWin $exp $null
    if ($el) { L ("OK element: [" + $el.Current.Name + "] " + $el.Current.ControlType.ProgrammaticName) }
    else { L ("MISSING element: " + $exp) }
}

# 5. «Сформировать» без сценария -> асинхронное предупреждение
$btn = FindFirst $formWin "Сформировать" @("ControlType.Button")
if ($btn) {
    L "invoking Сформировать (empty scenario)"
    $btn.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke()
    Start-Sleep -Seconds 5
    $warn = $null
    foreach ($c in $root.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)) {
        if ($c.Current.ProcessId -eq $proc.Id -and $c.Current.Name -like "*Укажите сценарий*") { $warn = $c; break }
    }
    if (-not $warn) {
        $warn = FindFirst $root "*Укажите сценарий планирования*" $null
    }
    if ($warn) {
        L "WARNING SHOWN: (async, NFR-001)"
        Shot "t9_ui_warning.png"
        $ok = FindFirst $warn "ОК" @("ControlType.Button")
        if (-not $ok) { $ok = FindFirst $warn "Закрыть*" @("ControlType.Button") }
        if ($ok) { [void](Activate $ok); L "warning closed" }
    } else {
        L "WARNING NOT FOUND (check screenshot)"
        Shot "t9_ui_no_warning.png"
    }
} else {
    L "BUTTON Сформировать NOT FOUND"
}

Shot "t9_ui_final.png"
Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
L "DONE"
$log | Out-File $logPath -Encoding UTF8
Write-Output "LOG: $logPath"
