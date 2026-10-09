$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32Cap {
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdc, uint flags);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT r);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint flags, int dx, int dy, int data, UIntPtr extra);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  public struct RECT { public int Left, Top, Right, Bottom; }
  public const uint LEFTDOWN = 0x0002;
  public const uint LEFTUP = 0x0004;
  public const uint WHEEL = 0x0800;
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
function TryFindSection([string]$png, [string]$txt) {
    $ocr = & python C:\MyProjects\APKTechPlan\scripts\ocr_boxes.py $png ru
    $ocr | Out-File $txt -Encoding UTF8
    return (& python C:\MyProjects\APKTechPlan\scripts\t10_find_section.py $txt)
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
Start-Sleep -Seconds 25
[void][Win32Cap]::SetForegroundWindow($hwnd)
Start-Sleep -Milliseconds 500
$ok = CapWin $hwnd "t10_ui4_start.png"
if (-not $ok) { Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue; exit 3 }
$png = "C:\MyProjects\APKTechPlan\heartbeat\t10_ui4_start.png"
$txt = "C:\MyProjects\APKTechPlan\heartbeat\t10_ocr4_start.txt"
$found = TryFindSection $png $txt
$round = 0
while ($found -notmatch "^FOUND" -and $round -lt 6) {
    $round++
    Write-Output ("scroll round $round...")
    [void][Win32Cap]::SetForegroundWindow($hwnd)
    Start-Sleep -Milliseconds 300
    [void][Win32Cap]::SetCursorPos(($script:winL + 100), ($script:winT + 480))
    Start-Sleep -Milliseconds 400
    for ($i = 0; $i -lt 6; $i++) {
        [Win32Cap]::mouse_event([Win32Cap]::WHEEL, 0, 0, -120, [UIntPtr]::Zero)
        Start-Sleep -Milliseconds 120
    }
    Start-Sleep -Seconds 2
    $png = "C:\MyProjects\APKTechPlan\heartbeat\t10_ui4_scroll$round.png"
    $txt = "C:\MyProjects\APKTechPlan\heartbeat\t10_ocr4_scroll$round.txt"
    $ok = CapWin $hwnd ("t10_ui4_scroll{0}.png" -f $round)
    if (-not $ok) { continue }
    $found = TryFindSection $png $txt
}
if ($found -notmatch "^FOUND") {
    Write-Output ("SECTION NOT FOUND after $round scroll rounds")
    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    exit 5
}
$coords = $found.Split(" ")
$bx = [int]$coords[1]; $by = [int]$coords[2]
$cx = $script:winL + $bx
$cy = $script:winT + $by
Write-Output ("section at bitmap $bx,$by -> screen $cx,$cy")
[void][Win32Cap]::SetForegroundWindow($hwnd)
Start-Sleep -Milliseconds 600
[void][Win32Cap]::SetCursorPos($cx, $cy)
Start-Sleep -Milliseconds 400
[Win32Cap]::mouse_event([Win32Cap]::LEFTDOWN, 0, 0, 0, [UIntPtr]::Zero)
[Win32Cap]::mouse_event([Win32Cap]::LEFTUP, 0, 0, 0, [UIntPtr]::Zero)
Write-Output ("CLICK: $cx,$cy")
Start-Sleep -Seconds 4
$okA = CapWin $hwnd "t10_ui4_panel4s.png"
if ($okA) {
    $ocrA = & python C:\MyProjects\APKTechPlan\scripts\ocr_boxes.py C:\MyProjects\APKTechPlan\heartbeat\t10_ui4_panel4s.png ru
    $ocrA | Out-File C:\MyProjects\APKTechPlan\heartbeat\t10_ocr4_panel4s.txt -Encoding UTF8
}
Start-Sleep -Seconds 8
$okB = CapWin $hwnd "t10_ui4_panel12s.png"
if ($okB) {
    $ocrB = & python C:\MyProjects\APKTechPlan\scripts\ocr_boxes.py C:\MyProjects\APKTechPlan\heartbeat\t10_ui4_panel12s.png ru
    $ocrB | Out-File C:\MyProjects\APKTechPlan\heartbeat\t10_ocr4_panel12s.txt -Encoding UTF8
}
Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
Write-Output "DONE"
