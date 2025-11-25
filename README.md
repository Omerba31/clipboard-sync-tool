# 📋 Clipboard Sync Tool

Sync your clipboard between desktop and mobile devices - copy on one, paste on another instantly.

## Features

- **Cloud Sync** - Sync between desktop and mobile via cloud relay (works anywhere)
- **Local P2P** - Encrypted desktop-to-desktop sync on same network
- **End-to-End Encryption** - AES-256-GCM encryption, server never sees plaintext
- **Bidirectional** - Send and receive clipboard in both directions
- **Images** - Support for images up to 5MB
- **Cross-Platform** - Desktop (Windows/Mac/Linux) + Mobile (any browser)

---

## Quick Start

### 1. Install

```bash
git clone https://github.com/Omerba31/clipboard-sync-tool.git
cd clipboard-sync-tool

# Windows
.\scripts\install.ps1

# Mac/Linux
chmod +x scripts/install.sh && ./scripts/install.sh
```

### 2. Run

```bash
python main.py
```

### 3. Connect Mobile

1. Click **☁️ Cloud Relay** in the app
2. Enter your server URL (auto-filled if deployed) or use: `https://clipboard-sync-tool-production.up.railway.app`
3. Enter a Room ID (e.g., `my-room-123`)
4. Open the same URL on mobile, enter the same Room ID
5. Start syncing!

---

## How It Works

### Cloud Relay (Desktop ↔ Mobile)

```
Desktop → Cloud Server → Mobile
         (Room ID)
```

- Open cloud relay URL on mobile browser
- Same Room ID = same sync group
- Works over internet (no same WiFi needed)

### Local P2P (Desktop ↔ Desktop)

```
Computer A ←→ Computer B
   (encrypted, same network)
```

- Click **📱 Local P2P** → Show QR
- Other computer scans/enters QR data
- End-to-end encrypted, no cloud needed

---

## Security

| Mode | Encryption | Data Path |
|------|------------|-----------|
| **Local P2P** | ✅ ECC + AES-256-GCM | Device to device only |
| **Cloud Relay** | ✅ AES-256-GCM | Through cloud server (encrypted) |

**Both modes use end-to-end encryption:**
- Server never sees your plaintext data
- AES-256-GCM encryption
- Key derived from Room ID + optional password
- Devices with the same password can decrypt each other's messages (different passwords = separate encryption groups in the same room)

**Local P2P extra features:**
- ECDH key exchange via QR code
- Forward secrecy per message
- Data never leaves your network

📖 See [docs/ENCRYPTION.md](docs/ENCRYPTION.md) for detailed encryption documentation.

---

## Deploy Your Own Cloud Relay

Free deployment to Railway.app ($5 credit/month):

### Option 1: CLI (Recommended)

```bash
# Windows
.\scripts\deploy.ps1

# Mac/Linux
chmod +x scripts/deploy.sh && ./scripts/deploy.sh
```

### Option 2: Web Dashboard

1. Go to https://railway.app/new
2. Deploy from GitHub → select this repo
3. Set Root Directory to `cloud-relay`
4. Click Generate Domain

See [cloud-relay/README.md](cloud-relay/README.md) for details.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Mobile won't connect | Check Room ID matches exactly |
| Desktop says connected but no sync | Click "Test Sync" button |
| Decryption failed error | Ensure same password on both devices |
| P2P devices not found | Both must be on same WiFi |
| App won't start | Run `pip install -r requirements.txt` |
| pytest Access Denied (Windows) | Use `python -m pytest` instead of `pytest` |

---

## Testing

Run the test suite with pytest:

```bash
# Windows (use python -m to avoid permission issues)
python -m pytest tests/ -v

# Mac/Linux
pytest tests/ -v

# Run specific test file
python -m pytest tests/unit/test_encryption.py -v

# Run with coverage
python -m pytest tests/ --cov=core --cov-report=html
```

### Test Categories

| Category | Tests | Description |
|----------|-------|-------------|
| **Unit** | `tests/unit/` | Core encryption, sync engine, clipboard |
| **Integration** | `tests/integration/` | Pairing server, HTTP endpoints |
| **Crypto Compatibility** | `test_crypto_compatibility.py` | Python ↔ JavaScript encryption |

---

## Project Structure

```
clipboard-sync-tool/
├── main.py              # Entry point
├── core/                # Sync engine, encryption, networking
│   ├── cloud_relay_client.py
│   ├── cloud_relay_crypto.py
│   ├── encryption.py
│   ├── monitor.py
│   ├── network.py
│   └── sync_engine.py
├── gui/                 # Desktop UI (PyQt6)
│   ├── main_window.py
│   ├── pairing_server.py
│   ├── styles.py
│   └── widgets.py
├── cloud-relay/         # Node.js relay server + mobile PWA
├── scripts/             # Installation and deployment scripts
├── docs/                # Documentation
└── tests/               # Unit and integration tests
    ├── unit/            # Core component tests
    └── integration/     # Server and API tests
```

---

## Requirements

- **Python 3.10+**
- **PyQt6** - Desktop GUI
- **Node.js 18+** - Cloud relay server (for deployment only)

### Python Dependencies

```
PyQt6, cryptography, pyperclip, pillow, qrcode, socketio, loguru
```

Install all with: `pip install -r requirements.txt`

---

## License

MIT

## Contributing

PRs welcome! Open an issue first for major changes.
