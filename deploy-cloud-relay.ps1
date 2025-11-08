# Deploy Cloud Relay to Fly.io
# This script helps deploy the cloud relay server for mobile sync

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Cloud Relay Deployment Helper" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if Fly CLI is installed
Write-Host "Checking Fly CLI..." -ForegroundColor Yellow
if (Get-Command fly -ErrorAction SilentlyContinue) {
    $flyVersion = fly version 2>&1
    Write-Host "✅ Fly CLI found: $flyVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Fly CLI not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Would you like to install Fly CLI now? (requires admin)" -ForegroundColor Yellow
    $response = Read-Host "Install Fly CLI? (y/n)"
    
    if ($response -eq 'y' -or $response -eq 'Y') {
        Write-Host "Installing Fly CLI..." -ForegroundColor Cyan
        try {
            iwr https://fly.io/install.ps1 -useb | iex
            Write-Host "✅ Fly CLI installed!" -ForegroundColor Green
            Write-Host "⚠️  Please restart PowerShell and run this script again" -ForegroundColor Yellow
            exit 0
        } catch {
            Write-Host "❌ Failed to install Fly CLI" -ForegroundColor Red
            Write-Host "Please install manually: https://fly.io/docs/hands-on/install-flyctl/" -ForegroundColor Gray
            exit 1
        }
    } else {
        Write-Host "Please install Fly CLI manually: https://fly.io/docs/hands-on/install-flyctl/" -ForegroundColor Gray
        exit 1
    }
}

# Check if user is logged in
Write-Host ""
Write-Host "Checking Fly.io authentication..." -ForegroundColor Yellow
$authCheck = fly auth whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Not logged in to Fly.io" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Opening browser for login..." -ForegroundColor Cyan
    fly auth login
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Login failed" -ForegroundColor Red
        exit 1
    }
}
Write-Host "✅ Authenticated" -ForegroundColor Green

# Navigate to cloud-relay directory
Write-Host ""
Write-Host "Navigating to cloud-relay directory..." -ForegroundColor Yellow
if (-not (Test-Path "cloud-relay")) {
    Write-Host "❌ cloud-relay directory not found!" -ForegroundColor Red
    Write-Host "Please run this script from the project root directory" -ForegroundColor Gray
    exit 1
}
Push-Location cloud-relay

# Check if already deployed
Write-Host ""
Write-Host "Checking for existing deployment..." -ForegroundColor Yellow
$flyToml = Get-Content "fly.toml" -ErrorAction SilentlyContinue
if ($flyToml -match 'app\s*=\s*"([^"]+)"') {
    $appName = $matches[1]
    Write-Host "Found existing app config: $appName" -ForegroundColor Cyan
    
    $flyApps = fly apps list 2>&1
    if ($flyApps -match $appName) {
        Write-Host "✅ App already exists" -ForegroundColor Green
        Write-Host ""
        Write-Host "Deploying update..." -ForegroundColor Cyan
        fly deploy
    } else {
        Write-Host "⚠️  App not found in your account" -ForegroundColor Yellow
        Write-Host "Creating new deployment..." -ForegroundColor Cyan
        fly launch
    }
} else {
    Write-Host "No existing deployment found" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Starting new deployment..." -ForegroundColor Cyan
    Write-Host "You'll be asked to choose:" -ForegroundColor Gray
    Write-Host "  - App name (default is fine)" -ForegroundColor Gray
    Write-Host "  - Region (choose closest to you)" -ForegroundColor Gray
    Write-Host "  - Database: Select NO" -ForegroundColor Gray
    Write-Host ""
    fly launch
}

Pop-Location

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host "✅ Deployment Complete!" -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Your cloud relay is now live!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Get your app URL: fly apps list" -ForegroundColor White
    Write-Host "  2. Open URL on your mobile device" -ForegroundColor White
    Write-Host "  3. Enter a Room ID and start syncing!" -ForegroundColor White
    Write-Host ""
    Write-Host "Monitor your app:" -ForegroundColor Yellow
    Write-Host "  - Status: fly status" -ForegroundColor White
    Write-Host "  - Logs: fly logs" -ForegroundColor White
    Write-Host "  - Dashboard: fly dashboard" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Deployment failed" -ForegroundColor Red
    Write-Host "Check the error messages above" -ForegroundColor Gray
    exit 1
}
