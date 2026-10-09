$ErrorActionPreference = "Stop"
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
$logPath = "C:\MyProjects\APKTechPlan\heartbeat\t9_ui_probe2b.txt"
$log = New-Object System.Collections.Generic.List[string]
function L([string]$m) { $script:log.Add($m); Write-Output $m }
$v8c = "C:\Program Files\1cv8\8.5.4.1683\bin\1cv8c.exe"
$epf = "C:\MyProjects\APKTechPlan\build\Тх_ЗондОткрытияФормы.epf"
L ("epf exists: " + (Test-Path $epf))
$a = "/S localhost\dev_erpapk_demo /N `"Администратор (ОрловАВ)`" /P `"`" /DisableStartupDialogs /DisableStartupMessages /Execute `"$epf`""
$proc = Start-Process -FilePath $v8c -ArgumentList $a -PassThru
L ("launched pid=" + $proc.Id)
$root = [System.Windows.Automation.AutomationElement]::RootElement
$deadline = (Get-Date).AddSeconds(120)
$main = $null
while ((Get-Date) -lt $deadline -and -not $main) {
    Start-Sleep -Seconds 5
    if ($proc.HasExited) { L "PROCESS EXITED"; break }
    foreach ($c in $root.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)) {
        if ($c.Current.ProcessId -eq $proc.Id -and $c.Current.ControlType.ProgrammaticName -eq "ControlType.Window") { $main = $c; break }
    }
}
if ($main) { L ("main: " + $main.Current.Name) }
Start-Sleep -Seconds 25
$wins = 0
foreach ($c in $root.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)) {
    if ($c.Current.ProcessId -eq $proc.Id) {
        $wins++
        L ("WIN: [" + $c.Current.Name + "] " + $c.Current.ControlType.ProgrammaticName)
    }
}
L ("windows: " + $wins)
# сообщение об ошибке может быть внутри главного окна - ищем тексты
if ($main) {
    foreach ($e in $main.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)) {
        $n = $e.Current.Name
        if ($n -and ($n -like "*Зонд*" -or $n -like "*Формирование плана*" -or $n -like "*Ошибка*" -or $n -like "*не существует*" -or $n -like "*Внешняя обработка*")) {
            L ("EL: [" + $n + "] " + $e.Current.ControlType.ProgrammaticName)
        }
    }
}
$bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bmp = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
$bmp.Save("C:\MyProjects\APKTechPlan\heartbeat\t9_ui_v2b.png", [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
L "DONE"
$log | Out-File $logPath -Encoding UTF8
