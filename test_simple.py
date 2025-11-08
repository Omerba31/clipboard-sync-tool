# test_simple.py
"""
test to verify everything is installed correctly.
Place this in the project root directory.
"""

import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing imports...")

# Test basic imports
errors = []

try:
    import pyperclip
    print("✅ pyperclip installed")
except ImportError:
    print("❌ pyperclip not installed - run: pip install pyperclip")
    errors.append("pyperclip")

try:
    import cryptography
    print("✅ cryptography installed")
except ImportError:
    print("❌ cryptography not installed - run: pip install cryptography")
    errors.append("cryptography")

try:
    from PyQt6.QtWidgets import QApplication
    print("✅ PyQt6 installed")
except ImportError:
    print("❌ PyQt6 not installed - run: pip install PyQt6")
    errors.append("PyQt6")

try:
    import zeroconf
    print("✅ zeroconf installed")
except ImportError:
    print("❌ zeroconf not installed - run: pip install zeroconf")
    errors.append("zeroconf")

try:
    import qrcode
    print("✅ qrcode installed")
except ImportError:
    print("❌ qrcode not installed - run: pip install qrcode")
    errors.append("qrcode")

try:
    import loguru
    print("✅ loguru installed")
except ImportError:
    print("❌ loguru not installed - run: pip install loguru")
    errors.append("loguru")

# Test local modules
print("\nTesting local modules...")

try:
    from core.encryption import HybridEncryption
    print("✅ Encryption module works")
except Exception as e:
    print(f"❌ Encryption module error: {e}")
    errors.append("encryption module")

try:
    from core.monitor import ClipboardMonitor
    print("✅ Monitor module works")
except Exception as e:
    print(f"❌ Monitor module error: {e}")
    errors.append("monitor module")

# Test clipboard access
print("\nTesting clipboard access...")
if "pyperclip" not in errors:
    try:
        import pyperclip
        pyperclip.copy("Test clipboard")
        result = pyperclip.paste()
        if result == "Test clipboard":
            print("✅ Clipboard read/write works")
        else:
            print("❌ Clipboard access issue")
    except Exception as e:
        print(f"❌ Clipboard error: {e}")
else:
    print("⏭️ Skipping clipboard test (pyperclip not installed)")

if not errors:
    print("\n✅ All tests passed! You can now run the application.")
    print("\nTo run the GUI: python main.py")
    print("To test simple clipboard monitor: python gui/simple_gui.py")
else:
    print(f"\n❌ Some modules are missing: {', '.join(errors)}")
    print("\nRun this command to install all requirements:")
    print("pip install pyperclip cryptography PyQt6 zeroconf qrcode pillow loguru colorama aiohttp python-socketio")