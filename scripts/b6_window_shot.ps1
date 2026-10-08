param([string]$TitleMatch = '', [switch]$Full)
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT r);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
  public struct RECT { public int Left, Top, Right, Bottom; }
}
"@
$procs = Get-Process 1cv8c,1cv8 -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 }
foreach ($p in $procs) {
  Write-Output ("proc {0} hwnd={1} title={2}" -f $p.ProcessName, $p.MainWindowHandle, $p.MainWindowTitle)
}
if ($TitleMatch -ne '') { $t = $procs | Where-Object { $_.MainWindowTitle -like "*$TitleMatch*" } | Select-Object -First 1 } else { $t = $null }
if ($t -ne $null) { $target = $t } else { $target = $procs | Select-Object -First 1 }
if ($target -eq $null) { Write-Output "NO WINDOW"; exit 1 }
[Win32]::ShowWindow($target.MainWindowHandle, 9) | Out-Null  # SW_RESTORE
[Win32]::SetForegroundWindow($target.MainWindowHandle) | Out-Null
Start-Sleep -Seconds 2
$r = New-Object Win32+RECT
if ($Full) {
  Add-Type -AssemblyName System.Windows.Forms
  $b = New-Object System.Drawing.Bitmap([System.Windows.Forms.SystemInformation]::VirtualScreen.Width, [System.Windows.Forms.SystemInformation]::VirtualScreen.Height)
  $g = [System.Drawing.Graphics]::FromImage($b)
  $g.CopyFromScreen(0,0,0,0,$b.Size)
  $out2 = "C:\MyProjects\APKTechPlan\heartbeat/b6_screen_full.png"
  $b.Save($out2, [System.Drawing.Imaging.ImageFormat]::Png)
  Write-Output "saved $out2"
  exit 0
}
[Win32]::GetWindowRect($target.MainWindowHandle, [ref]$r) | Out-Null
$w = $r.Right - $r.Left; $h = $r.Bottom - $r.Top
Write-Output ("rect {0},{1} {2}x{3}" -f $r.Left, $r.Top, $w, $h)
$b = New-Object System.Drawing.Bitmap($w, $h)
$g = [System.Drawing.Graphics]::FromImage($b)
$g.CopyFromScreen($r.Left, $r.Top, 0, 0, $b.Size)
$out = "C:\MyProjects\APKTechPlan\heartbeat\b6_screen2.png"
$b.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
Write-Output "saved $out"
