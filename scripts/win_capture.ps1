param([int]$ProcessId, [string]$Out = "C:\MyProjects\APKTechPlan\heartbeat\win_capture.png")
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class PW {
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr hdc, uint flags);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  public struct RECT { public int Left, Top, Right, Bottom; }
}
"@
$p = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
if ($p -eq $null) { Write-Output "no such process"; exit 1 }
$h = $p.MainWindowHandle
Write-Output ("pid={0} hwnd={1} title='{2}'" -f $p.Id, $h, $p.MainWindowTitle)
if ($h -eq 0) { Write-Output "no main window"; exit 1 }
[PW]::ShowWindow($h, 9) | Out-Null
[PW]::SetForegroundWindow($h) | Out-Null
Start-Sleep -Seconds 2
$r = New-Object PW+RECT
[PW]::GetWindowRect($h, [ref]$r) | Out-Null
$w = $r.Right - $r.Left; $ht = $r.Bottom - $r.Top
Write-Output ("rect {0},{1} {2}x{3}" -f $r.Left, $r.Top, $w, $ht)
if ($w -le 0 -or $ht -le 0) { Write-Output "bad rect"; exit 1 }
$bmp = New-Object System.Drawing.Bitmap($w, $ht)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$hdc = $g.GetHdc()
[PW]::PrintWindow($h, $hdc, 2) | Out-Null
$g.ReleaseHdc($hdc)
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
Write-Output "saved $Out"
