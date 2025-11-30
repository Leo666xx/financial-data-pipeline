# Scheduled Auto-Update Task
# Runs every 6 hours to check for updates

Write-Host "Setting up scheduled auto-update task..." -ForegroundColor Cyan

$taskName = "FinancialDashboard_AutoUpdate"
$scriptPath = "$PSScriptRoot\auto_update.ps1"

# Check if task already exists
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "Task already exists. Removing old task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Create trigger (every 6 hours)
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 6)

# Create action
$action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$scriptPath`""

# Create task settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable

# Register task
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -RunLevel Highest

Register-ScheduledTask -TaskName $taskName `
    -Trigger $trigger `
    -Action $action `
    -Settings $settings `
    -Principal $principal `
    -Description "Auto-update Financial Dashboard from GitHub every 6 hours" | Out-Null

Write-Host ""
Write-Host "[OK] Scheduled task created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Task Details:" -ForegroundColor White
Write-Host "  Name:        $taskName" -ForegroundColor Gray
Write-Host "  Schedule:    Every 6 hours" -ForegroundColor Gray
Write-Host "  Script:      $scriptPath" -ForegroundColor Gray
Write-Host ""
Write-Host "You can manage this task in:" -ForegroundColor White
Write-Host "  Task Scheduler -> Task Scheduler Library -> $taskName" -ForegroundColor Gray
Write-Host ""
Write-Host "To disable auto-update, run:" -ForegroundColor White
Write-Host "  Disable-ScheduledTask -TaskName '$taskName'" -ForegroundColor Yellow
Write-Host ""
Write-Host "To remove auto-update, run:" -ForegroundColor White
Write-Host "  Unregister-ScheduledTask -TaskName '$taskName' -Confirm:`$false" -ForegroundColor Yellow
Write-Host ""

Read-Host "Press Enter to continue"
