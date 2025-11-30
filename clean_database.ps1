# Clean Database Script
# Removes invalid/anomaly price data

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Database Cleanup Tool" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $PSScriptRoot
$pythonExe = ".\venv\Scripts\python.exe"

Write-Host "Choose an option:" -ForegroundColor White
Write-Host "  1. Clear ALL price data (⚠️  DESTRUCTIVE - fresh start)" -ForegroundColor Red
Write-Host "  2. Remove only INVALID prices (safe - keep valid data)" -ForegroundColor Yellow
Write-Host "  3. Backup database before cleaning" -ForegroundColor Green
Write-Host "  4. Cancel" -ForegroundColor Gray
Write-Host ""

$choice = Read-Host "Enter choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "⚠️  WARNING: This will DELETE ALL historical data!" -ForegroundColor Red
        $confirm = Read-Host "Type 'DELETE' to confirm (case-sensitive)"
        if ($confirm -eq "DELETE") {
            Write-Host "Clearing all data..." -ForegroundColor Red
            & $pythonExe "src\database.py" "clear"
        } else {
            Write-Host "Cancelled (incorrect confirmation)." -ForegroundColor Gray
        }
    }
    "2" {
        Write-Host "Removing invalid prices..." -ForegroundColor Yellow
        & $pythonExe "src\database.py" "clean"
    }
    "3" {
        Write-Host "Creating backup..." -ForegroundColor Green
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $backupPath = "data\market_backup_$timestamp.db"
        Copy-Item "data\market.db" $backupPath
        Write-Host "[OK] Backup created: $backupPath" -ForegroundColor Green
    }
    "4" {
        Write-Host "Cancelled." -ForegroundColor Gray
    }
    default {
        Write-Host "Invalid choice." -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Press Enter to exit..." -ForegroundColor Cyan
Read-Host
