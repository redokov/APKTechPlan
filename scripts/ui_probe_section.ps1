﻿# Открывает раздел «Планирование техники», скриншот панели.
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms

$out = "C:\MyProjects\APKTechPlan\heartbeat\ui_probe1.png"
$v8c = "C:\Program Files\1cv8\8.5.4.1683\bin\1cv8c.exe"
$a = "/S localhost\dev_erpapk_demo /N `"Администратор (ОрловАВ)`" /P `"`" /DisableStartupDialogs /DisableStartupMessages"
$proc = Start-Process -FilePath $v8c -ArgumentList $a -PassThru
$root = [System.Windows.Automation.AutomationElement]::RootElement
$main = $null
$deadline = (Get-Date).AddSeconds(120)
while ((Get-Date) -lt $deadline -and -not $main) {
    Start-Sleep -Seconds 5
    if ($proc.HasExited) { Write-Output "PROCESS EXITED"; exit 4 }
    foreach ($c in $root.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)) {
        if ($c.Current.ProcessId -eq $proc.Id -and $c.Current.ControlType.ProgrammaticName -eq "ControlType.Window") {
            $main = $c; break
        }
    }
}
if (-not $main) { Write-Output "MAIN WINDOW NOT FOUND"; exit 2 }
Write-Output ("main: " + $main.Current.Name)

# ищем элемент с именем, начинающимся на «Планирование техники»
$sec = $null
foreach ($e in $main.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)) {
    if ($e.Current.Name -like "Планирование техники*") {
        Write-Output ("cand: [" + $e.Current.Name + "] " + $e.Current.ControlType.ProgrammaticName)
        if ($e.Current.ControlType.ProgrammaticName -in @("ControlType.TabItem","ControlType.Button","ControlType.MenuItem","ControlType.ListItem")) { $sec = $e; break }
    }
}
if (-not $sec) { Write-Output "SECTION NOT FOUND"; exit 3 }
Write-Output ("click: " + $sec.Current.Name)
try {
    $inv = $sec.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
    $inv.Invoke()
} catch {
    $sel = $sec.GetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern)
    $sel.Select()
}
Start-Sleep -Seconds 8

$bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bmp = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
$bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
Write-Output "SAVED"
