<#
Production start script for Windows PowerShell.
Usage: .\scripts\start-prod.ps1 [-NoInstall]
#>
param(
  [switch]$NoInstall
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = (Resolve-Path "$ScriptDir\..").Path
Set-Location $RepoRoot

if (-not $NoInstall) {
  Write-Host "Installing Python dependencies..."
  python -m pip install --upgrade pip
  if (Test-Path requirements.txt) { pip install -r requirements.txt }

  Write-Host "Installing frontend dependencies..."
  npm install
}

Write-Host "Building frontend (Vite)..."
npm run build

Write-Host "Collecting static files"
python manage.py collectstatic --noinput

Write-Host "Applying migrations"
python manage.py migrate --noinput

Write-Host "Starting Gunicorn equivalent (on Windows you may use Waitress or IIS)":
Write-Host "Please configure a WSGI server such as Waitress or use a Linux host with Gunicorn."

# Example: start waitress-serve if installed
if (Get-Command waitress-serve -ErrorAction SilentlyContinue) {
  Write-Host "Starting Waitress (python -m waitress)"
  Start-Process -NoNewWindow -FilePath python -ArgumentList '-m','waitress','-b','0.0.0.0:8000','weather_prediction.wsgi:application'
} else {
  Write-Host "Waitress not found. Install with 'pip install waitress' or run this on a Linux host with Gunicorn."
}
