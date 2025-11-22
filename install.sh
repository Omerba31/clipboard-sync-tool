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

# Check Fly CLI
echo "Checking Fly CLI..."
if command -v fly &> /dev/null; then
    FLY_VERSION=$(fly version 2>&1 | head -n1)
    echo "✅ Fly CLI found ($FLY_VERSION)"
    FLY_INSTALLED=true
else
    echo "⚠️  Fly CLI not found"
    echo "   Installing Fly CLI..."
    
    # Install Fly CLI
    if curl -L https://fly.io/install.sh | sh; then
        # Update PATH for current session
        export FLYCTL_INSTALL="$HOME/.fly"
        export PATH="$FLYCTL_INSTALL/bin:$PATH"
        echo "✅ Fly CLI installed successfully"
        echo "   Note: Restart your terminal or run: export PATH=\"\$HOME/.fly/bin:\$PATH\""
        FLY_INSTALLED=true
    else
        echo "⚠️  Could not install Fly CLI automatically"
        echo "   You can install it manually later with:"
        echo "   curl -L https://fly.io/install.sh | sh"
        FLY_INSTALLED=false
    fi
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

# Auto-deploy to Fly.io if both Node.js and Fly CLI are available
DEPLOYED_URL=""
if [ "$NODE_INSTALLED" = true ] && [ "$FLY_INSTALLED" = true ]; then
    echo ""
    echo "================================"
    echo "Auto-Deploying Cloud Relay"
    echo "================================"
    echo ""
    echo "Would you like to deploy the cloud relay to Fly.io now?"
    echo "(This enables mobile device sync over the internet)"
    read -p "Deploy [y/N]: " deploy_response
    
    if [ "$deploy_response" = "y" ] || [ "$deploy_response" = "Y" ]; then
        echo ""
        echo "Deploying to Fly.io..."
        
        # Determine fly command
        if command -v flyctl &> /dev/null; then
            FLY_CMD="flyctl"
        else
            FLY_CMD="$HOME/.fly/bin/flyctl"
        fi
        
        # Check authentication
        echo "Checking Fly.io authentication..."
        if ! $FLY_CMD auth whoami &> /dev/null; then
            echo "Opening browser for Fly.io login..."
            $FLY_CMD auth login
        fi
        
        if $FLY_CMD auth whoami &> /dev/null; then
            echo "✅ Authenticated"
            echo ""
            
            # Navigate to cloud-relay and deploy
            cd cloud-relay
            
            # Check if already configured
            if grep -q 'app.*=' fly.toml 2>/dev/null; then
                APP_NAME=$(grep 'app.*=' fly.toml | cut -d'"' -f2)
                echo "Found existing app: $APP_NAME"
                echo "Deploying update..."
                $FLY_CMD deploy --yes
            else
                echo "Creating new app..."
                APP_NAME="clipboard-sync-$(head /dev/urandom | tr -dc a-z0-9 | head -c 8)"
                $FLY_CMD launch --yes --name "$APP_NAME" --region sjc
            fi
            
            if [ $? -eq 0 ]; then
                echo ""
                echo "✅ Deployment successful!"
                
                # Get the deployed URL
                APP_NAME=$(grep 'app.*=' fly.toml | cut -d'"' -f2)
                DEPLOYED_URL="$APP_NAME.fly.dev"
                echo ""
                echo "🌐 Your Cloud Relay URL: https://$DEPLOYED_URL"
                echo ""
                
                # Save URL to config file
                cat > ../cloud-relay-config.json <<EOF
{
  "cloudRelayUrl": "https://$DEPLOYED_URL",
  "deployedAt": "$(date '+%Y-%m-%d %H:%M:%S')"
}
EOF
                echo "✅ URL saved to cloud-relay-config.json"
            else
                echo ""
                echo "⚠️  Deployment had issues, but may have succeeded"
                echo "   Run: $FLY_CMD status (in cloud-relay folder)"
            fi
            
            cd ..
        else
            echo "⚠️  Authentication failed, skipping deployment"
        fi
    else
        echo "Skipping cloud relay deployment"
        echo "You can deploy later with: ./deploy-cloud-relay.sh"
    fi
fi

echo ""
echo "================================"
echo "Installation Complete! 🎉"
echo "================================"
echo ""
echo "Next steps:"
echo "  1. Run the desktop app: $PYTHON_CMD main.py"
if [ -n "$DEPLOYED_URL" ]; then
    echo "  2. Open on mobile: https://$DEPLOYED_URL"
    echo "  3. Enter same Room ID on both devices"
elif [ "$FLY_INSTALLED" = true ]; then
    echo "  2. Deploy cloud relay: ./deploy-cloud-relay.sh"
fi
echo ""
if [ "$FLY_INSTALLED" = true ] && ! command -v fly &> /dev/null && [ -z "$DEPLOYED_URL" ]; then
    echo "⚠️  Note: Restart your terminal or run this command to use Fly CLI:"
    echo "   export PATH=\"\$HOME/.fly/bin:\$PATH\""
    echo ""
fi
