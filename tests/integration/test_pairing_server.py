# tests/integration/test_pairing_server.py
"""
Integration tests for pairing server functionality.
"""

import pytest
import sys
import os
import time
import threading

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


class MockDiscovery:
    """Mock discovery for testing"""
    def __init__(self):
        self.local_ip = "127.0.0.1"
        self.port = 65321


class MockSyncEngine:
    """Mock sync engine for testing"""
    def __init__(self):
        self.device_id = "test-device-123"
        self.device_name = "Test Desktop"
        self.discovery = MockDiscovery()
        self.paired_device = None
    
    def _pair_with_device(self, device):
        self.paired_device = device


@pytest.fixture
def mock_engine():
    """Create a mock sync engine"""
    return MockSyncEngine()


@pytest.fixture
def pairing_server(mock_engine):
    """Create and return a pairing server instance"""
    from gui.pairing_server import PairingServer
    
    # Use a random high port to avoid conflicts
    server = PairingServer(mock_engine, port=0)  # port=0 lets OS assign
    yield server
    # Cleanup
    if hasattr(server, 'is_running') and server.is_running:
        server.stop()


class TestPairingServerCreation:
    """Test pairing server creation"""
    
    def test_server_creation(self, mock_engine):
        """Test creating a PairingServer instance"""
        from gui.pairing_server import PairingServer
        
        server = PairingServer(mock_engine, port=8888)
        assert server is not None
        assert server.sync_engine == mock_engine
    
    def test_server_has_required_methods(self, pairing_server):
        """Test server has required methods"""
        assert hasattr(pairing_server, 'start')
        assert hasattr(pairing_server, 'stop')
        assert hasattr(pairing_server, 'get_pairing_url')


class TestPairingServerFunctionality:
    """Test pairing server functionality"""
    
    def test_server_start_stop(self, mock_engine):
        """Test starting and stopping the server"""
        from gui.pairing_server import PairingServer
        
        server = PairingServer(mock_engine, port=8889)
        paired_devices = []
        
        def on_pair(device):
            paired_devices.append(device)
        
        # Start server
        server.start(on_pair_callback=on_pair)
        time.sleep(0.5)  # Give server time to start
        
        assert server.is_running == True
        
        # Stop server
        server.stop()
        time.sleep(0.5)
        
        assert server.is_running == False
    
    def test_pairing_url_format(self, mock_engine):
        """Test pairing URL format"""
        from gui.pairing_server import PairingServer
        
        server = PairingServer(mock_engine, port=8890)
        server.start(on_pair_callback=lambda x: None)
        time.sleep(0.3)
        
        try:
            url = server.get_pairing_url()
            assert url is not None
            assert "http://" in url or "https://" in url
            assert "127.0.0.1" in url or "localhost" in url or mock_engine.discovery.local_ip in url
        finally:
            server.stop()
    
    def test_server_running_state(self, mock_engine):
        """Test server running state tracking"""
        from gui.pairing_server import PairingServer
        
        server = PairingServer(mock_engine, port=8891)
        
        # Initially not running
        assert server.is_running == False
        
        server.start(on_pair_callback=lambda x: None)
        time.sleep(0.3)
        
        try:
            assert server.is_running == True
        finally:
            server.stop()


class TestPairingServerEdgeCases:
    """Test edge cases and error handling"""
    
    def test_double_start(self, mock_engine):
        """Test calling start twice doesn't crash"""
        from gui.pairing_server import PairingServer
        
        server = PairingServer(mock_engine, port=8892)
        
        try:
            server.start(on_pair_callback=lambda x: None)
            time.sleep(0.3)
            
            # Second start should be safe
            server.start(on_pair_callback=lambda x: None)
            
            assert server.is_running == True
        finally:
            server.stop()
    
    def test_stop_without_start(self, mock_engine):
        """Test calling stop without start doesn't crash"""
        from gui.pairing_server import PairingServer
        
        server = PairingServer(mock_engine, port=8893)
        
        # Should not raise
        server.stop()
        
        assert server.is_running == False
