# Flask API Startup Script
# Usage: Run .\start_api.ps1 in PowerShell

Write-Host "Starting Flask API..." -ForegroundColor Green

# Switch to project directory
Set-Location $PSScriptRoot

# Start API using virtual environment Python
& ".\venv\Scripts\python.exe" "src\api.py"
