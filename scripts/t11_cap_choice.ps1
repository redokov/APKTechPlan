$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32Cap2 {
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdc, uint flags);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT r);
  public struct RECT { public int Left, Top, Right, Bottom; }
}
"@
$procs = Get-Process 1cv8c -ErrorAction SilentlyContinue
if (-not $procs) { Write-Output "NO 1cv8c"; exit 1 }
$i = 0
foreach ($p in $procs) {
  $h = $p.MainWindowHandle
  if ($h -eq [IntPtr]::Zero) { Write-Output ("pid=" + $p.Id + " no hwnd"); continue }
  $r = New-Object Win32Cap2+RECT
  [void][Win32Cap2]::GetWindowRect($h, [ref]$r)
  $w = $r.Right - $r.Left; $ht = $r.Bottom - $r.Top
  if ($w -lt 100 -or $ht -lt 100) { Write-Output ("pid=" + $p.Id + " small ${w}x${ht}"); continue }
  $bmp = New-Object System.Drawing.Bitmap $w, $ht
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $hdc = $g.GetHdc()
  [void][Win32Cap2]::PrintWindow($h, $hdc, 2)
  $g.ReleaseHdc($hdc); $g.Dispose()
  $out = "C:\MyProjects\APKTechPlan\heartbeat\t11_choice_" + $i + ".png"
  $bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
  $bmp.Dispose()
  Write-Output ("CAP pid=" + $p.Id + " -> " + $out + " ${w}x${ht} at " + $r.Left + "," + $r.Top)
  $i++
}
