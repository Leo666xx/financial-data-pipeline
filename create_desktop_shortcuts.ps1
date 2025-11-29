# Create desktop shortcuts for Financial Dashboard
# Usage: .\create_desktop_shortcuts.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Creating Desktop Shortcut..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$desktopPath = [Environment]::GetFolderPath("Desktop")
$projectRoot = $PSScriptRoot
$WshShell = New-Object -ComObject WScript.Shell

# All-in-one startup shortcut
$startAllShortcut = $WshShell.CreateShortcut("$desktopPath\Financial Dashboard.lnk")
$startAllShortcut.TargetPath = "powershell.exe"
$startAllShortcut.Arguments = "-ExecutionPolicy Bypass -File `"$projectRoot\start_all.ps1`""
$startAllShortcut.WorkingDirectory = $projectRoot
$startAllShortcut.Description = "Start K-line Generator + API + Dashboard + Browser"
$startAllShortcut.IconLocation = "powershell.exe,0"
$startAllShortcut.Save()

Write-Host "[OK] Created: Financial Dashboard.lnk" -ForegroundColor Green
Write-Host "  -> Location: $desktopPath" -ForegroundColor Gray
Write-Host "  -> Target: $projectRoot\start_all.ps1" -ForegroundColor Gray
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Shortcut Created Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "What it does:" -ForegroundColor White
Write-Host "  1. Clear old price data" -ForegroundColor Gray
Write-Host "  2. Start K-line generator (live window)" -ForegroundColor Gray
Write-Host "  3. Start Flask API (background)" -ForegroundColor Gray
Write-Host "  4. Start Dashboard (background)" -ForegroundColor Gray
Write-Host "  5. Open browser automatically" -ForegroundColor Gray
Write-Host ""
Write-Host "How to use:" -ForegroundColor White
Write-Host "  -> Double-click 'Financial Dashboard' on desktop" -ForegroundColor Green
Write-Host "  -> Wait 10-15 minutes for K-line data to accumulate" -ForegroundColor Yellow
Write-Host "  -> Use dashboard to view charts and AI analysis" -ForegroundColor Cyan
Write-Host ""
Write-Host "To stop services:" -ForegroundColor White
Write-Host "  -> Run in terminal: .\stop_all.ps1" -ForegroundColor Gray
Write-Host "  -> Or close K-line generator window + run stop_all.ps1" -ForegroundColor Gray
Write-Host ""

$openDesktop = Read-Host "Open desktop folder now? (Y/N)"
if ($openDesktop -eq "Y" -or $openDesktop -eq "y") {
    explorer.exe $desktopPath
}
Write-Host ""