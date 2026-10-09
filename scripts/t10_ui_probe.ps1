$ErrorActionPreference = "Stop"
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32Cap {
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdc, uint flags);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT r);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint flags, int dx, int dy, uint data, UIntPtr extra);
  public struct RECT { public int Left, Top, Right, Bottom; }
  public const uint LEFTDOWN = 0x0002;
  public const uint LEFTUP = 0x0004;
}
"@
function CapWin([IntPtr]$hwnd, [string]$name) {
    $r = New-Object Win32Cap+RECT
    [void][Win32Cap]::GetWindowRect($hwnd, [ref]$r)
    $script:winL = $r.Left; $script:winT = $r.Top
    $w = $r.Right - $r.Left; $h = $r.Bottom - $r.Top
    if ($w -lt 50 -or $h -lt 50) { Write-Output ("skip cap: w=$w h=$h"); return $false }
    $bmp = New-Object System.Drawing.Bitmap $w, $h
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $hdc = $g.GetHdc()
    [void][Win32Cap]::PrintWindow($hwnd, $hdc, 2)
    $g.ReleaseHdc($hdc); $g.Dispose()
    $out = "C:\MyProjects\APKTechPlan\heartbeat\" + $name
    $bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
    $bmp.Dispose()
    Write-Output ("CAP: " + $name + " ${w}x${h} at ${r.Left},${r.Top}")
    return $true
}
function ClickAt([int]$x, [int]$y) {
    [void][Win32Cap]::SetCursorPos($x, $y)
    Start-Sleep -Milliseconds 300
    [Win32Cap]::mouse_event([Win32Cap]::LEFTDOWN, 0, 0, 0, [UIntPtr]::Zero)
    [Win32Cap]::mouse_event([Win32Cap]::LEFTUP, 0, 0, 0, [UIntPtr]::Zero)
    Write-Output ("CLICK: $x,$y")
}
$v8c = "C:\Program Files\1cv8\8.5.4.1683\bin\1cv8c.exe"
$a = "ENTERPRISE /S localhost\dev_erpapk_demo /N `"Администратор (ОрловАВ)`" /P `"`" /DisableStartupDialogs /DisableStartupMessages"
$proc = Start-Process -FilePath $v8c -ArgumentList $a -PassThru
Write-Output ("launched pid=" + $proc.Id)
$root = [System.Windows.Automation.AutomationElement]::RootElement
$deadline = (Get-Date).AddSeconds(180)
$main = $null
while ((Get-Date) -lt $deadline -and -not $main) {
    Start-Sleep -Seconds 5
    if ($proc.HasExited) { Write-Output "PROCESS EXITED"; exit 4 }
    foreach ($c in $root.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)) {
        if ($c.Current.ProcessId -eq $proc.Id -and $c.Current.ControlType.ProgrammaticName -eq "ControlType.Window") { $main = $c; break }
    }
}
if (-not $main) { Write-Output "MAIN WINDOW NOT FOUND"; Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue; exit 2 }
Write-Output ("main: " + $main.Current.Name)
$hwnd = [IntPtr]::new($main.Current.NativeWindowHandle)
Start-Sleep -Seconds 25   # дать базе прогрузиться
$ok = CapWin $hwnd "t10_ui_start.png"
if (-not $ok) { Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue; exit 3 }
# OCR стартового окна: ищем слово Планирование (раздел «Планирование техники»)
$ocr = & python C:\MyProjects\APKTechPlan\scripts\ocr_boxes.py C:\MyProjects\APKTechPlan\heartbeat\t10_ui_start.png ru
$ocr | Out-File C:\MyProjects\APKTechPlan\heartbeat\t10_ocr_start.txt -Encoding UTF8
$sec = $ocr | Where-Object { $_ -match "^Планирование\|" } | Select-Object -First 1
if (-not $sec) {
    Write-Output "SECTION WORD NOT FOUND IN OCR"
    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    exit 5
}
$parts = $sec.Split("|")
$sx = [int]$parts[1]; $sy = [int]$parts[2]; $sw = [int]$parts[3]; $sh = [int]$parts[4]
$cx = $script:winL + $sx + [int]($sw/2)
$cy = $script:winT + $sy + [int]($sh/2)
Write-Output ("section word at bitmap $sx,$sy ${sw}x$sh -> screen $cx,$cy")
ClickAt $cx $cy
Start-Sleep -Seconds 8   # дать разделу открыться
$ok2 = CapWin $hwnd "t10_ui_section.png"
if ($ok2) {
    $ocr2 = & python C:\MyProjects\APKTechPlan\scripts\ocr_boxes.py C:\MyProjects\APKTechPlan\heartbeat\t10_ui_section.png ru
    $ocr2 | Out-File C:\MyProjects\APKTechPlan\heartbeat\t10_ocr_section.txt -Encoding UTF8
}
Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
Write-Output "DONE"
