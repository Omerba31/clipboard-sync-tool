#!/bin/bash
# Deploy Cloud Relay to Railway using CLI
# Usage: ./deploy.sh

echo "================================"
echo "Cloud Relay - Railway Deployment"
echo "================================"
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "Railway CLI not found. Installing..."
    
    # Try npm
    if command -v npm &> /dev/null; then
        npm install -g @railway/cli
    # Try brew on macOS
    elif command -v brew &> /dev/null; then
        brew install railway
    # Try curl install
    else
        curl -fsSL https://railway.app/install.sh | sh
    fi
    
    if ! command -v railway &> /dev/null; then
        echo ""
        echo "❌ Could not install Railway CLI automatically."
        echo "Install manually:"
        echo "  npm install -g @railway/cli"
        echo "  OR"
        echo "  brew install railway"
        echo "  OR"
        echo "  curl -fsSL https://railway.app/install.sh | sh"
        exit 1
    fi
fi

echo "✅ Railway CLI found"

# Check login status
echo ""
echo "Checking Railway login..."
if ! railway whoami &> /dev/null; then
    echo "Not logged in. Opening browser for authentication..."
    railway login
    if [ $? -ne 0 ]; then
        echo "❌ Login failed"
        exit 1
    fi
fi

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
railway up

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deployment successful!"
    
    # Get the domain
    echo ""
    echo "Getting deployment URL..."
    DOMAIN=$(railway domain 2>&1)
    
    if [[ $DOMAIN == *"https://"* ]]; then
        echo ""
        echo "Your cloud relay URL:"
        echo "  $DOMAIN"
        
        # Save to config
        cd ..
        cat > cloud-relay-config.json <<EOF
{
  "cloudRelayUrl": "$DOMAIN",
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
        echo "Domain not generated. Generate one with:"
        echo "  cd cloud-relay"
        echo "  railway domain"
    fi
else
    cd ..
    echo ""
    echo "❌ Deployment failed"
    exit 1
fi

echo ""
echo "================================"
echo "Next Steps:"
echo "================================"
echo "1. Run desktop app: python main.py"
echo "2. Click 'Cloud Relay' and enter Room ID"
echo "3. Open URL on mobile, enter same Room ID"
echo ""
