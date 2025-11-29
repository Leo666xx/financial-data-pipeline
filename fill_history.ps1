# Fill Historical K-line Data
# Fetches 300 bars of 5-minute K-line data for all symbols

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Fill Historical K-line Data" -ForegroundColor Green
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

Write-Host "This will fill 300 bars of historical K-line data for each symbol" -ForegroundColor White
Write-Host ""
Write-Host "Symbols to fill:" -ForegroundColor Yellow
Write-Host "  - GBPUSD (British Pound / US Dollar)" -ForegroundColor Gray
Write-Host "  - EURUSD (Euro / US Dollar)" -ForegroundColor Gray
Write-Host "  - BTCUSD (Bitcoin / US Dollar)" -ForegroundColor Gray
Write-Host ""

$confirm = Read-Host "Continue? (Y/N)"
if ($confirm -ne "Y" -and $confirm -ne "y") {
    Write-Host "Cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

# Fill GBPUSD
Write-Host ""
Write-Host "[1/3] Filling GBPUSD..." -ForegroundColor Yellow
& $pythonExe "fill_history.py" "--symbol" "GBPUSD" "--bars" "300"

# Fill EURUSD
Write-Host ""
Write-Host "[2/3] Filling EURUSD..." -ForegroundColor Yellow
& $pythonExe "fill_history.py" "--symbol" "EURUSD" "--bars" "300"

# Fill BTCUSD
Write-Host ""
Write-Host "[3/3] Filling BTCUSD..." -ForegroundColor Yellow
& $pythonExe "fill_history.py" "--symbol" "BTCUSD" "--bars" "300"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ✓ All Symbols Filled" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Start the system: .\start_all.ps1" -ForegroundColor Gray
Write-Host "  2. Or double-click 'Financial Dashboard' on desktop" -ForegroundColor Gray
Write-Host "  3. View charts at: http://localhost:8050" -ForegroundColor Cyan
Write-Host ""

Read-Host "Press Enter to exit"
