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

# Function to show web dashboard instructions
function Show-WebDashboardInstructions {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  DEPLOY VIA WEB DASHBOARD" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  1. Open: https://railway.app/new" -ForegroundColor White
    Write-Host "  2. Click 'Deploy from GitHub repo'" -ForegroundColor White
    Write-Host "  3. Select 'clipboard-sync-tool' repository" -ForegroundColor White
    Write-Host "  4. Set Root Directory to: cloud-relay" -ForegroundColor White
    Write-Host "  5. Click Deploy" -ForegroundColor White
    Write-Host "  6. Go to Settings > Networking > Generate Domain" -ForegroundColor White
    Write-Host ""
    Write-Host "  Then update cloud-relay-config.json with your URL" -ForegroundColor Gray
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Try to open browser
    Start-Process "https://railway.app/new"
}

# Check if Railway CLI is installed and working
$railwayCli = Get-Command railway -ErrorAction SilentlyContinue
$railwayWorking = $false

if ($railwayCli) {
    # Test if CLI actually works (some Node.js versions have issues)
    $testOutput = railway --version 2>&1
    if ($testOutput -and $testOutput -notmatch "error") {
        $railwayWorking = $true
    }
}

if (-not $railwayWorking) {
    Write-Host "Installing Railway CLI via npm..." -ForegroundColor Yellow
    npm install -g @railway/cli 2>$null
    
    # Refresh PATH to find newly installed global npm packages
    $npmGlobalPath = (npm root -g) -replace 'node_modules$', ''
    if ($npmGlobalPath -and (Test-Path $npmGlobalPath)) {
        $env:Path = "$npmGlobalPath;$env:Path"
    }
    
    # Also add npm global bin to PATH
    $npmBin = npm bin -g 2>$null
    if ($npmBin -and ($npmBin -is [string]) -and ($npmBin.Trim() -ne "")) {
        $npmBinPath = $npmBin.Trim()
        if (Test-Path $npmBinPath) {
            $env:Path = "$npmBinPath;$env:Path"
        }
    }
    
    # Try to find railway again
    $railwayCli = Get-Command railway -ErrorAction SilentlyContinue
    
    if (-not $railwayCli) {
        # Try common npm global locations on Windows
        $possiblePaths = @(
            "$env:APPDATA\npm\railway.cmd",
            "$env:APPDATA\npm\railway",
            "$env:ProgramFiles\nodejs\railway.cmd"
        )
        
        foreach ($path in $possiblePaths) {
            if (Test-Path $path) {
                $railwayPath = Split-Path $path -Parent
                $env:Path = "$railwayPath;$env:Path"
                $railwayCli = Get-Command railway -ErrorAction SilentlyContinue
                if ($railwayCli) { break }
            }
        }
    }
    
    if (-not $railwayCli) {
        Write-Host ""
        Write-Host "Railway CLI not found in PATH." -ForegroundColor Yellow
        Show-WebDashboardInstructions
        exit 1
    }
    
    # Test if CLI actually works
    $testOutput = railway --version 2>&1
    if (-not $testOutput -or $testOutput -eq "") {
        Write-Host ""
        Write-Host "Railway CLI installed but not working (Node.js compatibility issue)." -ForegroundColor Yellow
        Show-WebDashboardInstructions
        exit 1
    }
    
    $railwayWorking = $true
}

if (-not $railwayWorking) {
    Write-Host ""
    Write-Host "Railway CLI not working properly." -ForegroundColor Yellow
    Show-WebDashboardInstructions
    exit 1
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
        $cleanUrl = $domain.Trim()
        
        # Save to config first
        Pop-Location
        $config = @{
            cloudRelayUrl = $cleanUrl
            deployedAt = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
            platform = "railway"
            deployMethod = "cli"
        }
        $config | ConvertTo-Json | Out-File "cloud-relay-config.json" -Encoding UTF8
        
        # Display prominent URL box
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  CLOUD RELAY DEPLOYED SUCCESSFULLY!   " -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "  Your URL:" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "    $cleanUrl" -ForegroundColor White -BackgroundColor DarkBlue
        Write-Host ""
        Write-Host "  (URL saved to cloud-relay-config.json)" -ForegroundColor Gray
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
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
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Run desktop app: python main.py" -ForegroundColor White
Write-Host "  2. Click 'Cloud Relay' and enter Room ID" -ForegroundColor White
Write-Host "  3. Open URL on mobile, enter same Room ID" -ForegroundColor White
Write-Host ""
