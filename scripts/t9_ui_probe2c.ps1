$ErrorActionPreference = "Stop"
Add-Type -AssemblyName UIAutomationClient
$logPath = "C:\MyProjects\APKTechPlan\heartbeat\t9_ui_probe2c.txt"
$log = New-Object System.Collections.Generic.List[string]
function L([string]$m) { $script:log.Add($m); Write-Output $m }
$v8c = "C:\Program Files\1cv8\8.5.4.1683\bin\1cv8c.exe"
$epf = "C:\MyProjects\APKTechPlan\build\Тх_ЗондОткрытияФормы.epf"
$out = "C:\MyProjects\APKTechPlan\heartbeat\t9_exec_log.txt"
$a = "ENTERPRISE /S localhost\dev_erpapk_demo /N `"Администратор (ОрловАВ)`" /P `"`" /DisableStartupDialogs /DisableStartupMessages /Execute `"$epf`" /Out `"$out`""
$proc = Start-Process -FilePath $v8c -ArgumentList $a -PassThru
L ("launched pid=" + $proc.Id)
$root = [System.Windows.Automation.AutomationElement]::RootElement
$deadline = (Get-Date).AddSeconds(150)
$main = $null
while ((Get-Date) -lt $deadline -and -not $main) {
    Start-Sleep -Seconds 5
    if ($proc.HasExited) { L "PROCESS EXITED"; break }
    foreach ($c in $root.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)) {
        if ($c.Current.ProcessId -eq $proc.Id -and $c.Current.ControlType.ProgrammaticName -eq "ControlType.Window") { $main = $c; break }
    }
}
if ($main) { L ("main: " + $main.Current.Name) }
Start-Sleep -Seconds 30
$n = 0
foreach ($e in $main.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)) {
    $nm = $e.Current.Name
    if ($nm -and $nm.Trim().Length -gt 0) {
        $n++
        if ($n -le 250) { L ("EL[" + $n + "]: [" + $nm.Substring(0, [Math]::Min(90, $nm.Length)) + "] " + $e.Current.ControlType.ProgrammaticName) }
    }
}
L ("named elements: " + $n)
Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
L "DONE"
$log | Out-File $logPath -Encoding UTF8
