# Pairing Guide

## Cloud Relay (Mobile ↔ Desktop)

Best for: Mobile devices, different networks

1. Desktop: Click **☁️ Cloud Relay**, enter URL, Room ID, and optional password
2. Mobile: Open same URL in browser, enter same Room ID and password
3. Done! Devices sync via cloud (encrypted)

## Local P2P (Desktop ↔ Desktop)

Best for: Same network, encrypted sync

### Via QR Code
1. Computer A: Click **📱 Local P2P** → Show QR tab
2. Computer B: Click **📱 Local P2P** → Enter QR Data tab
3. Paste QR data, click Pair

### Automatic Discovery
Devices on the same WiFi network appear automatically in the Devices tab.

## Security

| Mode | Encryption | Best For |
|------|------------|----------|
| Cloud Relay | ✅ AES-256-GCM | All data (E2E encrypted) |
| Local P2P | ✅ ECC + AES-256-GCM | Sensitive data |

**Both modes use end-to-end encryption.** Add an encryption password in the connection dialog for extra security.
