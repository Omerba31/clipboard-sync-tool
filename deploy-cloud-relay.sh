#!/bin/bash
# Deploy Cloud Relay to Fly.io
# This script helps deploy the cloud relay server for mobile sync

echo "================================"
echo "Cloud Relay Deployment Helper"
echo "================================"
echo ""

# Check if Fly CLI is installed
echo "Checking Fly CLI..."
if command -v fly &> /dev/null; then
    FLY_VERSION=$(fly version 2>&1)
    echo "✅ Fly CLI found: $FLY_VERSION"
else
    echo "❌ Fly CLI not found"
    echo ""
    echo "Installing Fly CLI..."
    curl -L https://fly.io/install.sh | sh
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install Fly CLI"
        echo "Please install manually: https://fly.io/docs/hands-on/install-flyctl/"
        exit 1
    fi
    
    echo "✅ Fly CLI installed!"
    echo "⚠️  Please restart your terminal and run this script again"
    exit 0
fi

# Check if user is logged in
echo ""
echo "Checking Fly.io authentication..."
fly auth whoami &> /dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Not logged in to Fly.io"
    echo ""
    echo "Opening browser for login..."
    fly auth login
    
    if [ $? -ne 0 ]; then
        echo "❌ Login failed"
        exit 1
    fi
fi
echo "✅ Authenticated"

# Navigate to cloud-relay directory
echo ""
echo "Navigating to cloud-relay directory..."
if [ ! -d "cloud-relay" ]; then
    echo "❌ cloud-relay directory not found!"
    echo "Please run this script from the project root directory"
    exit 1
fi
cd cloud-relay

# Check if already deployed
echo ""
echo "Checking for existing deployment..."
if [ -f "fly.toml" ]; then
    APP_NAME=$(grep 'app = ' fly.toml | cut -d'"' -f2)
    if [ ! -z "$APP_NAME" ]; then
        echo "Found existing app config: $APP_NAME"
        
        fly apps list 2>&1 | grep -q "$APP_NAME"
        if [ $? -eq 0 ]; then
            echo "✅ App already exists"
            echo ""
            echo "Deploying update..."
            fly deploy
        else
            echo "⚠️  App not found in your account"
            echo "Creating new deployment..."
            fly launch
        fi
    else
        echo "No app name found in fly.toml"
        echo "Starting new deployment..."
        fly launch
    fi
else
    echo "No existing deployment found"
    echo ""
    echo "Starting new deployment..."
    echo "You'll be asked to choose:"
    echo "  - App name (default is fine)"
    echo "  - Region (choose closest to you)"
    echo "  - Database: Select NO"
    echo ""
    fly launch
fi

cd ..

if [ $? -eq 0 ]; then
    echo ""
    echo "================================"
    echo "✅ Deployment Complete!"
    echo "================================"
    echo ""
    echo "Your cloud relay is now live!"
    echo ""
    echo "Next steps:"
    echo "  1. Get your app URL: fly apps list"
    echo "  2. Open URL on your mobile device"
    echo "  3. Enter a Room ID and start syncing!"
    echo ""
    echo "Monitor your app:"
    echo "  - Status: fly status"
    echo "  - Logs: fly logs"
    echo "  - Dashboard: fly dashboard"
    echo ""
else
    echo ""
    echo "❌ Deployment failed"
    echo "Check the error messages above"
    exit 1
fi
