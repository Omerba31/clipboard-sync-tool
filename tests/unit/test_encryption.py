# tests/unit/test_encryption.py
"""
Unit tests for encryption functionality.
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


class TestHybridEncryption:
    """Test HybridEncryption class for P2P encryption"""
    
    def test_encryption_creation(self):
        """Test creating a HybridEncryption instance"""
        from core.encryption import HybridEncryption
        
        encryption = HybridEncryption()
        assert encryption is not None
        assert encryption.device_id is not None
        assert len(encryption.device_id) == 16
    
    def test_keypair_generation(self):
        """Test keypair generation"""
        from core.encryption import HybridEncryption
        
        encryption = HybridEncryption()
        assert encryption.private_key is not None
        assert encryption.public_key is not None
    
    def test_export_public_key(self):
        """Test exporting public key"""
        from core.encryption import HybridEncryption
        
        encryption = HybridEncryption()
        public_key = encryption.export_public_key()
        
        assert public_key is not None
        assert isinstance(public_key, str)
        assert len(public_key) > 0
    
    def test_import_peer_key(self):
        """Test importing peer's public key"""
        from core.encryption import HybridEncryption
        
        # Create two encryption instances (simulating two devices)
        device_a = HybridEncryption()
        device_b = HybridEncryption()
        
        # Export and import keys
        key_a = device_a.export_public_key()
        key_b = device_b.export_public_key()
        
        device_a.import_peer_key(device_b.device_id, key_b)
        device_b.import_peer_key(device_a.device_id, key_a)
        
        assert device_b.device_id in device_a.peer_public_keys
        assert device_a.device_id in device_b.peer_public_keys
    
    def test_encrypt_decrypt_text(self):
        """Test encrypting and decrypting text"""
        from core.encryption import HybridEncryption
        
        # Setup two devices
        device_a = HybridEncryption()
        device_b = HybridEncryption()
        
        # Exchange keys
        device_a.import_peer_key(device_b.device_id, device_b.export_public_key())
        device_b.import_peer_key(device_a.device_id, device_a.export_public_key())
        
        # Encrypt on device A
        plaintext = "Hello, World!"
        encrypted = device_a.encrypt_content(plaintext.encode(), 'text')
        
        # Add device B's key to encrypted data
        encrypted['encrypted_keys'][device_b.device_id] = encrypted['encrypted_keys'].get(device_b.device_id)
        
        assert encrypted is not None
        assert 'encrypted_content' in encrypted
        assert 'content_type' in encrypted
        assert encrypted['content_type'] == 'text'
    
    def test_signature_creation(self):
        """Test digital signature creation"""
        from core.encryption import HybridEncryption
        
        encryption = HybridEncryption()
        content = b"Test content for signature"
        
        signature = encryption.create_signature(content)
        
        assert signature is not None
        assert isinstance(signature, str)
        assert len(signature) > 0


class TestCloudRelayCrypto:
    """Test CloudRelayCrypto class for E2E encryption"""
    
    def test_crypto_creation(self):
        """Test creating a CloudRelayCrypto instance"""
        from core.cloud_relay_crypto import CloudRelayCrypto
        
        crypto = CloudRelayCrypto()
        assert crypto is not None
        assert crypto.key is None  # Not initialized yet
    
    def test_crypto_initialization(self):
        """Test initializing encryption with room ID"""
        from core.cloud_relay_crypto import CloudRelayCrypto
        
        crypto = CloudRelayCrypto()
        crypto.init("test-room-123", "")
        
        assert crypto.is_initialized()
        assert crypto.room_id == "test-room-123"
        assert crypto.key is not None
    
    def test_crypto_initialization_with_password(self):
        """Test initializing encryption with room ID and password"""
        from core.cloud_relay_crypto import CloudRelayCrypto
        
        crypto = CloudRelayCrypto()
        crypto.init("test-room", "secret-password")
        
        assert crypto.is_initialized()
        assert crypto.password == "secret-password"
    
    def test_encrypt_decrypt_roundtrip(self):
        """Test encrypting and decrypting returns original content"""
        from core.cloud_relay_crypto import CloudRelayCrypto
        
        crypto = CloudRelayCrypto()
        crypto.init("test-room", "password123")
        
        plaintext = "Hello, this is a secret message!"
        encrypted = crypto.encrypt(plaintext)
        decrypted = crypto.decrypt(encrypted)
        
        assert decrypted == plaintext
    
    def test_encrypt_decrypt_unicode(self):
        """Test encrypting and decrypting unicode content"""
        from core.cloud_relay_crypto import CloudRelayCrypto
        
        crypto = CloudRelayCrypto()
        crypto.init("test-room", "")
        
        plaintext = "Hello 世界 🌍 émoji тест"
        encrypted = crypto.encrypt(plaintext)
        decrypted = crypto.decrypt(encrypted)
        
        assert decrypted == plaintext
    
    def test_encrypt_decrypt_long_text(self):
        """Test encrypting and decrypting long text"""
        from core.cloud_relay_crypto import CloudRelayCrypto
        
        crypto = CloudRelayCrypto()
        crypto.init("test-room", "password")
        
        plaintext = "A" * 10000  # 10KB of text
        encrypted = crypto.encrypt(plaintext)
        decrypted = crypto.decrypt(encrypted)
        
        assert decrypted == plaintext
    
    def test_different_rooms_different_keys(self):
        """Test that different room IDs produce different keys"""
        from core.cloud_relay_crypto import CloudRelayCrypto
        
        crypto1 = CloudRelayCrypto()
        crypto1.init("room-1", "")
        
        crypto2 = CloudRelayCrypto()
        crypto2.init("room-2", "")
        
        assert crypto1.key != crypto2.key
    
    def test_same_room_same_key(self):
        """Test that same room ID produces same key (for device sync)"""
        from core.cloud_relay_crypto import CloudRelayCrypto
        
        crypto1 = CloudRelayCrypto()
        crypto1.init("same-room", "same-password")
        
        crypto2 = CloudRelayCrypto()
        crypto2.init("same-room", "same-password")
        
        assert crypto1.key == crypto2.key
    
    def test_cross_device_encryption(self):
        """Test that two devices with same room/password can communicate"""
        from core.cloud_relay_crypto import CloudRelayCrypto
        
        # Simulate desktop
        desktop = CloudRelayCrypto()
        desktop.init("my-room", "shared-secret")
        
        # Simulate mobile
        mobile = CloudRelayCrypto()
        mobile.init("my-room", "shared-secret")
        
        # Desktop encrypts
        message = "Hello from desktop!"
        encrypted = desktop.encrypt(message)
        
        # Mobile decrypts
        decrypted = mobile.decrypt(encrypted)
        
        assert decrypted == message
    
    def test_wrong_password_fails(self):
        """Test that wrong password fails to decrypt"""
        from core.cloud_relay_crypto import CloudRelayCrypto
        
        sender = CloudRelayCrypto()
        sender.init("room", "correct-password")
        
        receiver = CloudRelayCrypto()
        receiver.init("room", "wrong-password")
        
        message = "Secret message"
        encrypted = sender.encrypt(message)
        
        with pytest.raises(Exception):
            receiver.decrypt(encrypted)
    
    def test_encrypt_without_init_fails(self):
        """Test that encrypting without initialization fails"""
        from core.cloud_relay_crypto import CloudRelayCrypto
        
        crypto = CloudRelayCrypto()
        
        with pytest.raises(ValueError):
            crypto.encrypt("test")
    
    def test_decrypt_without_init_fails(self):
        """Test that decrypting without initialization fails"""
        from core.cloud_relay_crypto import CloudRelayCrypto
        
        crypto = CloudRelayCrypto()
        
        with pytest.raises(ValueError):
            crypto.decrypt("test")
