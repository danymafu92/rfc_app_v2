<#
Start both backend (Django) and frontend (Vite) for local development on Windows PowerShell.
Usage: .\scripts\start-dev.ps1 [-NoInstall] [-Build]
  -NoInstall : skip installing dependencies
  -Build     : build frontend before starting servers
#>
param(
  [switch]$NoInstall,
  [switch]$Build
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = (Resolve-Path "$ScriptDir\..").Path
Set-Location $RepoRoot

# --- Dependency Installation ---
if (-not $NoInstall) {
  Write-Host "Installing Python dependencies..."
  # Use '&' for explicit execution of command in case 'python' isn't fully in PATH
  & python -m pip install --upgrade pip
  if (Test-Path requirements.txt) { & pip install -r requirements.txt }

  Write-Host "Installing frontend dependencies (root package.json)..."
  & npm install
}

# --- Frontend Build ---
if ($Build) {
  Write-Host "Building frontend..."
  & npm run build
}

# --- Server Startup (with fix for npm) ---
$LogDir = Join-Path $RepoRoot ".dev_logs"
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }

# Start Django
Write-Host "Starting Django dev server (http://localhost:8000)"
$DjangoProcess = Start-Process -NoNewWindow -PassThru -FilePath python -ArgumentList 'manage.py','runserver','0.0.0.0:8000' -RedirectStandardOutput "$LogDir\django.log" -RedirectStandardError "$LogDir\django.err.log"

# Start Vite - FIX: Use cmd.exe to reliably run shell commands like 'npm run dev'
# CRITICAL FIX FOR HMR: Changed '/c' to '/k' to keep the command shell open
Write-Host "Starting Vite dev server (http://localhost:5173)"
$ViteProcess = Start-Process -NoNewWindow -PassThru -FilePath cmd.exe -ArgumentList '/k', 'npm run dev' -RedirectStandardOutput "$LogDir\vite.log" -RedirectStandardError "$LogDir\vite.err.log"

# --- Cleanup (Trap for Ctrl-C) ---
# Note: Cleanup is complex in PowerShell with Start-Process, as the parent script terminates,
# but the spawned process (cmd.exe or python) may continue. The best practice is
# to capture the Process objects and explicitly stop them.
$ProcessIdsToKill = @($DjangoProcess.Id, $ViteProcess.Id)

function Cleanup {
    Write-Host "`nStopping servers..."
    foreach ($pid in $ProcessIdsToKill) {
        if (Get-Process -Id $pid -ErrorAction SilentlyContinue) {
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        }
    }
    exit 0
}
# Set up trap for Ctrl-C (stopping the script)
Trap {
    if ($_.Exception.GetType().Name -eq 'TerminateException') {
        # This is the exception thrown when Ctrl-C is pressed
        Cleanup
    }
    # For any other error, re-throw
    else {
        Write-Error $_.Exception.Message
        exit 1
    }
}

# --- Log Tailing (Keeps script alive) ---
Write-Host "Servers started. Logs are in $LogDir. Press Ctrl-C to stop."
Write-Host "Tailing logs (Ctrl-C will stop all servers)..."

# Tail the logs in a separate PowerShell runspace for simultaneous output
$LogJob = Start-Job -ScriptBlock {
    # Use -Wait (equivalent to tail -f) to follow multiple files
    Get-Content -Path $using:LogDir\django.log, $using:LogDir\vite.log -Wait
}

# Wait for the job to complete (which it won't until Ctrl-C or an error)
Wait-Job $LogJob
Receive-Job $LogJob
Remove-Job $LogJob

# Final cleanup just in case
Cleanup