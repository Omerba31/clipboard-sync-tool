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

### 1️⃣ Install Desktop App

```bash
git clone https://github.com/Omerba31/clipboard-sync-tool.git
cd clipboard-sync-tool

# Windows
.\install.ps1

# Mac/Linux
chmod +x install.sh
./install.sh

# Run the app
python main.py
```

### 2️⃣ Connect Mobile Device

**🌐 Cloud Relay (Recommended - Works Anywhere)**

1. **Desktop**: Click **☁️ Cloud Relay** button
   - Enter URL: `https://clipboard-sync-tool.fly.dev`
   - Enter Room ID: `your-unique-room-name`
   - Click Connect

2. **Mobile**: Open `https://clipboard-sync-tool.fly.dev` in browser
   - Enter same Room ID
   - Enter device name (e.g., "iPhone")
   - Click Connect

3. **Done!** Now you can:
   - ✅ Copy on desktop → Tap item on mobile to paste
   - ✅ Type on mobile → Send to desktop clipboard
   - ✅ See all synced items in history

### 3️⃣ Desktop-to-Desktop (Same Wi-Fi)

**📱 Local P2P Mode**

1. **Computer 1**: Click **📱 Local P2P** → Show QR code
2. **Computer 2**: Click **📱 Local P2P** → Enter QR Data tab → Paste data → Pair
3. **Done!** Clipboards stay in sync with end-to-end encryption

---

## 📖 How to Use

### Mobile Web App Features

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

### Desktop App Features

**Dashboard Tab:**
- View total syncs, active devices, and recent activity
- Real-time statistics

**History Tab:**
- 📜 View all synced clipboard items
- 🔍 Search by content
- 🏷️ Filter by type (Text, Images, URLs, Code)
- 📋 Click any item to copy it back to clipboard

**Devices Tab:**
- ☁️ **Cloud Relay Status** - Shows connection state with visual feedback
  - 🟢 Green = Connected to cloud relay
  - 🟠 Orange = Not connected
  - Shows server URL and Room ID when connected
  - **📤 Test Sync** button to verify connection
- 💡 **Local P2P** - Discover devices on same network
  - Shows discovered and paired devices
  - Connect for encrypted P2P sync

**Settings Tab:**
- Configure auto-sync behavior
- Choose content types to sync
- Set size limits
- Customize device name

---

## 🚀 Deploy Your Own Cloud Relay (Optional)

Want to host your own relay server? It's **FREE** on Fly.io!

**Windows:**
```powershell
.\deploy-cloud-relay.ps1
```

**Mac/Linux:**
```bash
chmod +x deploy-cloud-relay.sh
./deploy-cloud-relay.sh
```

The script will:
- ✅ Install Fly CLI (if not already installed)
- ✅ Authenticate with Fly.io
- ✅ Deploy your cloud relay
- ✅ Give you your custom URL

**If Fly CLI is installed but not recognized:**

Windows (PowerShell - restart terminal or run):
```powershell
$env:Path += ";$env:USERPROFILE\.fly\bin"
```

Mac/Linux (add to ~/.bashrc or ~/.zshrc):
```bash
export PATH="$HOME/.fly/bin:$PATH"
```

Then close and reopen your terminal, or run `source ~/.bashrc` (Mac/Linux).

Then use your own URL instead of the public one!

> 💡 **Fly.io Free Tier**: 160GB bandwidth/month, plenty for clipboard sync

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

### Running Tests

```bash
# All tests
python -m pytest tests/

# Specific test
python tests/test_pairing_server.py
```

### Development Setup

```bash
# Clone repo
git clone https://github.com/Omerba31/clipboard-sync-tool.git
cd clipboard-sync-tool

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

### Local Cloud Relay Development

```bash
cd cloud-relay
npm install
node server.js
```

Then open `http://localhost:3000` on mobile.

---

## 📚 Additional Documentation

- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Detailed troubleshooting guide
- [cloud-relay/README.md](cloud-relay/README.md) - Cloud relay deployment & API

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
