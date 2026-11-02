# Closer Studio installer for Windows 10 and 11. Safe to run again any time.
# Run in PowerShell from this folder:   powershell -ExecutionPolicy Bypass -File .\install.ps1 [-Scenes]
#  - ffmpeg, Python 3.12 and Node.js through winget (the Windows package manager)
#  - the engine's Python packages in their own venv at %USERPROFILE%\.closer-studio\venv
#  - the caption and display fonts (for your user, no admin needed)
#  - every skill copied where Claude Code loads it from (%USERPROFILE%\.claude\skills)
#  - optional: -Scenes installs Playwright's Chromium for the animated VSL scenes (about 150 MB)
# Written to mirror install.sh; not yet run on a Windows machine, so report anything that fails.
param([switch]$Scenes)
$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
function Say($m) { Write-Host "`n$m" -ForegroundColor White }
function Ok($m) { Write-Host "  ok  $m" }
function Have($c) { return [bool](Get-Command $c -ErrorAction SilentlyContinue) }

Say "Closer Studio: setting up"

# 1. tools
if (-not (Have winget)) { Write-Host "winget is missing: install 'App Installer' from the Microsoft Store, then run this again."; exit 1 }
if (-not (Have ffmpeg)) { Say "Installing ffmpeg"; winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements }
if (-not (Have python)) { Say "Installing Python 3.12"; winget install --id Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements }
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
if (-not (Have ffmpeg)) { Write-Host "ffmpeg was installed but this window cannot see it yet: open a new PowerShell and run this again."; exit 1 }
Ok "ffmpeg"

$Venv = Join-Path $HOME ".closer-studio\venv"
if (-not (Test-Path (Join-Path $Venv "Scripts\python.exe"))) { python -m venv $Venv }
$Py = Join-Path $Venv "Scripts\python.exe"
& $Py -m pip install -q --upgrade pip
& $Py -m pip install -q numpy scipy pillow faster-whisper opencv-python-headless scenedetect librosa soundfile
Ok "python packages"

# 2. fonts, for this user only (no admin)
$FontDir = Join-Path $env:LOCALAPPDATA "Microsoft\Windows\Fonts"
New-Item -ItemType Directory -Force -Path $FontDir | Out-Null
$Reg = "HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts"
Get-ChildItem (Join-Path $Here "fonts\*.ttf") | ForEach-Object {
  Copy-Item $_.FullName -Destination $FontDir -Force
  New-ItemProperty -Path $Reg -Name "$($_.BaseName) (TrueType)" -Value (Join-Path $FontDir $_.Name) -PropertyType String -Force | Out-Null
}
Ok "fonts"

# 3. skills into Claude Code
$Dest = if ($env:CLAUDE_SKILLS_DIR) { $env:CLAUDE_SKILLS_DIR } else { Join-Path $HOME ".claude\skills" }
New-Item -ItemType Directory -Force -Path $Dest | Out-Null
$count = 0
Get-ChildItem (Join-Path $Here "skills") -Directory | ForEach-Object { Get-ChildItem $_.FullName -Directory } | ForEach-Object {
  if (Test-Path (Join-Path $_.FullName "SKILL.md")) {
    $t = Join-Path $Dest $_.Name
    if (Test-Path $t) { Remove-Item $t -Recurse -Force }
    Copy-Item $_.FullName -Destination $t -Recurse
    $count++
  }
}
Ok "$count skills installed into $Dest"

# 4. a pointer so the skills can find the tools from any folder
New-Item -ItemType Directory -Force -Path (Join-Path $HOME ".closer-studio") | Out-Null
Set-Content -Path (Join-Path $HOME ".closer-studio\kit_path") -Value $Here -NoNewline
New-Item -ItemType Directory -Force -Path (Join-Path $Here "inbox"), (Join-Path $Here "output") | Out-Null
Ok "kit path recorded"

# 5. optional: Node.js + Playwright Chromium for the animated scenes
if ($Scenes) {
  if (-not (Have node)) { Say "Installing Node.js"; winget install --id OpenJS.NodeJS.LTS -e --accept-source-agreements --accept-package-agreements
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User") }
  Ok "node $(node --version)"
  Say "Installing Playwright and its Chromium (about 150 MB, first time only)"
  Push-Location (Join-Path $Here "tools\vsl\mg"); npm install --silent --no-audit --no-fund; npx --yes playwright@1.63.0 install chromium; Pop-Location
  Ok "animated scenes ready"
}

Say "Done. Open this folder in Claude Code and say what you want."
if (-not (Have claude)) { Write-Host "Claude Code itself is not installed yet: get it at https://claude.ai/code, then run this again." }
