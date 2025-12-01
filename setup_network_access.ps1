# Network Access Configuration Script
# Configures Windows Firewall to allow external access to Dashboard

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Configure Network Access" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get local IP address
$localIP = Get-NetIPAddress -AddressFamily IPv4 | 
    Where-Object { $_.IPAddress -like "192.168.*" -or $_.IPAddress -like "10.*" } | 
    Select-Object -First 1 -ExpandProperty IPAddress

if (-not $localIP) {
    Write-Host "[ERROR] Could not detect local IP address" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Detected IP Address: $localIP" -ForegroundColor Green
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[ERROR] This script requires Administrator privileges" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run PowerShell as Administrator and try again:" -ForegroundColor Yellow
    Write-Host "  1. Right-click PowerShell" -ForegroundColor White
    Write-Host "  2. Select 'Run as administrator'" -ForegroundColor White
    Write-Host "  3. Navigate to: $PSScriptRoot" -ForegroundColor White
    Write-Host "  4. Run: .\setup_network_access.ps1" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Step 1/3: Configuring Windows Firewall..." -ForegroundColor Yellow

# Remove existing rules if any
$existingRules = @(
    "Financial Dashboard - Port 8050",
    "Financial Dashboard API - Port 5000"
)

foreach ($ruleName in $existingRules) {
    $rule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
    if ($rule) {
        Remove-NetFirewallRule -DisplayName $ruleName
        Write-Host "  Removed old rule: $ruleName" -ForegroundColor Gray
    }
}

# Create firewall rules for Dashboard (port 8050)
New-NetFirewallRule -DisplayName "Financial Dashboard - Port 8050" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 8050 `
    -Action Allow `
    -Profile Domain,Private `
    -Description "Allow access to Financial Dashboard web interface" | Out-Null

Write-Host "[OK] Dashboard port 8050 opened" -ForegroundColor Green

# Create firewall rules for API (port 5000)
New-NetFirewallRule -DisplayName "Financial Dashboard API - Port 5000" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 5000 `
    -Action Allow `
    -Profile Domain,Private `
    -Description "Allow access to Financial Dashboard API" | Out-Null

Write-Host "[OK] API port 5000 opened" -ForegroundColor Green
Write-Host ""

Write-Host "Step 2/3: Testing local access..." -ForegroundColor Yellow
Start-Sleep -Seconds 1

# Check if services are running
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue | 
    Where-Object { $_.Path -like "*financial-data-pipeline*" }

if ($pythonProcesses) {
    Write-Host "[OK] Dashboard services are running" -ForegroundColor Green
} else {
    Write-Host "[WARN] Dashboard services not running" -ForegroundColor Yellow
    Write-Host "       Start services first: .\start_all.ps1" -ForegroundColor Gray
}
Write-Host ""

Write-Host "Step 3/3: Configuration complete!" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Access Information" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Local Access (this computer):" -ForegroundColor White
Write-Host "  http://localhost:8050" -ForegroundColor Cyan
Write-Host ""
Write-Host "Network Access (other devices on same network):" -ForegroundColor White
Write-Host "  http://$localIP:8050" -ForegroundColor Cyan
Write-Host ""
Write-Host "Share this URL with others:" -ForegroundColor Yellow
Write-Host "  http://$localIP:8050" -ForegroundColor Green
Write-Host ""
Write-Host "Requirements for network access:" -ForegroundColor White
Write-Host "  ✓ Dashboard services must be running" -ForegroundColor Gray
Write-Host "  ✓ Other devices must be on same network (WiFi/LAN)" -ForegroundColor Gray
Write-Host "  ✓ Windows Firewall rules configured (done)" -ForegroundColor Gray
Write-Host ""
Write-Host "Features:" -ForegroundColor White
Write-Host "  ✓ Auto-refreshes every 5 seconds" -ForegroundColor Green
Write-Host "  ✓ Real-time data updates" -ForegroundColor Green
Write-Host "  ✓ No manual refresh needed" -ForegroundColor Green
Write-Host "  ✓ Multiple users can view simultaneously" -ForegroundColor Green
Write-Host ""
Write-Host "To start services automatically on boot:" -ForegroundColor White
Write-Host "  .\install_service.ps1" -ForegroundColor Yellow
Write-Host ""

# Copy URL to clipboard
$url = "http://$localIP:8050"
Set-Clipboard -Value $url
Write-Host "[INFO] Network URL copied to clipboard!" -ForegroundColor Cyan
Write-Host ""

Read-Host "Press Enter to exit"
