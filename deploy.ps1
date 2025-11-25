# Deploy Cloud Relay to Railway using CLI
# Usage: .\deploy.ps1

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Cloud Relay - Railway Deployment" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if Node.js is installed (required for Railway CLI)
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "Node.js not found (required for Railway CLI)." -ForegroundColor Yellow
    
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host ""
        Write-Host "Install Node.js now? (y/n)" -ForegroundColor Yellow
        $installNode = Read-Host "Install"
        if ($installNode -eq 'y' -or $installNode -eq 'Y') {
            Write-Host "Installing Node.js via winget..." -ForegroundColor Yellow
            winget install OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements
            # Refresh PATH
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
            if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
                Write-Host ""
                Write-Host "Node.js installed! Please restart PowerShell and run .\deploy.ps1 again" -ForegroundColor Green
                exit 0
            }
        } else {
            Write-Host ""
            Write-Host "Use Web Dashboard instead: https://railway.app/new" -ForegroundColor Cyan
            Write-Host "  1. Click 'Deploy from GitHub repo'" -ForegroundColor White
            Write-Host "  2. Select clipboard-sync-tool repository" -ForegroundColor White
            Write-Host "  3. Set Root Directory to 'cloud-relay'" -ForegroundColor White
            Write-Host "  4. Generate Domain in Settings" -ForegroundColor White
            exit 0
        }
    } else {
        Write-Host ""
        Write-Host "Install Node.js from: https://nodejs.org" -ForegroundColor Cyan
        Write-Host "Or use Web Dashboard: https://railway.app/new" -ForegroundColor Cyan
        exit 1
    }
}

# Check if Railway CLI is installed
$railwayCli = Get-Command railway -ErrorAction SilentlyContinue

if (-not $railwayCli) {
    Write-Host "Installing Railway CLI via npm..." -ForegroundColor Yellow
    npm install -g @railway/cli
    $railwayCli = Get-Command railway -ErrorAction SilentlyContinue
    
    if (-not $railwayCli) {
        Write-Host ""
        Write-Host "Railway CLI installation failed." -ForegroundColor Red
        Write-Host "Use Web Dashboard instead: https://railway.app/new" -ForegroundColor Cyan
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
