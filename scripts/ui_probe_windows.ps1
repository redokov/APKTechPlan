# Список топ-уровневых окон 1cv8c с заголовками (UIA).
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName UIAutomationClient

$v8c = "C:\Program Files\1cv8\8.5.4.1683\bin\1cv8c.exe"
$a = "/S localhost\dev_erpapk_demo /N `"Администратор (ОрловАВ)`" /P `"`" /DisableStartupDialogs /DisableStartupMessages"
$proc = Start-Process -FilePath $v8c -ArgumentList $a -PassThru
Start-Sleep -Seconds 35

$root = [System.Windows.Automation.AutomationElement]::RootElement
$children = $root.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)
foreach ($c in $children) {
    $pid2 = $c.Current.ProcessId
    if ($pid2 -eq $proc.Id) {
        Write-Output ("WINDOW: [" + $c.Current.Name + "] type=" + $c.Current.ControlType.ProgrammaticName)
    }
}
