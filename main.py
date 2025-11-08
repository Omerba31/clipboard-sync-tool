# main.py
"""
main entry point with better error handling and fallbacks.
"""

import sys
import os
import argparse

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try to import logger, but provide fallback if not available
try:
    from loguru import logger
    LOGURU_AVAILABLE = True
except ImportError:
    LOGURU_AVAILABLE = False
    # Create a simple logger replacement
    class SimpleLogger:
        def info(self, msg): print(f"[INFO] {msg}")
        def error(self, msg): print(f"[ERROR] {msg}")
        def warning(self, msg): print(f"[WARNING] {msg}")
        def debug(self, msg): print(f"[DEBUG] {msg}")
        def remove(self): pass
        def add(self, *args, **kwargs): pass
    
    logger = SimpleLogger()

def setup_logging(debug: bool = False):
    """Configure logging"""
    if LOGURU_AVAILABLE:
        level = "DEBUG" if debug else "INFO"
        logger.remove()  # Remove default handler
        
        # Console logging
        logger.add(
            sys.stderr,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
            level=level
        )
        
        # File logging
        os.makedirs('logs', exist_ok=True)
        logger.add(
            "logs/clipboard_sync.log",
            rotation="10 MB",
            retention="7 days",
            level="DEBUG"
        )
    else:
        print("[WARNING] Loguru not installed, using simple logging")

def check_dependencies():
    """Check if required dependencies are installed"""
    missing = []
    
    required_packages = {
        'PyQt6': 'PyQt6',
        'pyperclip': 'pyperclip',
        'cryptography': 'cryptography',
        'zeroconf': 'zeroconf',
        'qrcode': 'qrcode',
        'PIL': 'pillow',
        'loguru': 'loguru'
    }
    
    for module, package in required_packages.items():
        try:
            if module == 'PyQt6':
                from PyQt6.QtWidgets import QApplication
            else:
                __import__(module)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("=" * 60)
        print("Missing required packages!")
        print("=" * 60)
        print("\nThe following packages need to be installed:")
        for pkg in missing:
            print(f"  - {pkg}")
        print("\nRun this command to install all requirements:")
        print(f"\npip install {' '.join(missing)}")
        print("\nOr install all requirements at once:")
        print("pip install pyperclip cryptography PyQt6 zeroconf qrcode pillow loguru colorama aiohttp python-socketio")
        print("=" * 60)
        return False
    return True

def run_gui():
    """Run the GUI application"""
    try:
        from PyQt6.QtWidgets import QApplication
    except ImportError:
        print("[ERROR] PyQt6 not installed. Run: pip install PyQt6")
        return
    
    # Import the main window
    try:
        from gui.main_window import MainWindow
        print("[INFO] Loading GUI...")
    except ImportError as e:
        print(f"[ERROR] Could not load main_window.py: {e}")
        print("[ERROR] Make sure all dependencies are installed: pip install -r requirements.txt")
        return
    
    app = QApplication(sys.argv)
    app.setApplicationName("Clipboard Sync Tool")
    app.setApplicationDisplayName("Clipboard Sync")
    
    # Set application style
    app.setStyle('Fusion')
    
    try:
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"[ERROR] Failed to start GUI: {e}")
        import traceback
        traceback.print_exc()

def run_cli(args):
    """Run in CLI mode (headless)"""
    try:
        from core.sync_engine import SyncEngine
        import time
    except ImportError as e:
        print(f"[ERROR] Could not import sync engine: {e}")
        print("[INFO] CLI mode requires all core modules to be working")
        return
    
    logger.info("Starting Clipboard Sync in CLI mode...")
    
    # Create sync engine
    engine = SyncEngine(device_name=args.name)
    
    try:
        # Start engine
        engine.start()
        logger.info(f"Device ID: {engine.device_id}")
        logger.info(f"Device Name: {engine.device_name}")
        logger.info("Press Ctrl+C to stop...")
        
        # Keep running
        while True:
            time.sleep(1)
            
            # Print status every 30 seconds
            if int(time.time()) % 30 == 0:
                devices = engine.get_paired_devices()
                logger.info(f"Connected devices: {len(devices)}")
                
    except KeyboardInterrupt:
        logger.info("Stopping...")
        engine.stop()
        logger.info("Stopped successfully")
    except Exception as e:
        logger.error(f"Error in CLI mode: {e}")

def run_simple_test():
    """Run a simple clipboard monitor without network features"""
    print("[INFO] Running simple clipboard monitor...")
    print("[INFO] This mode only monitors your local clipboard")
    
    try:
        import pyperclip
        import time
        from datetime import datetime
    except ImportError:
        print("[ERROR] pyperclip is required. Run: pip install pyperclip")
        return
    
    print("[INFO] Monitoring clipboard... Press Ctrl+C to stop")
    last_text = ""
    
    try:
        while True:
            try:
                current = pyperclip.paste()
                if current != last_text:
                    last_text = current
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}] Clipboard changed: {current[:50]}...")
            except Exception as e:
                print(f"[ERROR] Clipboard error: {e}")
            
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Stopped monitoring")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Clipboard Sync Tool')
    parser.add_argument(
        '--mode', 
        choices=['gui', 'cli', 'simple'], 
        default='gui',
        help='Run mode (default: gui, simple: basic clipboard monitor)'
    )
    parser.add_argument(
        '--name',
        default=None,
        help='Device name for identification'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check dependencies and exit'
    )
    
    args = parser.parse_args()
    
    # Check dependencies
    if args.check or not check_dependencies():
        if args.check:
            print("\n[INFO] All dependencies are installed!")
        return
    
    # Setup logging
    setup_logging(args.debug)
    
    # Run in selected mode
    if args.mode == 'gui':
        run_gui()
    elif args.mode == 'cli':
        run_cli(args)
    elif args.mode == 'simple':
        run_simple_test()

if __name__ == '__main__':
    main()