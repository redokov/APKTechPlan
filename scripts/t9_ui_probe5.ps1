$ErrorActionPreference = "Stop"
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32Cap {
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdc, uint flags);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT r);
  public struct RECT { public int Left, Top, Right, Bottom; }
}
"@
$logPath = "C:\MyProjects\APKTechPlan\heartbeat\t9_ui_probe5.txt"
$log = New-Object System.Collections.Generic.List[string]
function L([string]$m) { $script:log.Add($m); Write-Output $m }
$v8c = "C:\Program Files\1cv8\8.5.4.1683\bin\1cv8c.exe"
$epf = "C:\MyProjects\APKTechPlan\build\Тх_ЗондОткрытияФормы.epf"
$a = "ENTERPRISE /S localhost\dev_erpapk_demo /N `"Администратор (ОрловАВ)`" /P `"`" /DisableStartupDialogs /DisableStartupMessages /Execute `"$epf`""
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
Start-Sleep -Seconds 20
$i = 0
foreach ($c in $root.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)) {
    if ($c.Current.ProcessId -eq $proc.Id) {
        $i++
        $nm = $c.Current.Name
        L ("WIN${i}: [" + $nm + "] " + $c.Current.ControlType.ProgrammaticName)
        $hwnd = [IntPtr]::new($c.Current.NativeWindowHandle)
        $r = New-Object Win32Cap+RECT
        [void][Win32Cap]::GetWindowRect($hwnd, [ref]$r)
        $w = $r.Right - $r.Left; $h = $r.Bottom - $r.Top
        L ("  rect: ${w}x${h}")
        if ($w -ge 50 -and $h -ge 50) {
            $bmp = New-Object System.Drawing.Bitmap $w, $h
            $g = [System.Drawing.Graphics]::FromImage($bmp)
            $hdc = $g.GetHdc()
            [void][Win32Cap]::PrintWindow($hwnd, $hdc, 2)
            $g.ReleaseHdc($hdc); $g.Dispose()
            $out = ("C:\MyProjects\APKTechPlan\heartbeat\t9_ui_v5_win{0}.png" -f $i)
            $bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
            $bmp.Dispose()
            L ("  CAP: " + $out)
        }
    }
}
Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
L "DONE"
$log | Out-File $logPath -Encoding UTF8
