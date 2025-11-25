# 📋 Clipboard Sync Tool

Sync your clipboard between desktop and mobile devices - copy on one, paste on another instantly.

## Features

- **Cloud Sync** - Sync between desktop and mobile via cloud relay (works anywhere)
- **Local P2P** - Encrypted desktop-to-desktop sync on same network
- **Bidirectional** - Send and receive clipboard in both directions
- **Images** - Support for images up to 5MB

---

## Quick Start

### 1. Install

```bash
git clone https://github.com/Omerba31/clipboard-sync-tool.git
cd clipboard-sync-tool

# Windows
.\install.ps1

# Mac/Linux
./install.sh
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
| **Cloud Relay** | ⚠️ Base64 only | Through cloud server |

**Local P2P encryption details:**
- ECDH key exchange via QR code
- AES-256-GCM for content
- Forward secrecy per message
- Data never leaves your network

**Cloud relay:** Use unique Room IDs. Don't sync sensitive data.

---

## Deploy Your Own Cloud Relay

Free deployment to Railway.app ($5 credit/month):

### Option 1: CLI (Recommended)

```bash
# Windows
.\deploy.ps1

# Mac/Linux
chmod +x deploy.sh && ./deploy.sh
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
| P2P devices not found | Both must be on same WiFi |
| App won't start | Run `pip install -r requirements.txt` |

---

## Project Structure

```
clipboard-sync-tool/
├── main.py              # Entry point
├── core/                # Sync engine, encryption, networking
├── gui/                 # Desktop UI (PyQt6)
├── cloud-relay/         # Node.js relay server + mobile PWA
└── tests/               # Unit and integration tests
```

---

## License

MIT

## Contributing

PRs welcome! Open an issue first for major changes.
