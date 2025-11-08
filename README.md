# Clipboard Sync Tool

A cross-platform clipboard synchronization tool that allows seamless clipboard sharing between devices.

**Sync Options:**
- 🖥️ **Desktop ↔ Desktop**: Local P2P on same network with end-to-end encryption
- 📱 **Desktop ↔ Mobile**: Cloud relay via Fly.io (works anywhere, FREE tier available)

## Features

- 📋 **Real-time Clipboard Sync** - Automatically sync clipboard content across devices
- 📱 **Mobile Support** - Cloud relay for mobile devices (iOS/Android via PWA)
- 🌐 **Cloud Relay** - Sync anywhere via FREE Fly.io hosting
- 🔒 **Encrypted Transfer** - All clipboard data is encrypted during transfer (local P2P)
- 🖼️ **Multiple Content Types** - Support for text, images, files, URLs, and more
- 🎨 **Modern GUI** - Clean PyQt6-based interface with emoji icons
- 🔍 **Search & Filter** - Quickly find items in clipboard history
- 🌐 **Network Discovery** - Automatic device discovery on local network (desktop-to-desktop)

## Requirements

**Desktop App:**
- Python 3.8+
- Windows/Linux/macOS
- Local network connection

**Cloud Relay (Optional, for mobile sync):**
- Node.js 18+
- Fly.io account (free tier available)

## Installation

### Option 1: Automated Installation (Recommended)

**Windows (PowerShell):**
```powershell
# Clone the repository
git clone https://github.com/Omerba31/clipboard-sync-tool.git
cd clipboard-sync-tool

# Allow script execution (if needed - run PowerShell as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run installer (installs both Python and Node.js dependencies)
.\install.ps1
```

**Note:** If you get "cannot be loaded because running scripts is disabled", run the `Set-ExecutionPolicy` command above.

**Mac/Linux:**
```bash
# Clone the repository
git clone https://github.com/Omerba31/clipboard-sync-tool.git
cd clipboard-sync-tool

# Make installer executable and run
chmod +x install.sh
./install.sh
```

The installer will:
- ✅ Check for Python and Node.js
- ✅ Install Python dependencies (desktop app)
- ✅ Install Node.js dependencies (cloud relay)
- ✅ Report any missing prerequisites

### Option 2: Manual Installation

**Step 1: Clone the repository**
```bash
git clone https://github.com/Omerba31/clipboard-sync-tool.git
cd clipboard-sync-tool
```

**Step 2: Install Python dependencies (Desktop App)**
```bash
# Optional: Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

**Step 3: Install Node.js dependencies (Cloud Relay - Optional)**
```bash
cd cloud-relay
npm install
cd ..
```

## Usage

### Quick Start Guide

**1. Launch the Application**
```bash
python main.py
```

**2. First Time Setup**
- The app will start with sync **active** by default (automatically monitoring)
- Your device will appear in the **Devices** tab

**3. Pairing Devices**

There are two ways to pair devices:

#### Option A: QR Code Pairing (Recommended for Mobile)
1. Click the **"Devices"** tab
2. Click **"Show QR"** button
3. From your mobile device:
   - Scan the QR code with your camera app
   - Open the link (e.g., `http://192.168.1.100:8080`)
   - Enter a device name (e.g., "My iPhone")
   - Click **"Pair Device"**
4. The device will appear in your devices list

#### Option B: Manual QR Data Entry (For Desktop-to-Desktop)
1. On Device A: Click **"Show QR"** → Copy the QR data text
2. On Device B: Click **"Enter QR Data"** tab → Paste the QR data
3. Click **"Pair"**
4. Devices are now connected!

**4. Using Clipboard Sync**
- Copy anything on one device (text, image, file, etc.)
- It automatically appears on all paired devices
- View history in the **"History"** tab
- Filter by type using the dropdown menu
- Search for specific content using the search box

### Main Window Interface

**History Tab**
- 📝 View all clipboard items with icons (📝 text, 🖼️ image, 📁 file, 🔗 URL, etc.)
- 🔍 Search bar - Find specific clipboard items
- 🏷️ Filter dropdown - Filter by content type
- 🗑️ Clear History - Remove all items
- Click any item to copy it back to clipboard

**Devices Tab**
- 📱 Show QR - Generate QR code for mobile pairing
- 👥 Device list - See all paired devices and their status
- 🟢 Green = Connected | 🟡 Yellow = Pairing | ⚪ Gray = Offline
- Each device shows: Name, IP address, and last seen time

**Controls**
- ▶️ Start Sync / ⏸️ Pause Sync - Toggle clipboard monitoring
- Status indicator shows current state

### Desktop-to-Desktop Pairing

**Computer 1:**
```bash
python main.py
# Click "Show QR" → Copy the QR data text (long base64 string)
```

**Computer 2:**
```bash
python main.py  
# Click "Enter QR Data" tab → Paste the QR data → Click "Pair"
```

Both computers are now synced!

### Mobile Device Pairing

#### Cloud Relay (Required for Mobile) 🌐

**Why Cloud Relay?**
Mobile browsers cannot act as P2P servers, so direct local sync isn't possible. The cloud relay bridges desktop ↔ mobile communication.

**Features:**
- ✅ **Bidirectional sync** (mobile ↔ desktop)
- ✅ **Works anywhere** (no same network required)
- ✅ **FREE hosting** on Fly.io
- ✅ **Built-in protection** (won't exceed free tier)
- ✅ **Mobile PWA** (install as app on home screen)
- ✅ **Real-time sync** via WebSocket

**Quick Setup:**

**Option A - Automated (Recommended):**
```powershell
# Windows
.\deploy-cloud-relay.ps1

# Mac/Linux
chmod +x deploy-cloud-relay.sh
./deploy-cloud-relay.sh
```
The script will:
- Install Fly CLI if needed
- Authenticate with Fly.io
- Deploy the cloud relay
- Show you the app URL

**Option B - Manual:**
```bash
# 1. Install Fly CLI (if not installed)
# Windows: iwr https://fly.io/install.ps1 -useb | iex
# Mac/Linux: curl -L https://fly.io/install.sh | sh

# 2. Deploy relay server
cd cloud-relay
fly auth login
fly launch
fly deploy

# 3. Open on mobile
https://your-app.fly.dev

# 4. Enter same Room ID on desktop and mobile
```

**See full guide:** [cloud-relay/README.md](cloud-relay/README.md)

**Built-in Free Tier Protection:**
- 150MB bandwidth/month (enough for 150,000+ text syncs)
- 50 simultaneous connections max
- 60 messages per minute per device
- 100KB max message size
- Automatic monthly reset
- Real-time usage monitoring

**Note:** Desktop app integration coming soon. Currently use the mobile web app directly.

## How It Works

### System Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIPBOARD SYNC FLOW                       │
└─────────────────────────────────────────────────────────────┘

1. APPLICATION START
   ├─ Generate ECC keypair (SECP384R1)
   ├─ Start clipboard monitoring
   ├─ Start mDNS service discovery (Zeroconf)
   ├─ Start P2P server (SocketIO)
   └─ Start mobile pairing server (HTTP:8080)

2. DEVICE DISCOVERY (Automatic)
   ├─ Broadcast mDNS service "clipboard-sync._tcp"
   ├─ Listen for other devices on network
   └─ Display discovered devices in UI

3. DEVICE PAIRING
   ├─ Generate QR code with pairing data
   ├─ Exchange public keys (ECC)
   ├─ Store peer's public key
   └─ Device marked as "Paired"

4. CLIPBOARD MONITORING
   ├─ Watch system clipboard for changes
   ├─ Detect content type (text/image/file/url)
   ├─ Add to local history
   └─ Trigger sync to paired devices

5. CONTENT ENCRYPTION
   ├─ Generate random AES-256 key
   ├─ Compress content if beneficial
   ├─ Encrypt with AES-256-GCM
   ├─ Encrypt AES key for each peer (ECDH + ChaCha20)
   └─ Create encrypted bundle

6. TRANSMISSION
   ├─ Send via SocketIO (WebSocket)
   ├─ Peer receives encrypted bundle
   ├─ Automatic retry on failure
   └─ Acknowledge receipt

7. DECRYPTION & DISPLAY
   ├─ Derive shared key (ECDH)
   ├─ Decrypt AES key (ChaCha20)
   ├─ Decrypt content (AES-256-GCM)
   ├─ Verify authenticity (GCM tag)
   ├─ Decompress if needed
   ├─ Add to clipboard
   └─ Show in history
```

### Network Communication

**Ports Used:**
- `8080` - Mobile pairing HTTP server (temporary during pairing)
- `5353` - mDNS service discovery (UDP)
- `Dynamic` - P2P communication (SocketIO assigns random port)

**Protocols:**
- **mDNS** - Automatic device discovery (no configuration needed)
- **HTTP** - Mobile pairing web interface
- **WebSocket** - Real-time P2P data transfer (via SocketIO)
- **TCP** - Reliable delivery of clipboard data

## Network Requirements

⚠️ **Important**: Devices must be on the same local network without VPN interference.

**Requirements:**
- ✅ All devices on the **same Wi-Fi network**
- ✅ No VPN blocking local traffic (or VPN with local network access enabled)
- ✅ Firewall allowing Python/app network access
- ✅ Ports 8080 (pairing), 5353 (mDNS), and dynamic P2P ports not blocked

**Common Network Issues:**
- If using VPN (like Harmony SASE), add your Wi-Fi network to trusted networks
- Or temporarily disconnect VPN while using clipboard sync
- Corporate networks may block mDNS - use manual pairing instead
- Some routers have "Client Isolation" - disable it in router settings

## Security & Encryption

### 🔐 End-to-End Encryption

All clipboard data is encrypted before transmission using a hybrid encryption system:

**Encryption Methods:**
- **ECC (Elliptic Curve Cryptography)** - SECP384R1 curve for key exchange
- **AES-256-GCM** - For content encryption (industry standard)
- **ChaCha20-Poly1305** - For encrypting symmetric keys
- **ECDSA** - Digital signatures for content verification

**How It Works:**
```
1. Device Pairing
   ├─ Each device generates ECC keypair (private + public)
   ├─ Public keys exchanged during pairing (QR code or manual)
   └─ Private keys NEVER leave the device

2. Sending Clipboard Data
   ├─ Generate random AES-256 key (unique per message)
   ├─ Encrypt content with AES-256-GCM
   ├─ Derive shared secret using ECDH (your private + peer's public)
   ├─ Encrypt AES key with ChaCha20-Poly1305
   └─ Send encrypted bundle over network

3. Receiving Clipboard Data
   ├─ Derive same shared secret using ECDH
   ├─ Decrypt AES key using ChaCha20-Poly1305
   ├─ Decrypt content using AES-256-GCM
   └─ Verify authenticity with GCM authentication tag
```

**Security Features:**
- ✅ **End-to-End Encrypted** - Only paired devices can decrypt
- ✅ **Forward Secrecy** - New encryption key for each clipboard item
- ✅ **Authenticated Encryption** - GCM mode prevents tampering
- ✅ **Digital Signatures** - Verify content integrity (ECDSA)
- ✅ **Compression** - Automatic compression for text content
- ✅ **Multi-Peer Support** - Can encrypt for multiple devices simultaneously

**What's NOT Encrypted:**
- ❌ Mobile pairing page (HTTP) - Only shows during initial setup
- ❌ QR code content - Only contains IP address and port
- ❌ Device discovery (mDNS) - Service announcement broadcasts

**Note:** Once devices are paired, ALL clipboard data transfer is fully encrypted!

## Architecture

- **PyQt6** - Modern GUI framework for desktop interface
- **Zeroconf** - mDNS service discovery for automatic device detection
- **python-socketio** - WebSocket-based P2P communication
- **Cryptography** - Industry-standard encryption library (ECC, AES, ChaCha20)
- **HTTP Server** - Lightweight server for mobile device pairing

## Project Structure

```
clipboard-sync-tool/
├── core/                      # Core functionality
│   ├── __init__.py
│   ├── encryption.py          # Hybrid encryption (ECC + AES-256-GCM)
│   ├── monitor.py             # Clipboard monitoring
│   ├── network.py             # Network discovery & P2P communication
│   └── sync_engine.py         # Main sync orchestration
├── gui/                       # GUI components
│   ├── __init__.py
│   ├── main_window.py         # Main PyQt6 application window
│   ├── simple_gui.py          # Simplified fallback GUI
│   └── pairing_server.py      # HTTP server for mobile pairing
├── cloud-relay/               # Cloud relay server for mobile sync
│   ├── server.js              # Node.js relay server (Socket.IO)
│   ├── package.json           # Node.js dependencies
│   ├── Dockerfile             # Container for Fly.io deployment
│   ├── fly.toml               # Fly.io configuration
│   ├── public/
│   │   ├── index.html         # Mobile PWA interface
│   │   └── app.js             # Mobile app JavaScript
│   └── README.md              # Deployment & usage guide
├── tests/                     # Test files
│   ├── test_simple.py         # Basic clipboard tests
│   ├── test_simple_server.py  # HTTP server connectivity test
│   ├── test_pairing_server.py # Pairing server tests
│   └── test_http_response.py  # HTTP response verification
├── docs/                      # Documentation
│   ├── BUG_FIXES.md           # Bug fixes and solutions
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── MOBILE_PAIRING.md      # Mobile pairing guide
│   ├── MOBILE_TESTING.md      # Testing procedures
│   └── QUICK_START_MOBILE.md  # Quick mobile setup
├── storage/                   # Data storage
│   └── __init__.py
├── utils/                     # Utility modules
│   └── __init__.py
├── logs/                      # Application logs
├── main.py                    # Application entry point
├── verify_setup.py            # Environment verification script
├── requirements.txt           # Python dependencies
├── SETUP.md                   # Setup guide
└── README.md                  # This file
```

## Troubleshooting

### Mobile Device Can't Connect

**Problem:** Mobile browser shows "Can't reach this page" or downloads empty file

**Solutions:**
1. **VPN Issue (Most Common)**
   - Disconnect VPN completely
   - OR add your home/office Wi-Fi to VPN's trusted networks
   - Check VPN settings for "Allow Local Network Access"

2. **Network Issues**
   - Ensure mobile and desktop on SAME Wi-Fi network
   - Don't use mobile data or different network
   - Restart router if needed

3. **Firewall Blocking**
   - Windows: Allow Python through Windows Firewall
   - Check antivirus software isn't blocking connections
   - Temporarily disable firewall to test (then re-enable with exception)

4. **Wrong IP Address**
   - IP address in QR code must be your computer's local IP
   - Run `ipconfig` (Windows) or `ifconfig` (Mac/Linux) to verify
   - IP should be like `192.168.x.x` or `10.x.x.x`

**Testing Connection:**
```bash
# Test if server is accessible
python test_simple_server.py
# Then access from mobile: http://YOUR-IP:8888/
```

### Clipboard Not Syncing

**Problem:** Copy/paste not appearing on other devices

**Solutions:**
1. **Sync Not Started**
   - Click **"▶ Start Sync"** button
   - Should show "Sync engine started successfully"

2. **Devices Not Paired**
   - Check Devices tab - devices should be listed
   - Status should be green (connected)
   - Re-pair if needed

3. **Network Discovery Failed**
   - Restart the application
   - Check both devices on same network
   - Firewall might be blocking mDNS (port 5353)

4. **Encryption Key Mismatch**
   - Re-pair the devices
   - Delete old pairing data and start fresh

### Application Won't Start

**Problem:** Python errors when launching

**Solutions:**
1. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

2. **Python Version**
   - Check: `python --version` (need 3.8+)
   - Update Python if needed

3. **Virtual Environment**
   - Make sure venv is activated: `(venv)` in prompt
   - Recreate if corrupted: `python -m venv venv --clear`

### Performance Issues

**Slow Sync:**
- Large files take time (they're encrypted)
- Check network speed
- Too many clipboard items in history (clear old ones)

**High CPU Usage:**
- Normal during file transfers
- Encryption/decryption is CPU-intensive
- Pause sync when not needed

### Common Error Messages

| Error | Solution |
|-------|----------|
| `EventLoopBlocked` | Restart application - fixed in latest version |
| `Port already in use` | Another instance running - close it first |
| `No public key for device` | Re-pair devices - encryption keys lost |
| `Failed to start pairing server` | Port 8080 in use - close other apps |
| `Zeroconf timeout` | Network discovery blocked - check firewall |

## FAQ

**Q: Is my clipboard data sent to the cloud?**  
A: No! All data transfers happen directly between your devices on your local network. Nothing is sent to any server or cloud service.

**Q: Can someone intercept my clipboard data?**  
A: Very unlikely. All data is encrypted with AES-256-GCM before transmission. Even if intercepted, it's useless without the private keys that never leave your devices.

**Q: How many devices can I sync?**  
A: Unlimited! You can pair as many devices as you want. The encryption system supports multi-peer communication.

**Q: Does it work over the internet?**  
A: Yes! Use the cloud relay server. See [cloud-relay/README.md](cloud-relay/README.md) for setup. Local P2P mode requires same network.

**Q: What happens if I copy a large file?**  
A: It will sync, but may take time depending on file size and network speed. Files are compressed and encrypted before transfer.

**Q: Can I sync between Windows and Mac?**  
A: Yes! The app is cross-platform (Windows/Mac/Linux). As long as both devices run the Python app, they can sync.

**Q: Why do I need to pair devices?**  
A: Pairing exchanges encryption keys (public keys). This ensures only your devices can decrypt your clipboard data.

**Q: Will this work on public Wi-Fi?**  
A: Technically yes, but not recommended. Use your home/office network for security. Public Wi-Fi may have restrictions or isolation between devices.

**Q: Does it sync clipboard history?**  
A: Yes! All synced items are stored in the History tab. You can click any item to copy it again.

**Q: Can I exclude certain content from syncing?**  
A: Not yet, but this could be added as a filter feature in future versions.

**Q: Is there a mobile app?**  
A: Yes! Use the cloud relay web app (PWA) - works on iPhone/Android. Deploy to Fly.io (free), then open on mobile browser. See [cloud-relay/README.md](cloud-relay/README.md) for full guide. Can install to home screen like a native app!

**Q: What if my devices have the same name?**  
A: Each device gets a unique ID automatically. Names are just for display - duplicates won't cause issues.

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Test Simple Server
```bash
python tests/test_simple_server.py
```

### Verify Setup
```bash
python verify_setup.py
```

### Run All Tests
```bash
python -m pytest tests/
```

### Development Setup
```bash
# Clone repo
git clone https://github.com/Omerba31/clipboard-sync-tool.git
cd clipboard-sync-tool

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run app
python main.py
```

## License

[Add your license here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Changelog

### Version 1.0.0 (Current)
- ✅ End-to-end encryption (ECC + AES-256-GCM)
- ✅ Desktop-to-desktop sync
- ✅ Mobile device pairing via QR code
- ✅ Automatic device discovery (mDNS)
- ✅ Clipboard history with search/filter
- ✅ Multiple content types (text, images, files, URLs)
- ✅ Modern PyQt6 GUI with emoji icons
- ✅ Compression for text content
- ✅ Digital signatures for content verification

### Roadmap
- ✅ **Cloud relay for internet-based sync** - DONE! See [cloud-relay/](cloud-relay/)
- ✅ **Mobile web app (PWA)** - DONE! Works on iOS/Android via cloud relay
- 🔜 Desktop app integration with cloud relay
- 🔜 End-to-end encryption for cloud relay (currently Base64 only)
- 🔜 Native mobile app (iOS/Android) with E2E encryption
- 🔜 Exclude filters (don't sync passwords, etc.)
- 🔜 Sync selective clipboard history
- 🔜 Dark mode
- 🔜 System tray icon
- 🔜 Auto-start on boot option

## Support

If you encounter issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review [FAQ](#faq)
3. Open an issue on GitHub with:
   - Your OS and Python version
   - Error messages or logs
   - Steps to reproduce the problem

## Acknowledgments

Built with:
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework
- [Cryptography](https://cryptography.io/) - Encryption library
- [python-socketio](https://python-socketio.readthedocs.io/) - Real-time communication
- [Zeroconf](https://github.com/jstasiak/python-zeroconf) - Service discovery
