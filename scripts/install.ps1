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
    Write-Host "⚠️ Node.js not found" -ForegroundColor Yellow
    Write-Host "   (Required for cloud relay deployment)" -ForegroundColor Gray
    
    # Offer to install via winget
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host ""
        Write-Host "Install Node.js now? (y/n)" -ForegroundColor Yellow
        $installNode = Read-Host "Install"
        if ($installNode -eq 'y' -or $installNode -eq 'Y') {
            Write-Host "Installing Node.js via winget..." -ForegroundColor Yellow
            winget install OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements
            # Refresh PATH
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
            if (Get-Command node -ErrorAction SilentlyContinue) {
                Write-Host "✅ Node.js installed successfully" -ForegroundColor Green
                $hasNode = $true
            } else {
                Write-Host "⚠️ Node.js installed but requires terminal restart" -ForegroundColor Yellow
                Write-Host "   Please restart PowerShell and run install.ps1 again" -ForegroundColor Gray
                $hasNode = $false
            }
        } else {
            $hasNode = $false
        }
    } else {
        Write-Host "   Install from: https://nodejs.org" -ForegroundColor Gray
        $hasNode = $false
    }
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
python -m pip install -r requirements.txt

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
    Write-Host "Would you like to deploy the cloud relay to Railway.app now?" -ForegroundColor Yellow
    Write-Host "(This enables mobile device sync over the internet)" -ForegroundColor Gray
    Write-Host "Railway offers `$5 free credit/month (no credit card needed)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Deployment options:" -ForegroundColor Cyan
    Write-Host "  [1] CLI Deploy (Recommended - automatic, uses Railway CLI)" -ForegroundColor White
    Write-Host "  [2] Web Deploy (Manual - uses Railway web dashboard)" -ForegroundColor White
    Write-Host "  [3] Skip (Deploy later)" -ForegroundColor White
    Write-Host ""
    $deployResponse = Read-Host "Choose option (1/2/3)"
    
    if ($deployResponse -eq '1') {
        # CLI Deployment
        Write-Host ""
        Write-Host "Starting CLI deployment..." -ForegroundColor Yellow
        
        # Check if Railway CLI is installed
        $railwayCli = Get-Command railway -ErrorAction SilentlyContinue
        
        if (-not $railwayCli) {
            Write-Host "Installing Railway CLI via npm..." -ForegroundColor Yellow
            npm install -g @railway/cli
            
            # Refresh PATH to find railway
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
            $npmGlobalPath = (npm root -g) -replace "node_modules$", "node_modules\.bin"
            if ($npmGlobalPath -and (Test-Path $npmGlobalPath)) {
                $env:Path = "$npmGlobalPath;$env:Path"
            }
            
            $railwayCli = Get-Command railway -ErrorAction SilentlyContinue
            
            if (-not $railwayCli) {
                Write-Host "⚠️  Railway CLI installed but not found in PATH" -ForegroundColor Yellow
                Write-Host "   Please restart PowerShell and run: .\scripts\deploy.ps1" -ForegroundColor Gray
                Write-Host ""
                Write-Host "   Or use web deploy: https://railway.app/new" -ForegroundColor Gray
            }
        }
        
        if ($railwayCli) {
            Write-Host "✅ Railway CLI found" -ForegroundColor Green
            
            # Check login status
            Write-Host ""
            Write-Host "Checking Railway login..." -ForegroundColor Yellow
            $loginCheck = railway whoami 2>&1
            
            if ($LASTEXITCODE -ne 0) {
                Write-Host "Opening browser for Railway authentication..." -ForegroundColor Yellow
                railway login
                if ($LASTEXITCODE -ne 0) {
                    Write-Host "❌ Login failed. Try again later with: .\scripts\deploy.ps1" -ForegroundColor Red
                }
            }
            
            if ($LASTEXITCODE -eq 0 -or (railway whoami 2>&1; $LASTEXITCODE -eq 0)) {
                Write-Host "✅ Logged in to Railway" -ForegroundColor Green
                
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
                    Write-Host "✅ Deployment successful!" -ForegroundColor Green
                    
                    # Get the domain
                    Write-Host ""
                    Write-Host "Getting deployment URL..." -ForegroundColor Yellow
                    $domain = railway domain 2>&1
                    
                    if ($domain -match "https://") {
                        $deployedUrl = $domain.Trim()
                        Write-Host ""
                        Write-Host "Your cloud relay URL:" -ForegroundColor Cyan
                        Write-Host "  $deployedUrl" -ForegroundColor White
                        
                        # Save to config
                        Pop-Location
                        $config = @{
                            cloudRelayUrl = $deployedUrl
                            deployedAt = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
                            platform = "railway"
                            deployMethod = "cli"
                        }
                        $config | ConvertTo-Json | Out-File "cloud-relay-config.json" -Encoding UTF8
                        Write-Host ""
                        Write-Host "✅ URL saved to cloud-relay-config.json" -ForegroundColor Green
                    } else {
                        Pop-Location
                        Write-Host ""
                        Write-Host "⚠️  Domain not generated automatically." -ForegroundColor Yellow
                        Write-Host "   Generate one with:" -ForegroundColor Gray
                        Write-Host "   cd cloud-relay; railway domain" -ForegroundColor White
                    }
                } else {
                    Pop-Location
                    Write-Host ""
                    Write-Host "❌ Deployment failed. Try again with: .\scripts\deploy.ps1" -ForegroundColor Red
                }
            }
        }
        
    } elseif ($deployResponse -eq '2') {
        # Web Deployment
        Write-Host ""
        Write-Host "Railway Web Deployment Steps:" -ForegroundColor Cyan
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
        Write-Host "3. Configure your service (IMPORTANT):" -ForegroundColor Yellow
        Write-Host "   - Click on your service" -ForegroundColor White
        Write-Host "   - Go to Settings tab" -ForegroundColor White
        Write-Host "   - Set Root Directory to: cloud-relay" -ForegroundColor Cyan
        Write-Host "   - Click 'Generate Domain' to get your URL" -ForegroundColor White
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
                deployMethod = "web"
            }
            $config | ConvertTo-Json | Out-File "cloud-relay-config.json" -Encoding UTF8
            Write-Host "✅ URL saved to cloud-relay-config.json" -ForegroundColor Green
            $deployedUrl = $railwayUrl
        }
    } else {
        Write-Host "Skipping cloud relay deployment" -ForegroundColor Gray
        Write-Host "You can deploy later with: .\scripts\deploy.ps1" -ForegroundColor Gray
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
    Write-Host "  2. Deploy cloud relay: .\scripts\deploy.ps1" -ForegroundColor White
    Write-Host "     Or via web: https://railway.app/new" -ForegroundColor Gray
}
Write-Host ""
Write-Host "Other commands:" -ForegroundColor Yellow
Write-Host "  Run tests:    python -m pytest tests/ -v" -ForegroundColor White
Write-Host "  Deploy:       .\scripts\deploy.ps1" -ForegroundColor White
Write-Host ""
