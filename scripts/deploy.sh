#!/bin/bash
# Deploy Cloud Relay to Railway using CLI
# Usage: ./deploy.sh

echo "================================"
echo "Cloud Relay - Railway Deployment"
echo "================================"
echo ""

# Check if Node.js is installed (required for Railway CLI)
if ! command -v node &> /dev/null; then
    echo "Node.js not found (required for Railway CLI)."
    echo ""
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
                exit 1
            fi
        fi
        
        if ! command -v node &> /dev/null; then
            echo ""
            echo "Node.js installed! Please restart terminal and run ./deploy.sh again"
            exit 0
        fi
    else
        echo ""
        echo "Use Web Dashboard instead: https://railway.app/new"
        echo "  1. Click 'Deploy from GitHub repo'"
        echo "  2. Select clipboard-sync-tool repository"
        echo "  3. Set Root Directory to 'cloud-relay'"
        echo "  4. Generate Domain in Settings"
        exit 0
    fi
fi

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "Installing Railway CLI via npm..."
    npm install -g @railway/cli
    
    # Add npm global bin to PATH
    NPM_BIN=$(npm bin -g 2>/dev/null)
    if [ -n "$NPM_BIN" ] && [ -d "$NPM_BIN" ]; then
        export PATH="$NPM_BIN:$PATH"
    fi
    
    # Also check common npm global locations
    if ! command -v railway &> /dev/null; then
        for path in "$HOME/.npm-global/bin" "$HOME/.local/bin" "/usr/local/bin"; do
            if [ -f "$path/railway" ]; then
                export PATH="$path:$PATH"
                break
            fi
        done
    fi
    
    if ! command -v railway &> /dev/null; then
        echo ""
        echo "Railway CLI installed but not found in PATH."
        echo "Please restart terminal and run ./deploy.sh again"
        echo ""
        echo "Or use Web Dashboard: https://railway.app/new"
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
        CLEAN_URL=$(echo "$DOMAIN" | tr -d '[:space:]')
        
        # Save to config first
        cd ..
        cat > cloud-relay-config.json <<EOF
{
  "cloudRelayUrl": "$CLEAN_URL",
  "deployedAt": "$(date '+%Y-%m-%d %H:%M:%S')",
  "platform": "railway",
  "deployMethod": "cli"
}
EOF
        
        # Display prominent URL box
        echo ""
        echo "========================================"
        echo "  CLOUD RELAY DEPLOYED SUCCESSFULLY!   "
        echo "========================================"
        echo ""
        echo "  Your URL:"
        echo ""
        echo "    $CLEAN_URL"
        echo ""
        echo "  (URL saved to cloud-relay-config.json)"
        echo ""
        echo "========================================"
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
echo "Next Steps:"
echo "  1. Run desktop app: python main.py"
echo "  2. Click 'Cloud Relay' and enter Room ID"
echo "  3. Open URL on mobile, enter same Room ID"
echo ""
