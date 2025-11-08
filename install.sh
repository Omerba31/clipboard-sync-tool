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

echo ""
echo "================================"
echo "Installation Complete! 🎉"
echo "================================"
echo ""
echo "Next steps:"
echo "  1. Desktop app: $PYTHON_CMD main.py"
if [ "$NODE_INSTALLED" = true ]; then
    echo "  2. Cloud relay: cd cloud-relay && npm start"
fi
echo ""
