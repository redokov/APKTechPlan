$ErrorActionPreference = "Stop"
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32Cap {
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdc, uint flags);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT r);
  [DllImport("dwmapi.dll")] public static extern int DwmGetWindowAttribute(IntPtr hwnd, int attr, out RECT pv, int cb);
  public struct RECT { public int Left, Top, Right, Bottom; }
}
"@
function CapWin([IntPtr]$hwnd, [string]$name) {
    $r = New-Object Win32Cap+RECT
    [void][Win32Cap]::GetWindowRect($hwnd, [ref]$r)
    $w = $r.Right - $r.Left; $h = $r.Bottom - $r.Top
    if ($w -lt 50 -or $h -lt 50) { Write-Output ("skip cap: w=$w h=$h"); return }
    $bmp = New-Object System.Drawing.Bitmap $w, $h
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $hdc = $g.GetHdc()
    [void][Win32Cap]::PrintWindow($hwnd, $hdc, 2)
    $g.ReleaseHdc($hdc); $g.Dispose()
    $out = "C:\MyProjects\APKTechPlan\heartbeat\" + $name
    $bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
    $bmp.Dispose()
    Write-Output ("CAP: " + $name + " ${w}x${h}")
}
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
Start-Sleep -Seconds 15   # дать /Execute открыть форму зонда и целевую
CapWin $hwnd "t9_ui_v4_window.png"
Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
Write-Output "DONE"
