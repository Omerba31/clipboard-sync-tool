# tests/unit/test_sync_engine.py
"""
Unit tests for sync engine functionality.
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


class TestSyncEngine:
    """Test SyncEngine class"""
    
    def test_engine_creation(self):
        """Test creating a SyncEngine instance"""
        from core.sync_engine import SyncEngine
        
        engine = SyncEngine(device_name="Test Device")
        assert engine is not None
        assert engine.device_name == "Test Device"
        assert engine.device_id is not None
    
    def test_engine_default_name(self):
        """Test engine creates default device name"""
        from core.sync_engine import SyncEngine
        
        engine = SyncEngine()
        assert engine.device_name is not None
        assert engine.device_name.startswith("Device-")
    
    def test_engine_components_initialized(self):
        """Test that engine initializes all components"""
        from core.sync_engine import SyncEngine
        
        engine = SyncEngine()
        assert engine.encryption is not None
        assert engine.monitor is not None
        assert engine.discovery is not None
        assert engine.p2p is not None
    
    def test_engine_initial_state(self):
        """Test engine initial state"""
        from core.sync_engine import SyncEngine
        
        engine = SyncEngine()
        assert engine.is_running == False
        assert engine.cloud_relay_enabled == False
        assert len(engine.paired_devices) == 0
        assert len(engine.sync_history) == 0
    
    def test_get_sync_history(self):
        """Test getting sync history"""
        from core.sync_engine import SyncEngine
        
        engine = SyncEngine()
        history = engine.get_sync_history(10)
        
        assert isinstance(history, list)
    
    def test_get_paired_devices(self):
        """Test getting paired devices"""
        from core.sync_engine import SyncEngine
        
        engine = SyncEngine()
        devices = engine.get_paired_devices()
        
        assert isinstance(devices, list)
        assert len(devices) == 0


class TestSyncSettings:
    """Test SyncSettings dataclass"""
    
    def test_default_settings(self):
        """Test default settings values"""
        from core.sync_engine import SyncSettings
        
        settings = SyncSettings()
        assert settings.auto_sync == True
        assert settings.sync_text == True
        assert settings.sync_images == True
        assert settings.sync_files == True
        assert settings.require_confirmation == False
        assert settings.max_size_mb == 10
    
    def test_custom_settings(self):
        """Test custom settings values"""
        from core.sync_engine import SyncSettings
        
        settings = SyncSettings(
            auto_sync=False,
            sync_images=False,
            max_size_mb=5
        )
        
        assert settings.auto_sync == False
        assert settings.sync_images == False
        assert settings.max_size_mb == 5
    
    def test_excluded_apps_default(self):
        """Test default excluded apps"""
        from core.sync_engine import SyncSettings
        
        settings = SyncSettings()
        assert 'password_manager' in settings.excluded_apps
        assert 'banking_app' in settings.excluded_apps


class TestQRPairing:
    """Test QR code pairing functionality"""
    
    def test_generate_pairing_qr(self):
        """Test generating QR code data"""
        from core.sync_engine import SyncEngine
        import json
        
        engine = SyncEngine()
        qr_data = engine.generate_pairing_qr()
        
        assert qr_data is not None
        
        # Parse the JSON
        data = json.loads(qr_data)
        assert 'device_id' in data
        assert 'device_name' in data
        assert 'ip' in data
        assert 'port' in data
        assert 'public_key' in data
        assert 'timestamp' in data
    
    def test_pairing_qr_contains_device_info(self):
        """Test QR data contains correct device info"""
        from core.sync_engine import SyncEngine
        import json
        
        engine = SyncEngine(device_name="My Computer")
        qr_data = engine.generate_pairing_qr()
        data = json.loads(qr_data)
        
        assert data['device_name'] == "My Computer"
        assert data['device_id'] == engine.device_id
