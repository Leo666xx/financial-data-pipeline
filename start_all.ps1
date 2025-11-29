# All-in-One Startup Script for Financial Dashboard System
# Auto-start: K-line Generator -> API -> Dashboard -> Browser

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Financial Dashboard - Complete System" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $PSScriptRoot
$pythonExe = ".\venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    Write-Host "ERROR: Python virtual environment not found" -ForegroundColor Red
    Write-Host "Please run: python -m venv venv" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 1: Clear old data
Write-Host "Step 1/5: Clearing old price data..." -ForegroundColor Yellow
& $pythonExe "src\database.py" "clear"
Write-Host ""

# Step 2: Start K-line generator (background)
Write-Host "Step 2/5: Starting K-line generator (normal window)..." -ForegroundColor Yellow
$klineProcess = Start-Process -FilePath $pythonExe `
    -ArgumentList "src\kline_generator.py" `
    -WorkingDirectory $PSScriptRoot `
    -WindowStyle Normal `
    -PassThru

Write-Host "[OK] K-line generator started (PID: $($klineProcess.Id))" -ForegroundColor Green
Write-Host "  -> Collecting ticks every 5 seconds" -ForegroundColor Gray
Write-Host "  -> Generating 5-minute K-lines" -ForegroundColor Gray
Write-Host ""

Start-Sleep -Seconds 2

# Step 3: Start Flask API (background)
Write-Host "Step 3/5: Starting Flask API (background)..." -ForegroundColor Yellow
$apiProcess = Start-Process -FilePath $pythonExe `
    -ArgumentList "src\api.py" `
    -WorkingDirectory $PSScriptRoot `
    -WindowStyle Minimized `
    -PassThru

Write-Host "[OK] API started (PID: $($apiProcess.Id))" -ForegroundColor Green
Write-Host "  -> Port: 5000" -ForegroundColor Gray
Write-Host ""

Write-Host "Waiting for API to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/" -TimeoutSec 2 -UseBasicParsing
    Write-Host "[OK] API health check passed" -ForegroundColor Green
} catch {
    Write-Host "[WARN] API is still starting (this is normal)" -ForegroundColor Yellow
}

Write-Host ""

# Step 4: Start Dashboard (background)
Write-Host "Step 4/5: Starting Dashboard (background)..." -ForegroundColor Yellow
$dashProcess = Start-Process -FilePath $pythonExe `
    -ArgumentList "dashboard\app.py" `
    -WorkingDirectory $PSScriptRoot `
    -WindowStyle Minimized `
    -PassThru

Write-Host "[OK] Dashboard started (PID: $($dashProcess.Id))" -ForegroundColor Green
Write-Host "  -> Port: 8050" -ForegroundColor Gray
Write-Host ""

Write-Host "Waiting for Dashboard to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Step 5: Open browser
Write-Host ""
Write-Host "Step 5/5: Opening browser..." -ForegroundColor Yellow
Start-Process "http://localhost:8050"
Write-Host "[OK] Browser opened" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  All Systems Running!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Service Information:" -ForegroundColor White
Write-Host "  K-line Generator:   PID $($klineProcess.Id) (normal window, live data)" -ForegroundColor Gray
Write-Host "  Flask API:          http://127.0.0.1:5000 (PID: $($apiProcess.Id), minimized)" -ForegroundColor Gray
Write-Host "  Dashboard:          http://localhost:8050 (PID: $($dashProcess.Id), minimized)" -ForegroundColor Gray
Write-Host ""
Write-Host "Data Flow:" -ForegroundColor White
Write-Host "  Tick (5s) -> K-line (5min) -> Database -> Dashboard" -ForegroundColor Gray
Write-Host ""
Write-Host "IMPORTANT:" -ForegroundColor Yellow
Write-Host "  - K-line generator window shows live tick data" -ForegroundColor White
Write-Host "  - API and Dashboard run in background (minimized)" -ForegroundColor White
Write-Host "  - To stop all services, run: .\stop_all.ps1" -ForegroundColor White
Write-Host "  - Or close K-line window and run stop_all.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Press Enter to close this window..." -ForegroundColor Cyan
Read-Host
