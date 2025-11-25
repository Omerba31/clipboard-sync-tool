#!/bin/bash
# Installation script for Clipboard Sync Tool
# Installs both Python (desktop app) and Node.js (cloud relay) dependencies

echo "================================"
echo "Clipboard Sync Tool - Installer"
echo "================================"
echo ""

# Check Python
echo "Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ $PYTHON_VERSION found"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo "✅ $PYTHON_VERSION found"
    PYTHON_CMD="python"
else
    echo "❌ Python not found. Please install Python 3.8+ from https://www.python.org/"
    exit 1
fi

# Check Node.js
echo "Checking Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js $NODE_VERSION found"
    NODE_INSTALLED=true
else
    echo "⚠️  Node.js not found (required for cloud relay deployment)"
    
    # Offer to install
    read -p "Install Node.js now? [y/N]: " install_node
    if [ "$install_node" = "y" ] || [ "$install_node" = "Y" ]; then
        echo "Installing Node.js..."
        
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS - use brew
            if command -v brew &> /dev/null; then
                brew install node
            else
                echo "Installing Homebrew first..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
                brew install node
            fi
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Linux - use apt or dnf
            if command -v apt &> /dev/null; then
                curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
                sudo apt-get install -y nodejs
            elif command -v dnf &> /dev/null; then
                sudo dnf install -y nodejs
            elif command -v pacman &> /dev/null; then
                sudo pacman -S nodejs npm
            else
                echo "Please install Node.js manually from https://nodejs.org"
            fi
        fi
        
        if command -v node &> /dev/null; then
            echo "✅ Node.js installed successfully"
            NODE_INSTALLED=true
        else
            echo "⚠️  Node.js installation may require terminal restart"
            NODE_INSTALLED=false
        fi
    else
        NODE_INSTALLED=false
    fi
fi

# Check Git (needed for Railway deployment)
echo "Checking Git..."
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version)
    echo "✅ $GIT_VERSION found"
    GIT_INSTALLED=true
else
    echo "⚠️  Git not found (needed for Railway deployment)"
    GIT_INSTALLED=false
fi

echo ""
echo "================================"
echo "Installing Dependencies..."
echo "================================"
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
echo "Running: pip install -r requirements.txt"
$PYTHON_CMD -m pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✅ Python dependencies installed successfully!"
else
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

echo ""

# Install Node.js dependencies (if Node.js is available)
if [ "$NODE_INSTALLED" = true ]; then
    echo "📦 Installing Node.js dependencies (cloud relay)..."
    echo "Running: cd cloud-relay && npm install"
    
    cd cloud-relay
    npm install
    if [ $? -eq 0 ]; then
        echo "✅ Node.js dependencies installed successfully!"
    else
        echo "❌ Failed to install Node.js dependencies"
        cd ..
        exit 1
    fi
    cd ..
else
    echo "⏭️  Skipping Node.js dependencies (Node.js not installed)"
    echo "   Cloud relay won't be available until Node.js is installed"
fi

# Prompt for Railway deployment
DEPLOYED_URL=""
if [ "$NODE_INSTALLED" = true ] && [ "$GIT_INSTALLED" = true ]; then
    echo ""
    echo "================================"
    echo "Deploy Cloud Relay to Railway?"
    echo "================================"
    echo ""
    echo "Would you like to deploy the cloud relay to Railway.app now?"
    echo "(This enables mobile device sync over the internet)"
    echo "Railway offers \$5 free credit/month (no credit card needed)"
    echo ""
    echo "Deployment options:"
    echo "  [1] CLI Deploy (Recommended - automatic, uses Railway CLI)"
    echo "  [2] Web Deploy (Manual - uses Railway web dashboard)"
    echo "  [3] Skip (Deploy later)"
    echo ""
    read -p "Choose option (1/2/3): " deploy_response
    
    if [ "$deploy_response" = "1" ]; then
        # CLI Deployment
        echo ""
        echo "Starting CLI deployment..."
        
        # Check if Railway CLI is installed
        if ! command -v railway &> /dev/null; then
            echo "Installing Railway CLI via npm..."
            npm install -g @railway/cli
        fi
        
        if command -v railway &> /dev/null; then
            echo "✅ Railway CLI found"
            
            # Check login status
            echo ""
            echo "Checking Railway login..."
            if ! railway whoami &> /dev/null; then
                echo "Opening browser for Railway authentication..."
                railway login
            fi
            
            if railway whoami &> /dev/null; then
                echo "✅ Logged in to Railway"
                
                # Navigate to cloud-relay directory
                cd cloud-relay
                
                echo ""
                echo "Deploying cloud-relay to Railway..."
                echo "(This may take 1-2 minutes)"
                
                # Initialize project if not already linked
                if ! railway status &> /dev/null; then
                    echo ""
                    echo "Creating new Railway project..."
                    railway init
                fi
                
                # Deploy
                if railway up; then
                    echo ""
                    echo "✅ Deployment successful!"
                    
                    # Get the domain
                    echo ""
                    echo "Getting deployment URL..."
                    domain=$(railway domain 2>&1)
                    
                    if [[ $domain =~ https:// ]]; then
                        DEPLOYED_URL=$(echo "$domain" | tr -d '[:space:]')
                        echo ""
                        echo "Your cloud relay URL:"
                        echo "  $DEPLOYED_URL"
                        
                        # Save to config
                        cd ..
                        cat > cloud-relay-config.json <<EOF
{
  "cloudRelayUrl": "$DEPLOYED_URL",
  "deployedAt": "$(date '+%Y-%m-%d %H:%M:%S')",
  "platform": "railway",
  "deployMethod": "cli"
}
EOF
                        echo ""
                        echo "✅ URL saved to cloud-relay-config.json"
                    else
                        cd ..
                        echo ""
                        echo "⚠️  Domain not generated automatically."
                        echo "   Generate one with: cd cloud-relay && railway domain"
                    fi
                else
                    cd ..
                    echo ""
                    echo "❌ Deployment failed. Try again with: ./scripts/deploy.sh"
                fi
            fi
        else
            echo "⚠️  Railway CLI installation failed."
            echo "   Try: ./scripts/deploy.sh"
            echo "   Or use web deploy: https://railway.app/new"
        fi
        
    elif [ "$deploy_response" = "2" ]; then
        # Web Deployment
        echo ""
        echo "Railway Web Deployment Steps:"
        echo ""
        echo "1. Push your code to GitHub (if not already):"
        echo "   git add ."
        echo "   git commit -m 'Deploy to Railway'"
        echo "   git push"
        echo ""
        echo "2. Go to: https://railway.app/new"
        echo "   - Click 'Deploy from GitHub repo'"
        echo "   - Select your clipboard-sync-tool repository"
        echo "   - Click 'Deploy Now'"
        echo ""
        echo "3. Configure your service (IMPORTANT):"
        echo "   - Click on your service"
        echo "   - Go to Settings tab"
        echo "   - Set Root Directory to: cloud-relay"
        echo "   - Click 'Generate Domain' to get your URL"
        echo ""
        echo "4. Save your URL:"
        echo "   - Copy the generated domain (e.g., yourapp.up.railway.app)"
        echo "   - It will be auto-loaded in the desktop app!"
        echo ""
        echo "Opening Railway deployment page..."
        
        # Open browser based on OS
        if [[ "$OSTYPE" == "darwin"* ]]; then
            open "https://railway.app/new"
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            xdg-open "https://railway.app/new" 2>/dev/null || echo "Please open: https://railway.app/new"
        fi
        
        echo ""
        read -p "After deployment, enter your Railway URL (or press Enter to skip): " railway_url
        
        if [ -n "$railway_url" ]; then
            # Ensure URL has https://
            if [[ ! $railway_url =~ ^https?:// ]]; then
                railway_url="https://$railway_url"
            fi
            
            # Save URL to config file
            cat > cloud-relay-config.json <<EOF
{
  "cloudRelayUrl": "$railway_url",
  "deployedAt": "$(date '+%Y-%m-%d %H:%M:%S')",
  "platform": "railway",
  "deployMethod": "web"
}
EOF
            echo "✅ URL saved to cloud-relay-config.json"
            DEPLOYED_URL="$railway_url"
        fi
    else
        echo "Skipping cloud relay deployment"
        echo "You can deploy later with: ./scripts/deploy.sh"
    fi
elif [ "$GIT_INSTALLED" = false ]; then
    echo ""
    echo "⚠️  Git not found - needed for Railway deployment"
    echo "   Install Git from your package manager or https://git-scm.com/downloads"
fi

echo ""
echo "================================"
echo "Installation Complete! 🎉"
echo "================================"
echo ""
echo "Next steps:"
echo "  1. Run the desktop app: $PYTHON_CMD main.py"
if [ -n "$DEPLOYED_URL" ]; then
    echo "  2. Open on mobile: $DEPLOYED_URL"
    echo "  3. Enter same Room ID on both devices"
else
    echo "  2. Deploy cloud relay: ./scripts/deploy.sh"
    echo "     Or via web: https://railway.app/new"
fi
echo ""
echo "Other commands:"
echo "  Run tests:    $PYTHON_CMD -m pytest tests/ -v"
echo "  Deploy:       ./scripts/deploy.sh"
echo ""
