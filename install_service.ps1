# Install Financial Dashboard as Windows Startup Service
# Auto-starts on boot and keeps running in background

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Install Dashboard Background Service" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$taskName = "FinancialDashboard_Service"
$scriptPath = "$PSScriptRoot\start_all.ps1"
$workingDir = $PSScriptRoot

# Check if task already exists
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "Service already installed. Removing old service..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Create trigger (at system startup)
$trigger = New-ScheduledTaskTrigger -AtStartup

# Create action
$action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$scriptPath`" -ServiceMode" `
    -WorkingDirectory $workingDir

# Create task settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Days 365) `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1)

# Create principal (run with highest privileges)
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType S4U -RunLevel Highest

# Register task
Register-ScheduledTask -TaskName $taskName `
    -Trigger $trigger `
    -Action $action `
    -Settings $settings `
    -Principal $principal `
    -Description "Auto-start Financial Dashboard system on boot. Access at http://localhost:8050" | Out-Null

Write-Host ""
Write-Host "[OK] Background service installed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Service Details:" -ForegroundColor White
Write-Host "  Name:        $taskName" -ForegroundColor Gray
Write-Host "  Start:       On system boot (automatic)" -ForegroundColor Gray
Write-Host "  Access:      http://localhost:8050" -ForegroundColor Gray
Write-Host "  Mode:        Background (hidden windows)" -ForegroundColor Gray
Write-Host ""
Write-Host "What this means:" -ForegroundColor White
Write-Host "  ✓ Dashboard starts automatically when Windows boots" -ForegroundColor Green
Write-Host "  ✓ Just open browser and go to http://localhost:8050" -ForegroundColor Green
Write-Host "  ✓ No need to click desktop shortcut anymore" -ForegroundColor Green
Write-Host "  ✓ Runs silently in background" -ForegroundColor Green
Write-Host "  ✓ Auto-restarts if crashes" -ForegroundColor Green
Write-Host ""
Write-Host "To start the service now (without reboot):" -ForegroundColor White
Write-Host "  Start-ScheduledTask -TaskName '$taskName'" -ForegroundColor Yellow
Write-Host ""
Write-Host "To stop the service:" -ForegroundColor White
Write-Host "  Get-Process python | Where-Object { `$_.Path -like '*financial-data-pipeline*' } | Stop-Process" -ForegroundColor Yellow
Write-Host ""
Write-Host "To uninstall the service:" -ForegroundColor White
Write-Host "  .\uninstall_service.ps1" -ForegroundColor Yellow
Write-Host ""

# Ask if user wants to start now
$response = Read-Host "Do you want to start the service now? (Y/N)"
if ($response -eq 'Y' -or $response -eq 'y') {
    Write-Host ""
    Write-Host "Starting service..." -ForegroundColor Yellow
    Start-ScheduledTask -TaskName $taskName
    Start-Sleep -Seconds 3
    Write-Host "[OK] Service started!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Opening browser in 5 seconds..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    Start-Process "http://localhost:8050"
} else {
    Write-Host ""
    Write-Host "Service will start automatically on next boot." -ForegroundColor Cyan
}

Write-Host ""
Read-Host "Press Enter to exit"
