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
    echo "❌ Node.js not found. Please install Node.js 18+ from https://nodejs.org/"
    NODE_INSTALLED=false
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
    echo "Railway offers $5 free credit/month (no credit card needed)"
    read -p "Deploy [y/N]: " deploy_response
    
    if [ "$deploy_response" = "y" ] || [ "$deploy_response" = "Y" ]; then
        echo ""
        echo "Railway Deployment Steps:"
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
        echo "3. Configure your service:"
        echo "   - Click on your service"
        echo "   - Go to Settings tab"
        echo "   - Set Root Directory: cloud-relay"
        echo "   - Click 'Generate Domain'"
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
  "platform": "railway"
}
EOF
            echo "✅ URL saved to cloud-relay-config.json"
            DEPLOYED_URL="$railway_url"
        fi
    else
        echo "Skipping cloud relay deployment"
        echo "You can deploy later - see: cloud-relay/README.md"
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
    echo "  2. Deploy cloud relay: See cloud-relay/README.md"
    echo "     Quick: https://railway.app/new"
fi
echo ""
