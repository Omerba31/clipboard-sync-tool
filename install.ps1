# Installation script for Clipboard Sync Tool
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Clipboard Sync Tool - Installer" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
if (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host " Python found" -ForegroundColor Green
} else {
    Write-Host " Python not found" -ForegroundColor Red
    exit 1
}

# Check Node.js
Write-Host "Checking Node.js..." -ForegroundColor Yellow
if (Get-Command node -ErrorAction SilentlyContinue) {
    Write-Host " Node.js found" -ForegroundColor Green
    $hasNode = $true
} else {
    Write-Host " Node.js not found (cloud relay will not be available)" -ForegroundColor Yellow
    $hasNode = $false
}

Write-Host ""
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($hasNode) {
    Write-Host ""
    Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
    Push-Location cloud-relay
    npm install
    Pop-Location
}

Write-Host ""
Write-Host " Installation complete!" -ForegroundColor Green
Write-Host "Run: python main.py" -ForegroundColor Cyan
