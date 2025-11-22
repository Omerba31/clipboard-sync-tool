# Deploy Cloud Relay to Fly.io
# This script helps deploy the cloud relay server for mobile sync

# Set console to UTF-8 to support emojis
chcp 65001 > $null
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Cloud Relay Deployment Helper" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if Fly CLI is installed
Write-Host "Checking Fly CLI..." -ForegroundColor Yellow

# Try different commands (flyctl is more reliable than fly on Windows)
$flyCmd = $null
$commands = @("flyctl", "fly")

foreach ($cmd in $commands) {
    try {
        $testOutput = & $cmd version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $flyCmd = $cmd
            Write-Host "$([char]0x2705) Fly CLI found: $cmd" -ForegroundColor Green
            break
        }
    } catch {
        # Command not found, try next one
        continue
    }
}

if (-not $flyCmd) {
    # Try direct path
    $directPath = "$env:USERPROFILE\.fly\bin\flyctl.exe"
    if (Test-Path $directPath) {
        try {
            # Test if we can execute it
            $testOutput = & $directPath version 2>&1
            if ($LASTEXITCODE -eq 0) {
                $flyCmd = $directPath
                Write-Host "$([char]0x2705) Fly CLI found at: $directPath" -ForegroundColor Green
            }
        } catch {
            Write-Host "$([char]0x26A0)$([char]0xFE0F) Fly CLI found but cannot execute (permission issue)" -ForegroundColor Yellow
        }
    }
}

if (-not $flyCmd) {
    Write-Host "$([char]0x274C) Fly CLI not found or not accessible" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting Steps:" -ForegroundColor Yellow
    Write-Host "1. Close ALL PowerShell windows" -ForegroundColor White
    Write-Host "2. Open a NEW PowerShell window (as Administrator if needed)" -ForegroundColor White
    Write-Host "3. Run: flyctl version" -ForegroundColor White
    Write-Host ""
    Write-Host "If 'flyctl' command not found:" -ForegroundColor Yellow
    Write-Host "Install with: iwr https://fly.io/install.ps1 -useb | iex" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "If 'Access Denied' error:" -ForegroundColor Yellow
    Write-Host "- Run PowerShell as Administrator, OR" -ForegroundColor White
    Write-Host "- Unblock the file: Unblock-File `$env:USERPROFILE\.fly\bin\flyctl.exe" -ForegroundColor White
    Write-Host ""
    exit 1
}

# Check if user is logged in
Write-Host ""
Write-Host "Checking Fly.io authentication..." -ForegroundColor Yellow
$authCheck = & $flyCmd auth whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "$([char]0x26A0)$([char]0xFE0F) Not logged in to Fly.io" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Opening browser for login..." -ForegroundColor Cyan
    & $flyCmd auth login
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "$([char]0x274C) Login failed" -ForegroundColor Red
        exit 1
    }
}
Write-Host "$([char]0x2705) Authenticated" -ForegroundColor Green

# Navigate to cloud-relay directory
Write-Host ""
Write-Host "Navigating to cloud-relay directory..." -ForegroundColor Yellow
if (-not (Test-Path "cloud-relay")) {
    Write-Host "$([char]0x274C) cloud-relay directory not found!" -ForegroundColor Red
    Write-Host "Please run this script from the project root directory" -ForegroundColor Gray
    exit 1
}
Push-Location cloud-relay

# Check if already deployed
Write-Host ""
Write-Host "Checking for existing deployment..." -ForegroundColor Yellow
$flyToml = Get-Content "fly.toml" -ErrorAction SilentlyContinue
$appName = $null
foreach ($line in $flyToml) {
    if ($line -match 'app\s*=\s*"(.+)"') {
        $appName = $matches[1]
        break
    }
}

if ($appName) {
    Write-Host "Found existing app config: $appName" -ForegroundColor Cyan
    
    $flyApps = & $flyCmd apps list 2>&1
    if ($flyApps -match $appName) {
        Write-Host "$([char]0x2705) App already exists" -ForegroundColor Green
        Write-Host ""
        Write-Host "Deploying update..." -ForegroundColor Cyan
        & $flyCmd deploy
    } else {
        Write-Host "$([char]0x26A0)$([char]0xFE0F) App not found in your account" -ForegroundColor Yellow
        Write-Host "Creating new deployment..." -ForegroundColor Cyan
        & $flyCmd launch
    }
} else {
    Write-Host "No existing deployment found" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Starting new deployment..." -ForegroundColor Cyan
    Write-Host "You will be asked to choose:" -ForegroundColor Gray
    Write-Host "  - App name (default is fine)" -ForegroundColor Gray
    Write-Host "  - Region (choose closest to you)" -ForegroundColor Gray
    Write-Host "  - Database: Select NO" -ForegroundColor Gray
    Write-Host ""
    & $flyCmd launch
}

Pop-Location

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host "$([char]0x2705) Deployment Complete!" -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Your cloud relay is now live!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Getting your app URL..." -ForegroundColor Yellow
    Write-Host ""
    & $flyCmd apps list
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Copy the hostname from above" -ForegroundColor White
    Write-Host "  2. Open https://YOUR-APP.fly.dev on your mobile device" -ForegroundColor White
    Write-Host "  3. Enter a Room ID and start syncing!" -ForegroundColor White
    Write-Host ""
    Write-Host "Monitor your app:" -ForegroundColor Yellow
    Write-Host "  - Status: $flyCmd status" -ForegroundColor White
    Write-Host "  - Logs: $flyCmd logs" -ForegroundColor White
    Write-Host "  - Dashboard: $flyCmd dashboard" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "Deployment failed" -ForegroundColor Red
    Write-Host "Check the error messages above" -ForegroundColor Gray
    exit 1
}
