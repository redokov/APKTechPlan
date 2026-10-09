# T9 UI-проверка формы «Тх_ФормированиеПланаРаботТехники» (v2, через /Execute зонд).
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
    return $false
}

$v8c = "C:\Program Files\1cv8\8.5.4.1683\bin\1cv8c.exe"
$epf = "C:\MyProjects\APKTechPlan\build\Тх_ЗондОткрытияФормы.epf"
$a = "/S localhost\dev_erpapk_demo /N `"Администратор (ОрловАВ)`" /P `"`" /DisableStartupDialogs /DisableStartupMessages /Execute `"$epf`""
$proc = Start-Process -FilePath $v8c -ArgumentList $a -PassThru
L ("launched pid=" + $proc.Id)

$root = [System.Windows.Automation.AutomationElement]::RootElement
$deadline = (Get-Date).AddSeconds(180)
$formWin = $null
$main = $null
while ((Get-Date) -lt $deadline -and -not $formWin) {
    Start-Sleep -Seconds 5
    if ($proc.HasExited) { L "PROCESS EXITED"; break }
    foreach ($c in $root.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)) {
        if ($c.Current.ProcessId -ne $proc.Id) { continue }
        if (-not $main -and $c.Current.ControlType.ProgrammaticName -eq "ControlType.Window") { $main = $c }
        if ($c.Current.Name -like "*Формирование плана работ техники*") { $formWin = $c }
    }
}
if ($main) { L ("main: " + $main.Current.Name) }
if (-not $formWin) {
    L "FORM WINDOW NOT FOUND"
    if ($main) { Shot "t9_ui_v2_noform.png" }
    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    $log | Out-File $logPath -Encoding UTF8
    exit 2
}
L ("form window: [" + $formWin.Current.Name + "]")
Start-Sleep -Seconds 3
Shot "t9_ui_form.png"

# Перечисление ключевых элементов формы (текст из UIA, без OCR)
$expect = @(
    "Сценарий планирования*", "Организация*", "Подразделение*", "Период с*",
    "Период по*", "Дней в периоде*", "Смен в день*",
    "Текущий документ (перезаполнить)*", "Сформировать*"
)
$missing = 0
foreach ($exp in $expect) {
    $el = FindFirst $formWin $exp $null
    if ($el) { L ("OK element: [" + $el.Current.Name + "] " + $el.Current.ControlType.ProgrammaticName) }
    else { L ("MISSING element: " + $exp); $missing++ }
}

# «Сформировать» без сценария -> асинхронное предупреждение (NFR-001)
$btn = FindFirst $formWin "Сформировать" @("ControlType.Button")
if ($btn) {
    L "invoking Сформировать (empty scenario)"
    $btn.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke()
    Start-Sleep -Seconds 6
    $warn = $null
    foreach ($c in $root.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)) {
        if ($c.Current.ProcessId -eq $proc.Id -and $c.Current.Name -like "*Укажите сценарий*") { $warn = $c; break }
    }
    if (-not $warn) { $warn = FindFirst $root "*Укажите сценарий планирования*" $null }
    if ($warn) {
        L "WARNING SHOWN (async, NFR-001)"
        Shot "t9_ui_warning.png"
        $ok = FindFirst $warn "ОК" @("ControlType.Button")
        if (-not $ok) { $ok = FindFirst $warn "Закрыть*" @("ControlType.Button") }
        if ($ok) { [void](Activate $ok); L "warning closed" }
        else {
            # предупреждение может быть не-окно, а элемент в форме - ищем и жмём ОК глобально
            $ok = FindFirst $root "ОК" @("ControlType.Button")
            if ($ok) { [void](Activate $ok); L "warning closed (global OK)" }
        }
    } else {
        L "WARNING NOT FOUND (see screenshot)"
        Shot "t9_ui_no_warning.png"
    }
} else {
    L "BUTTON Сформировать NOT FOUND"
    $missing++
}

Shot "t9_ui_final.png"
Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
if ($missing -gt 0) { L ("DONE WITH MISSING: " + $missing) } else { L "DONE ALL OK" }
$log | Out-File $logPath -Encoding UTF8
Write-Output "LOG: $logPath"
