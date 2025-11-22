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
    Write-Host "✅ Node.js found" -ForegroundColor Green
    $hasNode = $true
} else {
    Write-Host "⚠️ Node.js not found (cloud relay will not be available)" -ForegroundColor Yellow
    $hasNode = $false
}

# Check Fly CLI
Write-Host "Checking Fly CLI..." -ForegroundColor Yellow
if (Get-Command fly -ErrorAction SilentlyContinue) {
    Write-Host "✅ Fly CLI found" -ForegroundColor Green
    $hasFly = $true
} else {
    Write-Host "⚠️ Fly CLI not found" -ForegroundColor Yellow
    Write-Host "   Installing Fly CLI..." -ForegroundColor Yellow
    try {
        iwr https://fly.io/install.ps1 -useb | iex
        # Update PATH for current session
        $env:Path += ";$env:USERPROFILE\.fly\bin"
        Write-Host "✅ Fly CLI installed successfully" -ForegroundColor Green
        $hasFly = $true
    } catch {
        Write-Host "⚠️ Could not install Fly CLI automatically" -ForegroundColor Yellow
        Write-Host "   You can install it manually later with:" -ForegroundColor Yellow
        Write-Host "   iwr https://fly.io/install.ps1 -useb | iex" -ForegroundColor Cyan
        $hasFly = $false
    }
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

# Auto-deploy to Fly.io if both Node.js and Fly CLI are available
$deployedUrl = $null
if ($hasNode -and $hasFly) {
    Write-Host ""
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host "Auto-Deploying Cloud Relay" -ForegroundColor Cyan
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Would you like to deploy the cloud relay to Fly.io now? (y/n)" -ForegroundColor Yellow
    Write-Host "(This enables mobile device sync over the internet)" -ForegroundColor Gray
    $deployResponse = Read-Host "Deploy"
    
    if ($deployResponse -eq 'y' -or $deployResponse -eq 'Y' -or $deployResponse -eq '') {
        Write-Host ""
        Write-Host "Deploying to Fly.io..." -ForegroundColor Cyan
        
        # Use flyctl instead of fly for better compatibility
        $flyCmd = "flyctl"
        if (-not (Get-Command flyctl -ErrorAction SilentlyContinue)) {
            $flyCmd = "$env:USERPROFILE\.fly\bin\flyctl.exe"
        }
        
        # Check authentication
        Write-Host "Checking Fly.io authentication..." -ForegroundColor Yellow
        $authCheck = & $flyCmd auth whoami 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Opening browser for Fly.io login..." -ForegroundColor Cyan
            & $flyCmd auth login
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Authenticated" -ForegroundColor Green
            Write-Host ""
            
            # Navigate to cloud-relay and deploy
            Push-Location cloud-relay
            
            # Check if already configured
            $flyToml = Get-Content "fly.toml" -ErrorAction SilentlyContinue
            if ($flyToml -match 'app\s*=\s*"([^"]+)"') {
                $appName = $matches[1]
                Write-Host "Found existing app: $appName" -ForegroundColor Cyan
                Write-Host "Deploying update..." -ForegroundColor Yellow
                & $flyCmd deploy --yes 2>&1 | Out-Host
            } else {
                Write-Host "Creating new app..." -ForegroundColor Yellow
                Write-Host ""
                # Launch with defaults
                & $flyCmd launch --yes --name "clipboard-sync-$([System.Guid]::NewGuid().ToString().Substring(0,8))" --region sjc 2>&1 | Out-Host
            }
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host ""
                Write-Host "✅ Deployment successful!" -ForegroundColor Green
                
                # Get the deployed URL
                $statusOutput = & $flyCmd status 2>&1
                if ($statusOutput -match 'https://([^\s]+\.fly\.dev)') {
                    $deployedUrl = $matches[1]
                    Write-Host ""
                    Write-Host "🌐 Your Cloud Relay URL: https://$deployedUrl" -ForegroundColor Green
                    Write-Host ""
                    
                    # Save URL to config file
                    $config = @{
                        cloudRelayUrl = "https://$deployedUrl"
                        deployedAt = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
                    }
                    $config | ConvertTo-Json | Out-File "..\cloud-relay-config.json" -Encoding UTF8
                    Write-Host "✅ URL saved to cloud-relay-config.json" -ForegroundColor Green
                } else {
                    # Try alternative method to get URL
                    $infoOutput = & $flyCmd apps list 2>&1
                    Write-Host ""
                    Write-Host "App deployed! Check the hostname above." -ForegroundColor Green
                }
            } else {
                Write-Host ""
                Write-Host "⚠️  Deployment had issues, but may have succeeded" -ForegroundColor Yellow
                Write-Host "   Run: flyctl status (in cloud-relay folder)" -ForegroundColor Gray
            }
            
            Pop-Location
        } else {
            Write-Host "⚠️  Authentication failed, skipping deployment" -ForegroundColor Yellow
        }
    } else {
        Write-Host "Skipping cloud relay deployment" -ForegroundColor Gray
        Write-Host "You can deploy later with: .\deploy-cloud-relay.ps1" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "✅ Installation Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Run the desktop app: python main.py" -ForegroundColor White
if ($deployedUrl) {
    Write-Host "  2. Open on mobile: https://$deployedUrl" -ForegroundColor White
    Write-Host "  3. Enter same Room ID on both devices" -ForegroundColor White
} elseif ($hasFly) {
    Write-Host "  2. Deploy cloud relay: .\deploy-cloud-relay.ps1" -ForegroundColor White
}
Write-Host ""
