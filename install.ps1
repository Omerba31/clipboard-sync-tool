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

# Check Git (needed for Railway deployment)
Write-Host "Checking Git..." -ForegroundColor Yellow
if (Get-Command git -ErrorAction SilentlyContinue) {
    Write-Host "✅ Git found" -ForegroundColor Green
    $hasGit = $true
} else {
    Write-Host "⚠️ Git not found (needed for Railway deployment)" -ForegroundColor Yellow
    $hasGit = $false
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

# Prompt for Railway deployment
$deployedUrl = $null
if ($hasNode -and $hasGit) {
    Write-Host ""
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host "Deploy Cloud Relay to Railway?" -ForegroundColor Cyan
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Would you like to deploy the cloud relay to Railway.app now? (y/n)" -ForegroundColor Yellow
    Write-Host "(This enables mobile device sync over the internet)" -ForegroundColor Gray
    Write-Host "Railway offers $5 free credit/month (no credit card needed)" -ForegroundColor Gray
    $deployResponse = Read-Host "Deploy"
    
    if ($deployResponse -eq 'y' -or $deployResponse -eq 'Y') {
        Write-Host ""
        Write-Host "Railway Deployment Steps:" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "1. Push your code to GitHub (if not already):" -ForegroundColor Yellow
        Write-Host "   git add ." -ForegroundColor White
        Write-Host "   git commit -m 'Deploy to Railway'" -ForegroundColor White
        Write-Host "   git push" -ForegroundColor White
        Write-Host ""
        Write-Host "2. Go to: https://railway.app/new" -ForegroundColor Yellow
        Write-Host "   - Click 'Deploy from GitHub repo'" -ForegroundColor White
        Write-Host "   - Select your clipboard-sync-tool repository" -ForegroundColor White
        Write-Host "   - Click 'Deploy Now'" -ForegroundColor White
        Write-Host ""
        Write-Host "3. Configure your service:" -ForegroundColor Yellow
        Write-Host "   - Click on your service" -ForegroundColor White
        Write-Host "   - Go to Settings tab" -ForegroundColor White
        Write-Host "   - Set Root Directory: cloud-relay" -ForegroundColor White
        Write-Host "   - Click 'Generate Domain'" -ForegroundColor White
        Write-Host ""
        Write-Host "4. Save your URL:" -ForegroundColor Yellow
        Write-Host "   - Copy the generated domain (e.g., yourapp.up.railway.app)" -ForegroundColor White
        Write-Host "   - It will be auto-loaded in the desktop app!" -ForegroundColor White
        Write-Host ""
        Write-Host "Press Enter to open Railway deployment page..." -ForegroundColor Cyan
        Read-Host
        Start-Process "https://railway.app/new"
        Write-Host ""
        Write-Host "After deployment, enter your Railway URL to save it:" -ForegroundColor Yellow
        $railwayUrl = Read-Host "Railway URL (or press Enter to skip)"
        
        if ($railwayUrl) {
            # Ensure URL has https://
            if ($railwayUrl -notmatch '^https?://') {
                $railwayUrl = "https://$railwayUrl"
            }
            
            # Save URL to config file
            $config = @{
                cloudRelayUrl = $railwayUrl
                deployedAt = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
                platform = "railway"
            }
            $config | ConvertTo-Json | Out-File "cloud-relay-config.json" -Encoding UTF8
            Write-Host "✅ URL saved to cloud-relay-config.json" -ForegroundColor Green
            $deployedUrl = $railwayUrl
        }
    } else {
        Write-Host "Skipping cloud relay deployment" -ForegroundColor Gray
        Write-Host "You can deploy later - see: cloud-relay/README.md" -ForegroundColor Gray
    }
} elseif (-not $hasGit) {
    Write-Host ""
    Write-Host "⚠️  Git not found - needed for Railway deployment" -ForegroundColor Yellow
    Write-Host "   Install Git from: https://git-scm.com/downloads" -ForegroundColor Gray
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "✅ Installation Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Run the desktop app: python main.py" -ForegroundColor White
if ($deployedUrl) {
    Write-Host "  2. Open on mobile: $deployedUrl" -ForegroundColor White
    Write-Host "  3. Enter same Room ID on both devices" -ForegroundColor White
} else {
    Write-Host "  2. Deploy cloud relay: See cloud-relay/README.md" -ForegroundColor White
    Write-Host "     Quick: https://railway.app/new" -ForegroundColor Gray
}
Write-Host ""
