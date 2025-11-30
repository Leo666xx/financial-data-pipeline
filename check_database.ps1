# Database Health Check Script
# Shows database status and recent data

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Database Health Check" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $PSScriptRoot
$dbPath = "data\market.db"
$pythonExe = ".\venv\Scripts\python.exe"

# Check if database exists
if (Test-Path $dbPath) {
    $dbSize = (Get-Item $dbPath).Length
    $lastModified = (Get-Item $dbPath).LastWriteTime
    
    Write-Host "✓ Database Status:" -ForegroundColor Green
    Write-Host "  Path: $dbPath" -ForegroundColor Gray
    Write-Host "  Size: $('{0:N0}' -f $dbSize) bytes ($('{0:N2}' -f ($dbSize/1KB)) KB)" -ForegroundColor Gray
    Write-Host "  Last Modified: $lastModified" -ForegroundColor Gray
    Write-Host ""
    
    # Get data counts
    Write-Host "Data Summary:" -ForegroundColor Yellow
    & $pythonExe check_data.py
    
} else {
    Write-Host "✗ Database not found: $dbPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "To create database with sample data, run:" -ForegroundColor Yellow
    Write-Host "  .\start_all.ps1" -ForegroundColor White
}

Write-Host ""
Write-Host "Press Enter to exit..." -ForegroundColor Cyan
Read-Host
