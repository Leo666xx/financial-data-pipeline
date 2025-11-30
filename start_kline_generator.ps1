# Clean and restart K-line data collection
# This script will:
# 1. Clear old/invalid price data
# 2. Start the K-line generator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Clean Start: K-Line Data Collection" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $PSScriptRoot
$pythonExe = ".\venv\Scripts\python.exe"

# Step 1: Clear old data
Write-Host "Step 1/2: Clearing old price data..." -ForegroundColor Yellow
& $pythonExe "src\database.py" "clear"

Write-Host ""
Write-Host "Step 2/2: Starting K-line generator..." -ForegroundColor Yellow
Write-Host ""
Write-Host "The K-line generator will:" -ForegroundColor White
Write-Host "  - Fetch tick prices every 5 seconds" -ForegroundColor Gray
Write-Host "  - Generate 5-minute OHLC candlesticks" -ForegroundColor Gray
Write-Host "  - Filter out invalid prices automatically" -ForegroundColor Gray
Write-Host "  - Save clean data to database" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C to stop." -ForegroundColor Cyan
Write-Host ""

# Start the K-line generator
& $pythonExe "src\kline_generator.py"
