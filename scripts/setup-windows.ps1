# Windows setup (PowerShell). Run from the repo root:
#   powershell -ExecutionPolicy Bypass -File scripts\setup-windows.ps1
# Safe to re-run. If it installs new programs, it asks you to reopen PowerShell
# (so PATH refreshes) and run it again.
$ErrorActionPreference = "Stop"

if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host "winget not found. Install 'App Installer' from the Microsoft Store, then re-run." -ForegroundColor Red
    exit 1
}

# command to check -> winget package id
$tools = [ordered]@{
    git    = "Git.Git"
    python = "Python.Python.3.12"
    node   = "OpenJS.NodeJS.LTS"
    ffmpeg = "Gyan.FFmpeg"
    magick = "ImageMagick.ImageMagick"
}
$installed = $false
foreach ($cmd in $tools.Keys) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Write-Host "Installing $($tools[$cmd]) ..." -ForegroundColor Cyan
        winget install --id $tools[$cmd] -e --accept-package-agreements --accept-source-agreements
        $installed = $true
    }
}
# Optional GUI apps (not needed for the studio CLI); failures are non-fatal.
foreach ($id in "BlenderFoundation.Blender", "Synfig.SynfigStudio") {
    winget list --id $id -e 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) { winget install --id $id -e --accept-package-agreements --accept-source-agreements }
}
if ($installed) {
    Write-Host "`nNew programs were installed. CLOSE this window, open a new PowerShell, and run this script again." -ForegroundColor Yellow
    exit 0
}

# Python venv (no activation needed; we call the venv's python directly)
if (-not (Test-Path .venv)) { python -m venv .venv }
$py = ".\.venv\Scripts\python.exe"
& $py -m pip install --upgrade pip
& $py -m pip install -e . -r requirements.txt

# Node / browser tooling
npm install
npm run setup:browsers

if (-not (Test-Path .env)) { Copy-Item .env.example .env }
Write-Host "`nCore setup done. Test it:  .\.venv\Scripts\python.exe -m unittest discover tests" -ForegroundColor Green
Write-Host "Optional GPU extras:  .\.venv\Scripts\python.exe -m pip install -r requirements-ml.txt"
Write-Host "Then edit .env and add your API keys."
