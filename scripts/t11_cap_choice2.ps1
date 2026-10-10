$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
using System.Collections.Generic;
public class Win32Enum {
  public delegate bool EnumProc(IntPtr hWnd, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr lp);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern int GetWindowTextW(IntPtr hWnd, StringBuilder sb, int max);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdc, uint flags);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT r);
  public struct RECT { public int Left, Top, Right, Bottom; }
  public static List<IntPtr> Found = new List<IntPtr>();
  public static uint TargetPid;
  public static bool Cb(IntPtr h, IntPtr lp) {
    uint pid; GetWindowThreadProcessId(h, out pid);
    if (pid == TargetPid && IsWindowVisible(h)) { Found.Add(h); }
    return true;
  }
  public static void Run(uint p) { TargetPid = p; Found.Clear(); EnumWindows(Cb, IntPtr.Zero); }
}
"@
$procs = Get-Process 1cv8c -ErrorAction SilentlyContinue
if (-not $procs) { Write-Output "NO 1cv8c"; exit 1 }
$i = 0
foreach ($p in $procs) {
  [Win32Enum]::Run([uint32]$p.Id)
  Write-Output ("pid=" + $p.Id + " windows=" + [Win32Enum]::Found.Count)
  foreach ($h in [Win32Enum]::Found) {
    $r = New-Object Win32Enum+RECT
    [void][Win32Enum]::GetWindowRect($h, [ref]$r)
    $w = $r.Right - $r.Left; $ht = $r.Bottom - $r.Top
    $sb = New-Object System.Text.StringBuilder 256
    [void][Win32Enum]::GetWindowTextW($h, $sb, 256)
    if ($w -lt 100 -or $ht -lt 100) { Write-Output ("  skip " + $sb.ToString() + " ${w}x${ht}"); continue }
    $bmp = New-Object System.Drawing.Bitmap $w, $ht
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $hdc = $g.GetHdc()
    [void][Win32Enum]::PrintWindow($h, $hdc, 2)
    $g.ReleaseHdc($hdc); $g.Dispose()
    $out = "C:\MyProjects\APKTechPlan\heartbeat\t11_choice4_" + $p.Id + "_" + (Get-Date -Format 'HHmmssfff') + ".png"
    $bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
    $bmp.Dispose()
    Write-Output ("  CAP [" + $sb.ToString() + "] -> " + $out + " ${w}x${ht}")
    $i++
  }
}
