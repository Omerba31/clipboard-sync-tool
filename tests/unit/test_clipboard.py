# tests/unit/test_clipboard.py
"""
Unit tests for clipboard monitoring functionality.
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


class TestImports:
    """Test that all required packages are installed"""
    
    def test_pyperclip_import(self):
        """Test pyperclip is installed"""
        import pyperclip
        assert pyperclip is not None
    
    def test_cryptography_import(self):
        """Test cryptography is installed"""
        import cryptography
        assert cryptography is not None
    
    def test_pyqt6_import(self):
        """Test PyQt6 is installed"""
        from PyQt6.QtWidgets import QApplication
        assert QApplication is not None
    
    def test_zeroconf_import(self):
        """Test zeroconf is installed"""
        import zeroconf
        assert zeroconf is not None
    
    def test_qrcode_import(self):
        """Test qrcode is installed"""
        import qrcode
        assert qrcode is not None
    
    def test_loguru_import(self):
        """Test loguru is installed"""
        import loguru
        assert loguru is not None
    
    def test_pillow_import(self):
        """Test Pillow is installed"""
        from PIL import Image
        assert Image is not None
    
    def test_socketio_import(self):
        """Test python-socketio is installed"""
        import socketio
        assert socketio is not None


class TestCoreModules:
    """Test that core modules can be imported"""
    
    def test_encryption_module(self):
        """Test encryption module imports"""
        from core.encryption import HybridEncryption
        assert HybridEncryption is not None
    
    def test_monitor_module(self):
        """Test monitor module imports"""
        from core.monitor import ClipboardMonitor, ContentType
        assert ClipboardMonitor is not None
        assert ContentType is not None
    
    def test_sync_engine_module(self):
        """Test sync engine module imports"""
        from core.sync_engine import SyncEngine
        assert SyncEngine is not None
    
    def test_cloud_relay_client_module(self):
        """Test cloud relay client module imports"""
        from core.cloud_relay_client import CloudRelayClient
        assert CloudRelayClient is not None
    
    def test_cloud_relay_crypto_module(self):
        """Test cloud relay crypto module imports"""
        from core.cloud_relay_crypto import CloudRelayCrypto
        assert CloudRelayCrypto is not None


class TestClipboardMonitor:
    """Test ClipboardMonitor class"""
    
    def test_monitor_creation(self):
        """Test creating a ClipboardMonitor instance"""
        from core.monitor import ClipboardMonitor
        
        monitor = ClipboardMonitor(device_id="test-device")
        assert monitor is not None
        assert monitor.device_id == "test-device"
    
    def test_content_type_enum(self):
        """Test ContentType enum values"""
        from core.monitor import ContentType
        
        assert ContentType.TEXT.value == "text"
        assert ContentType.IMAGE.value == "image"
        assert ContentType.URL.value == "url"
        assert ContentType.CODE.value == "code"
    
    def test_monitor_history(self):
        """Test monitor history is empty initially"""
        from core.monitor import ClipboardMonitor
        
        monitor = ClipboardMonitor(device_id="test-device")
        history = monitor.get_history(10)
        assert isinstance(history, list)
        assert len(history) == 0
    
    def test_clear_history(self):
        """Test clearing monitor history"""
        from core.monitor import ClipboardMonitor
        
        monitor = ClipboardMonitor(device_id="test-device")
        monitor.clear_history()
        assert len(monitor.history) == 0


class TestClipboardAccess:
    """Test clipboard read/write operations"""
    
    def test_clipboard_write_read(self):
        """Test writing and reading from clipboard"""
        import pyperclip
        
        test_text = "pytest clipboard test"
        pyperclip.copy(test_text)
        result = pyperclip.paste()
        assert result == test_text
    
    def test_clipboard_unicode(self):
        """Test clipboard with unicode characters"""
        import pyperclip
        
        test_text = "Hello 世界 🌍 émoji"
        pyperclip.copy(test_text)
        result = pyperclip.paste()
        assert result == test_text
    
    def test_clipboard_multiline(self):
        """Test clipboard with multiline text"""
        import pyperclip
        
        test_text = "Line 1\nLine 2\nLine 3"
        pyperclip.copy(test_text)
        result = pyperclip.paste()
        assert result == test_text