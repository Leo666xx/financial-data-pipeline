# Financial Dashboard Startup Script
# Usage: Run .\start_dashboard.ps1 in PowerShell

Write-Host "Starting Financial Dashboard..." -ForegroundColor Green

# Switch to project directory
Set-Location $PSScriptRoot

# Start Dashboard using virtual environment Python
& ".\venv\Scripts\python.exe" "dashboard\app.py"
