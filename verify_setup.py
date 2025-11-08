#!/usr/bin/env python3
"""
Quick verification script to check if environment is ready
"""

import sys
import subprocess

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ ERROR: Python 3.8+ required")
        return False
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required = [
        'PyQt6',
        'pyperclip',
        'python-socketio',
        'zeroconf',
        'cryptography',
        'qrcode',
        'Pillow'
    ]
    
    print("\nChecking dependencies...")
    missing = []
    
    for package in required:
        try:
            __import__(package.replace('-', '_').lower())
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ❌ {package} - NOT INSTALLED")
            missing.append(package)
    
    return len(missing) == 0, missing

def check_network():
    """Check network configuration"""
    import socket
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"\n✓ Network OK - Your IP: {local_ip}")
        return True, local_ip
    except Exception as e:
        print(f"\n❌ Network Error: {e}")
        return False, None

def main():
    print("="*60)
    print("Clipboard Sync Tool - Environment Verification")
    print("="*60)
    
    # Check Python
    if not check_python_version():
        print("\n❌ Setup incomplete - Please install Python 3.8+")
        return False
    
    # Check dependencies
    deps_ok, missing = check_dependencies()
    if not deps_ok:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("\nRun: pip install -r requirements.txt")
        return False
    
    # Check network
    net_ok, ip = check_network()
    if not net_ok:
        print("\n⚠ Warning: Network issue detected")
    
    print("\n" + "="*60)
    print("✅ READY TO RUN!")
    print("="*60)
    print("\nTo start the application:")
    print("  python main.py")
    if ip:
        print(f"\nMobile pairing URL will be: http://{ip}:8080")
    print("\n⚠ Remember: Disconnect VPN or use trusted network!")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
