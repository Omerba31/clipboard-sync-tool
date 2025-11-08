#!/usr/bin/env python3
"""
Test the pairing server independently
"""

import sys
import os
import time
import webbrowser

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from gui.pairing_server import PairingServer

# Mock sync engine for testing
class MockSyncEngine:
    def __init__(self):
        self.device_id = "test-device-123"
        self.device_name = "Test Desktop"
        self.discovery = MockDiscovery()
    
    def _pair_with_device(self, device):
        print(f"✅ Would pair with: {device.name} ({device.ip_address})")

class MockDiscovery:
    def __init__(self):
        self.local_ip = "192.168.1.100"
        self.port = 65321

def test_pairing_server():
    """Test the pairing server"""
    print("=" * 60)
    print("🧪 Testing Pairing Server")
    print("=" * 60)
    
    # Create mock sync engine
    mock_engine = MockSyncEngine()
    
    # Create and start server
    print("\n1. Creating pairing server...")
    server = PairingServer(mock_engine, port=8080)
    
    print("2. Starting server...")
    server.start(on_pair_callback=lambda dev: print(f"📱 Device paired: {dev.name}"))
    
    if server.is_running:
        print("✅ Server started successfully!")
        
        url = server.get_pairing_url()
        print(f"\n3. Pairing URL: {url}")
        print(f"   Open this URL in your mobile browser")
        
        print("\n4. Opening in default browser (for testing)...")
        try:
            webbrowser.open(url)
            print("   Browser opened!")
        except:
            print("   Could not auto-open browser")
        
        print("\n" + "=" * 60)
        print("SERVER IS RUNNING")
        print("=" * 60)
        print(f"📱 Scan QR code with your phone or visit: {url}")
        print("⏸️  Press Ctrl+C to stop the server")
        print("=" * 60)
        
        try:
            # Keep running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n5. Stopping server...")
            server.stop()
            print("✅ Server stopped")
            print("\n👋 Test complete!")
    else:
        print("❌ Failed to start server")

if __name__ == "__main__":
    test_pairing_server()
