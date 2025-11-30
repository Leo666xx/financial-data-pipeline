# Auto-Update Script for Financial Dashboard
# Checks for updates from GitHub and restarts services

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Auto-Update Check" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $PSScriptRoot

# Step 1: Check Git status
Write-Host "Step 1/4: Checking for updates..." -ForegroundColor Yellow
$currentBranch = git branch --show-current
Write-Host "Current branch: $currentBranch" -ForegroundColor Gray

# Fetch latest changes
git fetch origin 2>&1 | Out-Null

# Check if there are updates
$localCommit = git rev-parse HEAD
$remoteCommit = git rev-parse origin/$currentBranch

if ($localCommit -eq $remoteCommit) {
    Write-Host "[OK] Already up-to-date" -ForegroundColor Green
    Write-Host ""
    Write-Host "No updates needed. System is running latest version." -ForegroundColor White
    Start-Sleep -Seconds 2
    exit 0
}

Write-Host "[INFO] Updates available!" -ForegroundColor Yellow
Write-Host "  Local:  $($localCommit.Substring(0,7))" -ForegroundColor Gray
Write-Host "  Remote: $($remoteCommit.Substring(0,7))" -ForegroundColor Gray
Write-Host ""

# Step 2: Stop all services
Write-Host "Step 2/4: Stopping running services..." -ForegroundColor Yellow
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object { 
    $_.Path -like "*financial-data-pipeline*" 
}

if ($pythonProcesses) {
    foreach ($proc in $pythonProcesses) {
        Stop-Process -Id $proc.Id -Force
        Write-Host "  Stopped PID: $($proc.Id)" -ForegroundColor Gray
    }
    Write-Host "[OK] All services stopped" -ForegroundColor Green
    Start-Sleep -Seconds 2
} else {
    Write-Host "[INFO] No running services found" -ForegroundColor Gray
}
Write-Host ""

# Step 3: Pull updates
Write-Host "Step 3/4: Pulling latest code..." -ForegroundColor Yellow
try {
    $pullOutput = git pull origin $currentBranch 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Code updated successfully" -ForegroundColor Green
        Write-Host $pullOutput -ForegroundColor Gray
    } else {
        Write-Host "[ERROR] Git pull failed" -ForegroundColor Red
        Write-Host $pullOutput -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[ERROR] Failed to pull updates: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 4: Check for requirements updates
Write-Host "Step 4/4: Checking Python dependencies..." -ForegroundColor Yellow
$pipExe = ".\venv\Scripts\pip.exe"
if (Test-Path "requirements.txt") {
    & $pipExe install -r requirements.txt --quiet --disable-pip-version-check
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Dependencies up-to-date" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Failed to update dependencies" -ForegroundColor Yellow
    }
} else {
    Write-Host "[INFO] No requirements.txt found" -ForegroundColor Gray
}
Write-Host ""

# Step 5: Restart system
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Update Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Restarting system in 3 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Start the system
& "$PSScriptRoot\start_all.ps1"
