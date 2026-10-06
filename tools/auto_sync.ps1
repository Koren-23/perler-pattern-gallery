# Pull the latest gallery from GitHub (including phone uploads) so the PC copy stays current.
# Run by the "PerlerGallerySync" scheduled task. Only fast-forwards: if the PC has diverged,
# it does nothing and logs the reason. Log: %LOCALAPPDATA%\perler-gallery-sync.log
$repo = Split-Path -Parent $PSScriptRoot
$log = Join-Path $env:LOCALAPPDATA 'perler-gallery-sync.log'
$git = 'C:\Program Files\Git\cmd\git.exe'

$out = & $git -C $repo pull --ff-only 2>&1 | Out-String
$line = '{0}  exit={1}  {2}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm'), $LASTEXITCODE, ($out.Trim() -replace '\s+', ' ')
Add-Content -Path $log -Value $line -Encoding UTF8

# Keep only the last 200 entries
$lines = @(Get-Content $log -Encoding UTF8)
if ($lines.Count -gt 200) { $lines[-200..-1] | Set-Content $log -Encoding UTF8 }
