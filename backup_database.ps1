# Automated Database Backup Script
# Creates timestamped backup in data/backups folder

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Database Backup Tool" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $PSScriptRoot
$dbPath = "data\market.db"
$backupDir = "data\backups"

# Create backup directory if not exists
if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir | Out-Null
    Write-Host "[OK] Created backup directory: $backupDir" -ForegroundColor Green
}

# Check if database exists
if (-not (Test-Path $dbPath)) {
    Write-Host "✗ Database not found: $dbPath" -ForegroundColor Red
    Write-Host "Nothing to backup." -ForegroundColor Gray
    Read-Host "Press Enter to exit"
    exit 1
}

# Create backup
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupPath = "$backupDir\market_$timestamp.db"

try {
    Copy-Item $dbPath $backupPath
    $backupSize = (Get-Item $backupPath).Length
    
    Write-Host "✓ Backup successful!" -ForegroundColor Green
    Write-Host "  Source: $dbPath" -ForegroundColor Gray
    Write-Host "  Backup: $backupPath" -ForegroundColor Gray
    Write-Host "  Size: $('{0:N0}' -f $backupSize) bytes ($('{0:N2}' -f ($backupSize/1KB)) KB)" -ForegroundColor Gray
    Write-Host ""
    
    # List all backups
    Write-Host "All backups:" -ForegroundColor Yellow
    Get-ChildItem "$backupDir\*.db" | Sort-Object LastWriteTime -Descending | ForEach-Object {
        $age = (Get-Date) - $_.LastWriteTime
        $ageStr = if ($age.TotalHours -lt 24) {
            "$([math]::Floor($age.TotalHours)) hours ago"
        } else {
            "$([math]::Floor($age.TotalDays)) days ago"
        }
        Write-Host "  $($_.Name) - $('{0:N0}' -f $_.Length) bytes - $ageStr" -ForegroundColor Gray
    }
    
    # Cleanup old backups (keep last 10)
    $oldBackups = Get-ChildItem "$backupDir\*.db" | Sort-Object LastWriteTime -Descending | Select-Object -Skip 10
    if ($oldBackups.Count -gt 0) {
        Write-Host ""
        Write-Host "Cleaning up old backups (keeping last 10)..." -ForegroundColor Yellow
        $oldBackups | ForEach-Object {
            Remove-Item $_.FullName
            Write-Host "  Removed: $($_.Name)" -ForegroundColor Gray
        }
    }
    
} catch {
    Write-Host "✗ Backup failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press Enter to exit..." -ForegroundColor Cyan
Read-Host
