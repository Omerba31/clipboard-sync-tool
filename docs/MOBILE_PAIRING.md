# Mobile QR Pairing Guide

## Overview
The Clipboard Sync Tool now supports easy mobile device pairing using QR codes! This is the **primary and recommended method** for connecting your mobile devices.

## How It Works

### Architecture
1. **Desktop App** runs a lightweight HTTP server on port 8080
2. **Mobile Device** scans QR code and opens pairing page in browser
3. **Web Interface** provides a beautiful, mobile-optimized pairing experience
4. **Automatic Pairing** happens once you submit your device name

### Features
✅ **No App Installation Required** - Works with any mobile browser  
✅ **Simple QR Scanning** - Use your phone's camera app  
✅ **Beautiful UI** - Modern, responsive design  
✅ **Instant Pairing** - Connect in seconds  
✅ **Secure** - Local network only  

## Step-by-Step Guide

### On Your Desktop:
1. Open Clipboard Sync Tool
2. Click **"📱 Show QR"** button in the header
3. A dialog opens with two tabs - stay on **"📱 Show QR"** tab
4. You'll see:
   - A QR code
   - The pairing URL (e.g., `http://192.168.1.100:8080`)
   - Device information

### On Your Mobile Device:
1. Open your **Camera app** or QR scanner
2. Point camera at the QR code on your desktop screen
3. Tap the notification/link that appears
4. Your mobile browser opens the pairing page
5. Enter a name for your device (e.g., "My iPhone")
6. Tap **"🔗 Pair Devices"**
7. Wait for confirmation ✅

### Success!
- Desktop shows: "Successfully paired with [Your Device]!"
- Mobile shows: "✅ Pairing Successful! You can now close this page"
- Your devices are now connected and ready to sync!

## What You'll See on Mobile

The pairing page is beautiful and mobile-optimized:
```
📱💻
Device Pairing
Pair this device with Clipboard Sync

┌─────────────────────────────┐
│ Device Name: Desktop-PC     │
│ IP Address: 192.168.1.100   │
│ Status: 🟢 Ready to Pair    │
└─────────────────────────────┘

Your Device Name
[My iPhone              ]

[🔗 Pair Devices]
```

## Troubleshooting

### QR Code doesn't scan
- Make sure devices are on the same Wi-Fi network
- Try increasing screen brightness
- Manually type the URL shown below the QR code

### "Connection Error" on mobile
- Check firewall settings (allow port 8080)
- Verify both devices are on same network
- Try restarting the desktop app

### "Network sync not available"
- Core modules not loaded
- Check if all dependencies are installed
- See main README for installation instructions

## Technical Details

### Ports Used
- **8080**: HTTP pairing server (mobile web interface)
- **5353**: mDNS discovery (automatic device discovery)
- **Dynamic**: P2P communication port (assigned by sync engine)

### Security
- Pairing server only listens on local network (0.0.0.0)
- No external internet connection required
- All clipboard data encrypted with hybrid encryption
- Device authentication using public key cryptography

### Browser Compatibility
Works with all modern mobile browsers:
- Safari (iOS)
- Chrome (Android)
- Firefox (Android)
- Edge (Android)
- Samsung Internet

## Alternative Pairing Method

If QR scanning doesn't work, use the **"🔗 Enter QR Data"** tab:
1. On Desktop: Copy the text from info panel
2. On Mobile: Use the same pairing URL in browser
3. Manual pairing available in app settings

## Next Steps

After pairing:
1. Copy text on one device
2. It automatically appears on the other device
3. View sync history in the **"📜 History"** tab
4. Check connected devices in **"🖥️ Devices"** tab

## Demo Video
[Coming Soon]

## Feedback
Found a bug or have suggestions? Open an issue on GitHub!
