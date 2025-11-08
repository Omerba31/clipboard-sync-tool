# Setup Guide for New Computer

Follow these steps to set up the clipboard sync tool on a new computer:

## Step 1: Verify Python Installation

Check if Python 3.8+ is installed:
```bash
python --version
```

If not installed, download from: https://www.python.org/downloads/

## Step 2: Create Virtual Environment

```bash
python -m venv venv
```

## Step 3: Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

**Note:** If you get execution policy error on Windows PowerShell:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 5: Verify Installation

Check if all packages are installed:
```bash
pip list
```

You should see:
- PyQt6
- pyperclip
- python-socketio
- zeroconf
- cryptography
- qrcode
- Pillow

## Step 6: Run the Application

```bash
python main.py
```

## Step 7: Test Mobile Pairing (Without VPN!)

1. Make sure you're **NOT connected to VPN** (or on trusted network)
2. Both devices should be on the **same Wi-Fi network**
3. In the app, click **"Show QR"** in the Devices tab
4. Scan the QR code from your mobile device
5. Enter device name and click "Pair Device"

## Troubleshooting

### Issue: Can't access server from mobile
- ✅ Disconnect VPN
- ✅ Check both devices on same Wi-Fi
- ✅ Check Windows Firewall allows Python
- ✅ Verify IP address is correct

### Issue: Module not found
```bash
pip install -r requirements.txt --force-reinstall
```

### Issue: Virtual environment not activating
- Use correct command for your shell (PowerShell vs CMD)
- Check execution policy on Windows

### Test Basic Server
Run this to test if server works:
```bash
python test_simple_server.py
```
Then access from phone: `http://YOUR-IP:8888/`

## Quick Verification Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created
- [ ] Virtual environment activated (see `(venv)` in prompt)
- [ ] All dependencies installed
- [ ] No VPN blocking connections
- [ ] Both devices on same network
- [ ] Application runs without errors
