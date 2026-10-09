$ErrorActionPreference = "Stop"
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr hWnd);
}
"@
$v8c = "C:\Program Files\1cv8\8.5.4.1683\bin\1cv8c.exe"
$epf = "C:\MyProjects\APKTechPlan\build\Тх_ЗондОткрытияФормы.epf"
$a = "ENTERPRISE /S localhost\dev_erpapk_demo /N `"Администратор (ОрловАВ)`" /P `"`" /DisableStartupDialogs /DisableStartupMessages /Execute `"$epf`""
$proc = Start-Process -FilePath $v8c -ArgumentList $a -PassThru
Write-Output ("launched pid=" + $proc.Id)
$root = [System.Windows.Automation.AutomationElement]::RootElement
$deadline = (Get-Date).AddSeconds(150)
$main = $null
while ((Get-Date) -lt $deadline -and -not $main) {
    Start-Sleep -Seconds 5
    if ($proc.HasExited) { Write-Output "PROCESS EXITED"; exit 4 }
    foreach ($c in $root.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)) {
        if ($c.Current.ProcessId -eq $proc.Id -and $c.Current.ControlType.ProgrammaticName -eq "ControlType.Window") { $main = $c; break }
    }
}
if (-not $main) { Write-Output "MAIN WINDOW NOT FOUND"; exit 2 }
Write-Output ("main: " + $main.Current.Name)
$hwnd = [IntPtr]::new($main.Current.NativeWindowHandle)
if ([Win32]::IsIconic($hwnd)) { [void][Win32]::ShowWindow($hwnd, 9) }  # SW_RESTORE
[void][Win32]::ShowWindow($hwnd, 3)  # SW_MAXIMIZE
[void][Win32]::SetForegroundWindow($hwnd)
Start-Sleep -Seconds 12
function Shot([string]$name) {
    $out = "C:\MyProjects\APKTechPlan\heartbeat\" + $name
    $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
    $bmp = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
    $bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose(); $bmp.Dispose()
    Write-Output ("SHOT: " + $name)
}
Shot "t9_ui_v3_foreground.png"
Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
Write-Output "DONE"
