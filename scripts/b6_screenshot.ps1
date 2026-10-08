param()
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$b = New-Object System.Drawing.Bitmap([System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width, [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height)
$g = [System.Drawing.Graphics]::FromImage($b)
$g.CopyFromScreen(0,0,0,0,$b.Size)
$out = "C:\MyProjects\APKTechPlan\heartbeat\b6_screen1.png"
$b.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
Write-Output "saved $out"
