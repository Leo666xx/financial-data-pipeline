# Stop all Financial Dashboard services

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Stop Financial Dashboard System" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Finding Flask API processes..." -ForegroundColor Yellow
$apiProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.Path -like "*financial-data-pipeline*" -and $_.CommandLine -like "*api.py*"
}

if ($apiProcesses) {
    foreach ($proc in $apiProcesses) {
        Write-Host "[OK] Stopping API process (PID: $($proc.Id))" -ForegroundColor Green
        Stop-Process -Id $proc.Id -Force
    }
} else {
    Write-Host "  No API process found" -ForegroundColor Gray
}

Write-Host "Finding Dashboard processes..." -ForegroundColor Yellow
$dashProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.Path -like "*financial-data-pipeline*" -and ($_.CommandLine -like "*dashboard*app.py*")
}

if ($dashProcesses) {
    foreach ($proc in $dashProcesses) {
        Write-Host "[OK] Stopping Dashboard process (PID: $($proc.Id))" -ForegroundColor Green
        Stop-Process -Id $proc.Id -Force
    }
} else {
    Write-Host "  No Dashboard process found" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  All services stopped" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Enter to exit..." -ForegroundColor Cyan
Read-Host
