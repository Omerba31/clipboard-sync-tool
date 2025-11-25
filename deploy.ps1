# Deploy Cloud Relay to Railway using CLI
# Usage: .\deploy.ps1

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Cloud Relay - Railway Deployment" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if Railway CLI is installed
$railwayCli = Get-Command railway -ErrorAction SilentlyContinue

if (-not $railwayCli) {
    Write-Host "Railway CLI not found. Installing..." -ForegroundColor Yellow
    
    # Try npm install
    if (Get-Command npm -ErrorAction SilentlyContinue) {
        npm install -g @railway/cli
        $railwayCli = Get-Command railway -ErrorAction SilentlyContinue
    }
    
    # Try scoop
    if (-not $railwayCli -and (Get-Command scoop -ErrorAction SilentlyContinue)) {
        scoop install railway
        $railwayCli = Get-Command railway -ErrorAction SilentlyContinue
    }
    
    if (-not $railwayCli) {
        Write-Host ""
        Write-Host "Could not install Railway CLI automatically." -ForegroundColor Red
        Write-Host "Install manually:" -ForegroundColor Yellow
        Write-Host "  npm install -g @railway/cli" -ForegroundColor White
        Write-Host "  OR" -ForegroundColor Gray
        Write-Host "  scoop install railway" -ForegroundColor White
        Write-Host "  OR download from: https://docs.railway.app/guides/cli" -ForegroundColor White
        exit 1
    }
}

Write-Host "Railway CLI found" -ForegroundColor Green

# Check login status
Write-Host ""
Write-Host "Checking Railway login..." -ForegroundColor Yellow
$loginCheck = railway whoami 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "Not logged in. Opening browser for authentication..." -ForegroundColor Yellow
    railway login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Login failed" -ForegroundColor Red
        exit 1
    }
}

Write-Host "Logged in to Railway" -ForegroundColor Green

# Navigate to cloud-relay directory
Push-Location cloud-relay

Write-Host ""
Write-Host "Deploying cloud-relay to Railway..." -ForegroundColor Yellow
Write-Host "(This may take 1-2 minutes)" -ForegroundColor Gray

# Initialize project if not already linked
$projectCheck = railway status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Creating new Railway project..." -ForegroundColor Yellow
    railway init
}

# Deploy
railway up

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Deployment successful!" -ForegroundColor Green
    
    # Get the domain
    Write-Host ""
    Write-Host "Getting deployment URL..." -ForegroundColor Yellow
    $domain = railway domain 2>&1
    
    if ($domain -match "https://") {
        Write-Host ""
        Write-Host "Your cloud relay URL:" -ForegroundColor Cyan
        Write-Host "  $domain" -ForegroundColor White
        
        # Save to config
        Pop-Location
        $config = @{
            cloudRelayUrl = $domain.Trim()
            deployedAt = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
            platform = "railway"
            deployMethod = "cli"
        }
        $config | ConvertTo-Json | Out-File "cloud-relay-config.json" -Encoding UTF8
        Write-Host ""
        Write-Host "URL saved to cloud-relay-config.json" -ForegroundColor Green
    } else {
        Pop-Location
        Write-Host ""
        Write-Host "Domain not generated. Generate one with:" -ForegroundColor Yellow
        Write-Host "  cd cloud-relay" -ForegroundColor White
        Write-Host "  railway domain" -ForegroundColor White
    }
} else {
    Pop-Location
    Write-Host ""
    Write-Host "Deployment failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host "1. Run desktop app: python main.py" -ForegroundColor White
Write-Host "2. Click 'Cloud Relay' and enter Room ID" -ForegroundColor White
Write-Host "3. Open URL on mobile, enter same Room ID" -ForegroundColor White
Write-Host ""
