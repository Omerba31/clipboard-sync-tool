# 📋 Clipboard Sync Tool

**Sync your clipboard seamlessly between desktop and mobile devices** - copy on one device, paste on another instantly!

## ✨ Features

- 🔄 **Bidirectional Sync** - Copy/paste works in BOTH directions (desktop ↔ mobile)
- 🚀 **Instant Transfer** - Changes appear immediately on all connected devices
- 📱 **Mobile Support** - Full clipboard sync on iPhone, Android (web app)
- 🌐 **Works Anywhere** - Cloud relay doesn't require same Wi-Fi network
- 🖥️ **Desktop-to-Desktop** - Local P2P sync on the same network
- 🔒 **Secure** - End-to-end encryption for local P2P mode
- 🎨 **Beautiful UI** - Modern desktop app with real-time status

---

## ⚡ Quick Start

### Choose Your Setup:

#### 🚀 **Option A: Automated Install (Recommended)**

Everything set up automatically with one command!

```bash
# Clone the repository
git clone https://github.com/Omerba31/clipboard-sync-tool.git
cd clipboard-sync-tool

# Windows
.\install.ps1

# Mac/Linux
chmod +x install.sh
./install.sh
```

**What happens:**
1. ✅ Installs Python dependencies (in isolated `venv/`)
2. ✅ Auto-installs Fly CLI
3. ✅ Prompts: "Deploy cloud relay? [y/N]"
4. ✅ If yes: Deploys to Fly.io & saves your URL
5. ✅ Shows your cloud relay URL

**Then run:**
```bash
python main.py
```

Your URL is **auto-loaded** in the app! Just enter a Room ID and connect.

---

#### 🎯 **Option B: Use Public Server (No Deployment)**

Skip deployment and use the public cloud relay:

```bash
# Clone and install Python deps only
git clone https://github.com/Omerba31/clipboard-sync-tool.git
cd clipboard-sync-tool

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate     # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

**In the app:**
- Click "☁️ Cloud Relay"
- Enter URL: `https://clipboard-sync-tool.fly.dev`
- Enter a Room ID (e.g., `my-room-123`)
- Connect!

---

#### 🐳 **Option C: Docker (Development Only)**

Run cloud relay locally for development:

```bash
# Run just the cloud relay
cd cloud-relay
docker build -t clipboard-relay .
docker run -p 3000:8080 clipboard-relay

# Or use docker-compose for full stack
docker-compose up
```

**Note:** Desktop GUI doesn't work in Docker. Use this for:
- Local cloud relay development
- Testing the relay server
- Custom deployments

Then run the desktop app normally:
```bash
python main.py
# Use URL: http://localhost:3000
```

### Connect Mobile & Desktop

#### **Step 1: Start Desktop App**

```bash
python main.py
```

#### **Step 2: Connect to Cloud Relay**

1. Click **☁️ Cloud Relay** button in the app
2. The URL is **auto-filled** if you used automated install!
   - Or enter: `https://clipboard-sync-tool.fly.dev` (public server)
   - Or your deployed URL: `https://your-app.fly.dev`
3. Enter a **Room ID**: `my-clipboard-123` (any unique name)
4. Click **🔌 Connect**

#### **Step 3: Connect Mobile Device**

1. **Open your cloud relay URL** in mobile browser
   - From auto-install: Check the desktop app (URL shown)
   - Public server: `https://clipboard-sync-tool.fly.dev`
2. **Enter the SAME Room ID**: `my-clipboard-123`
3. **Enter device name**: `iPhone` or `Android`
4. Click **Connect**

#### **Step 4: Start Syncing! 🎉**

- ✅ **Desktop → Mobile**: Copy anything on desktop, tap it on mobile to paste
- ✅ **Mobile → Desktop**: Type/paste on mobile, click "📤 Send to Desktop"
- ✅ **Images**: Supported (up to 5MB)
- ✅ **History**: View all synced items in the History tab

> 💡 **Tip**: Use the same Room ID on all your devices to sync between them!

### Desktop-to-Desktop (Optional - Local Network)

For **same Wi-Fi** encrypted sync without cloud:

**📱 Local P2P Mode**

1. **Computer 1**: 
   - Click **📱 Local P2P** 
   - Click **Show QR** tab
   - Show QR code on screen

2. **Computer 2**: 
   - Click **📱 Local P2P**
   - Click **Enter QR Data** tab
   - Paste the QR data
   - Click **Pair**

3. **Done!** 
   - ✅ End-to-end encrypted
   - ✅ Works offline (same network)
   - ✅ No cloud relay needed

---

## 📖 How to Use

### 🎮 Command Line Options

```bash
# GUI mode (default) - Full desktop interface
python main.py

# CLI mode - Headless background sync
python main.py --mode cli --name "MyComputer"

# Simple mode - Basic clipboard monitor only
python main.py --mode simple

# Debug mode - Detailed logging
python main.py --debug

# Check dependencies
python main.py --check
```

### 📱 Mobile Web App Features

**Sending to Desktop:**
1. On mobile, type or paste content in the text box
2. OR tap **📷 Choose Image** to select a photo
3. Tap **📤 Send to Desktop**
4. Content instantly appears in your desktop clipboard
5. Paste anywhere (Ctrl+V / Cmd+V)

**Receiving from Desktop:**
1. Copy anything on your desktop (text or images)
2. Content appears in **📥 From Desktop** section on mobile
3. **Tap text items** to copy to clipboard
4. **Tap image items** to download to your device
5. Paste in any app

**View Connected Devices:**
- See all devices synced to the same Room ID
- Desktop and other mobile devices shown with icons

### 🖥️ Desktop App Features

**📊 Dashboard Tab:**
- View total syncs, active devices, and recent activity
- Real-time statistics

**📜 History Tab:**
- View all synced clipboard items
- 🔍 Search by content
- 🏷️ Filter by type (Text, Images, URLs, Code)
- 📋 Click any item to copy it back to clipboard

**🖥️ Devices Tab:**
- ☁️ **Cloud Relay Status** - Shows connection state
  - 🟢 Green = Connected to cloud relay
  - 🟠 Orange = Not connected
  - Shows server URL and Room ID when connected
  - **📤 Test Sync** button to verify connection
- 💡 **Local P2P** - Discover devices on same network
  - Shows discovered and paired devices
  - Connect for encrypted P2P sync

**⚙️ Settings Tab:**
- Configure auto-sync behavior
- Choose content types to sync
- Set size limits
- Customize device name

### ⚡ Quick Actions (Header)

- **⏸️ Pause** - Temporarily stop syncing
- **📱 Local P2P** - Connect to nearby devices (QR code)
- **☁️ Cloud Relay** - Connect to internet-based sync

---

## 🚀 Cloud Relay Deployment (Now Automatic!)

### Automatic During Installation (Recommended)

The installer **automatically handles everything**:

1. Run `.\install.ps1` (Windows) or `./install.sh` (Mac/Linux)
2. When prompted: `Deploy [y/N]:` → Type `y`
3. Browser opens for Fly.io login (free account)
4. ✅ Your cloud relay is deployed!
5. ✅ URL is **saved** and **auto-loaded** in the app

### Manual Deployment (If Needed)

If you skipped auto-deployment or want to redeploy:

**Windows:**
```powershell
.\deploy-cloud-relay.ps1
```

**Mac/Linux:**
```bash
chmod +x deploy-cloud-relay.sh
./deploy-cloud-relay.sh
```

### What Gets Deployed

- **Free Tier**: 160GB bandwidth/month (plenty for clipboard sync!)
- **Your URL**: `https://clipboard-sync-[random].fly.dev`
- **Auto-saved**: Stored in `cloud-relay-config.json`
- **Auto-loaded**: Pre-filled in the app's Cloud Relay dialog

> 💡 **No configuration needed** - the app reads your URL automatically!

---

## 🔐 Security & Privacy

### Cloud Relay Mode
- ⚠️ Content is Base64 encoded (NOT encrypted) for cloud relay
- 🔒 Use Room IDs that others can't guess
- 📝 Don't use for sensitive data (passwords, keys, etc.)
- ✅ Perfect for: notes, links, code snippets, general text

### Local P2P Mode (Desktop-to-Desktop)
- ✅ **Full End-to-End Encryption**
- 🔐 ECC (Elliptic Curve) key exchange
- 🔒 AES-256-GCM content encryption
- ✅ Forward secrecy (unique key per message)
- 🛡️ Digital signatures verify authenticity
- 🏠 Data never leaves your local network

**Encryption Flow:**
```
1. Pairing: Exchange public keys via QR code
2. Sending: Encrypt with AES-256, wrap key with ECDH
3. Receiving: Decrypt key with ECDH, decrypt content
4. Verify: Check GCM authentication tag
```

> 🔒 **Privacy First**: Local P2P data never touches any server!

---

## 🏗️ Architecture

### Tech Stack

**Desktop App:**
- **PyQt6** - Modern cross-platform GUI
- **Python-SocketIO** - WebSocket communication
- **Cryptography** - Industry-standard encryption
- **Zeroconf** - mDNS service discovery
- **Pyperclip** - Cross-platform clipboard access

**Cloud Relay:**
- **Node.js 18** - Server runtime
- **Socket.IO 4.6** - Real-time bidirectional sync
- **Express** - HTTP server
- **Fly.io** - Free hosting platform

**Mobile Web App:**
- **Progressive Web App (PWA)** - Install to home screen
- **Socket.IO Client** - Real-time connection
- **Vanilla JavaScript** - No frameworks, fast & simple
- **Responsive CSS** - Works on all screen sizes

### Project Structure

```
clipboard-sync-tool/
├── core/                          # Core functionality
│   ├── encryption.py              # ECC + AES-256-GCM encryption
│   ├── monitor.py                 # Clipboard monitoring
│   ├── network.py                 # P2P networking & discovery
│   ├── sync_engine.py             # Sync orchestration
│   └── cloud_relay_client.py      # Cloud relay Socket.IO client
├── gui/                           # Desktop GUI
│   ├── main_window.py             # Main application window
│   └── pairing_server.py          # HTTP server for P2P QR pairing
├── cloud-relay/                   # Cloud relay server
│   ├── server.js                  # Node.js relay (Socket.IO)
│   ├── public/
│   │   ├── index.html             # Mobile PWA UI
│   │   ├── app.js                 # Mobile app logic
│   │   └── manifest.json          # PWA manifest
│   ├── Dockerfile                 # Container for deployment
│   ├── fly.toml                   # Fly.io config
│   ├── package.json               # Node dependencies
│   └── README.md                  # Deployment guide
├── tests/                         # Organized test suite
│   ├── unit/                      # Unit tests
│   │   └── test_clipboard.py      # Clipboard functionality tests
│   ├── integration/               # Integration tests
│   │   ├── test_pairing_server.py # P2P pairing tests
│   │   ├── test_simple_server.py  # HTTP server tests
│   │   └── test_http_response.py  # HTTP verification
│   └── README.md                  # Test documentation
├── docs/                          # Additional documentation
│   └── MOBILE_PAIRING.md          # Legacy P2P pairing guide
├── logs/                          # Application logs
├── deploy-cloud-relay.ps1         # Windows deployment script
├── deploy-cloud-relay.sh          # Mac/Linux deployment script
├── install.ps1                    # Windows install script
├── install.sh                     # Mac/Linux install script
├── main.py                        # Application entry point
├── requirements.txt               # Python dependencies
├── verify_setup.py                # Environment verification
├── TROUBLESHOOTING.md             # Common issues & solutions
└── README.md                      # This file
```

---

## 🐛 Troubleshooting

### Cloud Relay Connection Issues

**Desktop says "Connected" but mobile doesn't work:**
- Refresh mobile browser
- Check Room ID matches exactly
- Try Test Sync button on desktop
- Check browser console for errors (F12)

**Mobile can't load the URL:**
- Verify URL is correct: `https://clipboard-sync-tool.fly.dev`
- Check mobile has internet connection
- Try different browser (Safari, Chrome, Firefox)
- Clear browser cache

**"Already connected" error:**
- Close and reopen desktop app
- Refresh mobile browser
- App auto-reconnects now

### Mobile Sync Not Working

**Copied on desktop, nothing on mobile:**
- Check cloud relay status card is green on desktop
- Click Test Sync button - test message should appear on mobile
- Verify both devices use same Room ID
- Check desktop clipboard has text content (images not supported in cloud relay yet)

**Tap item on mobile but nothing copies:**
- Some browsers need HTTPS for clipboard API
- Try selecting and copying text manually
- Make sure item loaded fully (not loading spinner)

### Local P2P Issues

**Devices can't discover each other:**
- Ensure both on same Wi-Fi network
- Disable VPN or add network to trusted
- Check firewall allows Python
- Try manual QR pairing instead of auto-discovery

**Pairing fails:**
- Copy QR data carefully (entire JSON)
- Check no extra spaces/characters
- Restart both apps and try again

### Desktop App Issues

**App won't start:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python version (need 3.8+)
python --version
```

**GUI freezes:**
- Fixed in latest version
- Update to latest code: `git pull`
- Restart application

### Performance

**Slow sync:**
- Large files take time (encryption overhead)
- Cloud relay has 150MB/month bandwidth limit on free tier
- Local P2P is faster for large content

**High CPU:**
- Normal during encryption/decryption
- Pause sync when not needed
- Close other heavy applications

---

## ❓ FAQ

**Q: Can mobile devices send clipboard content to desktop?**  
**A: YES!** Mobile web app has full bidirectional sync. You can type on mobile and send to desktop, or receive desktop clipboard on mobile.

**Q: Does it work without internet?**  
A: Local P2P mode works offline (same Wi-Fi). Cloud relay requires internet.

**Q: Is my data sent to the cloud?**  
A: Only if using cloud relay. Local P2P mode keeps data on your network only.

**Q: Can someone intercept my clipboard?**  
A: Local P2P: No, fully encrypted. Cloud relay: Use unique Room IDs and don't share sensitive data.

**Q: How many devices can I sync?**  
A: Unlimited! Any device with the same Room ID joins the sync.

**Q: Does it work on iPhone/Android?**  
A: Yes! Open the cloud relay URL in any mobile browser. Works as a PWA (can install to home screen).

**Q: What content types are supported?**  
A: Cloud relay: Text and images (up to 5MB). Local P2P: Text, images, files, URLs.

**Q: Can I sync between Windows and Mac?**  
A: Yes! Desktop app works on Windows, Mac, Linux.

**Q: Why do I need a Room ID?**  
A: Room ID keeps your devices separate from others using the same relay server. Choose something unique!

**Q: Will this work on public Wi-Fi?**  
A: Cloud relay: Yes. Local P2P: Usually not (devices isolated on public networks).

**Q: Can I use my own relay server?**  
A: Yes! Deploy to Fly.io (free) with the included scripts. See deploy-cloud-relay.ps1/sh

**Q: Does mobile app store clipboard history?**  
A: Yes! Last 10 items shown in "From Desktop" section. Tap any to copy.

---

## 🛠️ Development

### Requirements

- **Desktop**: Python 3.8+
- **Cloud Relay**: Node.js 18+, Fly.io account (free)
- **Deployment**: Fly CLI (auto-installed by installer)

### Quick Setup

```bash
# Clone repo
git clone https://github.com/Omerba31/clipboard-sync-tool.git
cd clipboard-sync-tool

# Run the automated installer
.\install.ps1          # Windows
./install.sh           # Mac/Linux

# Answer 'y' when prompted to deploy
# Everything will be set up automatically!

# Run app
python main.py
```

### Manual Setup (Advanced)

```bash
# Create virtual environment
python -m venv venv

# Activate venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
source venv/bin/activate      # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run app
python main.py
```

### Running Tests

```bash
# All tests
python -m pytest tests/

# Specific test
python tests/test_pairing_server.py
```

### Local Cloud Relay Development

```bash
cd cloud-relay
npm install
node server.js
```

Then open `http://localhost:3000` on mobile.

### Project Configuration

After installation, `cloud-relay-config.json` contains your deployment info:
```json
{
  "cloudRelayUrl": "https://your-app.fly.dev",
  "deployedAt": "2025-11-22 12:34:56"
}
```

The app automatically reads this file and pre-fills your URL!

---

## 📚 Additional Documentation

- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Detailed troubleshooting guide
- [cloud-relay/README.md](cloud-relay/README.md) - Cloud relay deployment & API

## 🎯 Key Features of the Automated Setup

### What the Installer Does Automatically:

1. **Dependency Management**
   - ✅ Checks for Python, Node.js, Fly CLI
   - ✅ Auto-installs Fly CLI if missing
   - ✅ Installs all required packages

2. **Cloud Relay Deployment**
   - ✅ Prompts for one-click deployment
   - ✅ Handles Fly.io authentication
   - ✅ Deploys to free tier automatically
   - ✅ Generates unique app name

3. **Configuration Management**
   - ✅ Saves your deployed URL to `cloud-relay-config.json`
   - ✅ App auto-loads URL on startup
   - ✅ Pre-fills Cloud Relay connection dialog

4. **Zero Manual Configuration**
   - ✅ No URL copying needed
   - ✅ No manual file editing
   - ✅ Just enter a Room ID and connect!

## 🐳 Docker Deployment (Alternative)

### What Runs Where

**Cloud Relay (Already Dockerized!)**
- ✅ Runs on Fly.io in a Docker container automatically
- ✅ No local Node.js installation needed
- ✅ Dockerfile already included in `cloud-relay/`

**Desktop App (Optional Docker)**

The desktop app uses Python and needs GUI access, so it's best run natively. However, for development/testing:

```bash
# Run cloud relay locally with Docker
cd cloud-relay
docker build -t clipboard-relay .
docker run -p 3000:8080 clipboard-relay

# Or use docker-compose for full stack
docker-compose up
```

**Note**: The desktop app's GUI won't work inside Docker. Docker is mainly useful for:
- Running the cloud relay locally for development
- Testing the sync engine in CLI mode
- Deploying to custom cloud providers

### Minimal Local Installation

**Don't want anything on your computer?**

1. **Desktop App**: Use Python venv (isolated, deletable)
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

2. **Cloud Relay**: Already runs in Docker on Fly.io
   - OR use public server: `https://clipboard-sync-tool.fly.dev`
   - Zero local installation!

3. **Clean Up**: Just delete the project folder
   - Everything is in `venv/` (isolated)
   - No system-wide installation needed

---

## 🗺️ Roadmap

### ✅ Completed
- ✅ Desktop-to-desktop encrypted sync
- ✅ Mobile web app (PWA)
- ✅ Cloud relay for internet-based sync
- ✅ Bidirectional mobile sync (send & receive)
- ✅ Image support in cloud relay (up to 5MB)
- ✅ Clipboard history with tap-to-copy
- ✅ Visual connection status
- ✅ Auto-reconnection
- ✅ Test sync button

### 🔜 Planned
- 🔜 End-to-end encryption for cloud relay
- 🔜 File support in cloud relay
- 🔜 Dark mode
- 🔜 System tray minimize
- 🔜 Auto-start on boot
- 🔜 Content filters (exclude passwords, etc.)
- 🔜 Native mobile apps (iOS/Android)

---

## 📄 License

[Add your license]

## 🤝 Contributing

Contributions welcome! Please submit a Pull Request.

## 💬 Support

Having issues?
1. Check [Troubleshooting](#troubleshooting)
2. Review [FAQ](#faq)
3. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
4. Open a GitHub issue with:
   - OS and Python version
   - Error messages/logs
   - Steps to reproduce

---

**Made with ❤️ for seamless clipboard sync**
