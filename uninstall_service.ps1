# Uninstall Financial Dashboard Background Service

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Uninstall Dashboard Service" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$taskName = "FinancialDashboard_Service"

# Check if task exists
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if (-not $existingTask) {
    Write-Host "[INFO] Service not found - nothing to uninstall" -ForegroundColor Gray
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 0
}

# Stop running services
Write-Host "Stopping running services..." -ForegroundColor Yellow
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object { 
    $_.Path -like "*financial-data-pipeline*" 
}

if ($pythonProcesses) {
    foreach ($proc in $pythonProcesses) {
        Stop-Process -Id $proc.Id -Force
        Write-Host "  Stopped PID: $($proc.Id)" -ForegroundColor Gray
    }
    Write-Host "[OK] Services stopped" -ForegroundColor Green
} else {
    Write-Host "[INFO] No running services found" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Removing scheduled task..." -ForegroundColor Yellow
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
Write-Host "[OK] Service uninstalled" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Uninstall Complete" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "The dashboard will no longer start automatically." -ForegroundColor White
Write-Host "You can use the desktop shortcut to start it manually." -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit"
