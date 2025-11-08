# Clipboard Sync Tool

A cross-platform clipboard synchronization tool that allows seamless clipboard sharing between devices on the same network.

## Features

- 📋 **Real-time Clipboard Sync** - Automatically sync clipboard content across devices
- 📱 **Mobile Pairing** - Easy QR code-based pairing for mobile devices
- 🔒 **Encrypted Transfer** - All clipboard data is encrypted during transfer
- 🖼️ **Multiple Content Types** - Support for text, images, files, URLs, and more
- 🎨 **Modern GUI** - Clean PyQt6-based interface with emoji icons
- 🔍 **Search & Filter** - Quickly find items in clipboard history
- 🌐 **Network Discovery** - Automatic device discovery on local network

## Requirements

- Python 3.8+
- Windows/Linux/macOS
- Local network connection

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd clipboard-sync-tool
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Desktop Application

Run the main application:
```bash
python main.py
```

### Mobile Pairing

1. Start the desktop app
2. Click **"Show QR"** button in the Devices tab
3. Scan the QR code with your mobile device
4. Enter a device name and click **"Pair Device"**

### Features

- **Clipboard History**: View and manage all synced clipboard items
- **Device Management**: See connected devices and their status
- **Content Filtering**: Search by content or filter by type (text, image, file, etc.)
- **Clear History**: Remove all clipboard history items

## Network Requirements

⚠️ **Important**: Make sure devices are on the same local network without VPN interference.

- If using VPN (like Harmony SASE), add your Wi-Fi network to trusted networks
- Or temporarily disconnect VPN while using clipboard sync
- Firewall must allow incoming connections on port 8080 (pairing) and dynamic P2P ports

## Architecture

- **PyQt6** - GUI framework
- **Zeroconf** - mDNS service discovery
- **python-socketio** - P2P communication
- **Cryptography** - End-to-end encryption
- **HTTP Server** - Mobile device pairing

## Project Structure

```
clipboard-sync-tool/
├── core/               # Core functionality
│   ├── encryption.py   # Encryption/decryption
│   ├── monitor.py      # Clipboard monitoring
│   ├── network.py      # Network discovery & P2P
│   └── sync_engine.py  # Main sync orchestration
├── gui/                # GUI components
│   ├── main_window.py  # Main application window
│   ├── simple_gui.py   # Simplified GUI
│   └── pairing_server.py # HTTP server for mobile pairing
├── tests/              # Test files
├── docs/               # Documentation
├── main.py             # Application entry point
└── requirements.txt    # Python dependencies
```

## Troubleshooting

### Mobile device can't connect
- Ensure both devices are on the same network
- Disable VPN or add network to VPN trusted list
- Check firewall settings
- Verify IP address is correct

### Clipboard not syncing
- Check if sync is enabled (toggle button)
- Verify devices are paired
- Check logs in the application

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Test Simple Server
```bash
python test_simple_server.py
```

## License

[Add your license here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
