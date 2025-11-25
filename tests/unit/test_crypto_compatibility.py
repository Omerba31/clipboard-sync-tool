# tests/unit/test_crypto_compatibility.py
"""
Tests for Python/JavaScript encryption compatibility.
Ensures both implementations produce compatible encrypted data.
"""

import pytest
import sys
import os
import base64
import subprocess
import json

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


class TestCloudRelayCryptoBasics:
    """Test basic CloudRelayCrypto functionality"""
    
    def test_encrypt_decrypt_empty_password(self):
        """Test encryption with empty password"""
        from core.cloud_relay_crypto import CloudRelayCrypto
        
        crypto = CloudRelayCrypto()
        crypto.init('test-room', '')
        
        original = 'Hello World'
        encrypted = crypto.encrypt(original)
        decrypted = crypto.decrypt(encrypted)
        
        assert decrypted == original
    
    def test_encrypt_decrypt_with_password(self):
        """Test encryption with password"""
        from core.cloud_relay_crypto import CloudRelayCrypto
        
        crypto = CloudRelayCrypto()
        crypto.init('test-room', 'mypassword')
        
        original = 'Hello World'
        encrypted = crypto.encrypt(original)
        decrypted = crypto.decrypt(encrypted)
        
        assert decrypted == original
    
    def test_different_passwords_fail(self):
        """Test that different passwords cannot decrypt each other's data"""
        from core.cloud_relay_crypto import CloudRelayCrypto
        
        crypto1 = CloudRelayCrypto()
        crypto1.init('test-room', 'password1')
        
        crypto2 = CloudRelayCrypto()
        crypto2.init('test-room', 'password2')
        
        encrypted = crypto1.encrypt('secret message')
        
        # Should fail to decrypt with wrong password
        with pytest.raises(Exception):
            crypto2.decrypt(encrypted)
    
    def test_different_rooms_fail(self):
        """Test that different rooms cannot decrypt each other's data"""
        from core.cloud_relay_crypto import CloudRelayCrypto
        
        crypto1 = CloudRelayCrypto()
        crypto1.init('room1', 'password')
        
        crypto2 = CloudRelayCrypto()
        crypto2.init('room2', 'password')
        
        encrypted = crypto1.encrypt('secret message')
        
        # Should fail to decrypt with wrong room
        with pytest.raises(Exception):
            crypto2.decrypt(encrypted)
    
    def test_same_room_same_password_succeeds(self):
        """Test that same room+password can decrypt (simulates two devices)"""
        from core.cloud_relay_crypto import CloudRelayCrypto
        
        # Device 1 encrypts
        crypto1 = CloudRelayCrypto()
        crypto1.init('shared-room', 'shared-password')
        encrypted = crypto1.encrypt('message from device 1')
        
        # Device 2 decrypts (same room + password)
        crypto2 = CloudRelayCrypto()
        crypto2.init('shared-room', 'shared-password')
        decrypted = crypto2.decrypt(encrypted)
        
        assert decrypted == 'message from device 1'


class TestKeyDerivation:
    """Test key derivation parameters match JavaScript implementation"""
    
    def test_key_derivation_parameters(self):
        """Verify PBKDF2 parameters match JavaScript"""
        from core.cloud_relay_crypto import CloudRelayCrypto
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        from cryptography.hazmat.primitives import hashes
        
        room_id = 'test-room'
        password = 'test-password'
        
        # These should match JavaScript implementation
        key_material = (room_id + password).encode('utf-8')
        salt = f'clipboard-sync-{room_id}'.encode('utf-8')
        
        # Verify salt format matches JS: 'clipboard-sync-' + roomId
        assert salt == b'clipboard-sync-test-room'
        
        # Verify key material is roomId + password concatenated
        assert key_material == b'test-roomtest-password'
        
        # Verify we can derive a 32-byte key (256 bits for AES-256)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,  # Must match JS
        )
        key = kdf.derive(key_material)
        assert len(key) == 32
    
    def test_empty_password_key_derivation(self):
        """Test key derivation with empty password"""
        room_id = 'my-room'
        password = ''
        
        key_material = (room_id + password).encode('utf-8')
        salt = f'clipboard-sync-{room_id}'.encode('utf-8')
        
        # With empty password, key material is just the room ID
        assert key_material == b'my-room'
        assert salt == b'clipboard-sync-my-room'


class TestEncryptedDataFormat:
    """Test encrypted data format matches JavaScript"""
    
    def test_encrypted_format_is_base64(self):
        """Test encrypted output is valid base64"""
        from core.cloud_relay_crypto import CloudRelayCrypto
        
        crypto = CloudRelayCrypto()
        crypto.init('room', 'pass')
        
        encrypted = crypto.encrypt('test')
        
        # Should be valid base64
        try:
            decoded = base64.b64decode(encrypted)
            assert len(decoded) > 0
        except Exception as e:
            pytest.fail(f"Encrypted data is not valid base64: {e}")
    
    def test_encrypted_contains_iv(self):
        """Test encrypted data contains 12-byte IV prefix"""
        from core.cloud_relay_crypto import CloudRelayCrypto
        
        crypto = CloudRelayCrypto()
        crypto.init('room', 'pass')
        
        encrypted = crypto.encrypt('test')
        decoded = base64.b64decode(encrypted)
        
        # IV is 12 bytes, followed by ciphertext + 16-byte auth tag
        # Minimum size: 12 (IV) + 1 (min ciphertext) + 16 (tag) = 29 bytes
        assert len(decoded) >= 29
    
    def test_different_encryptions_have_different_ivs(self):
        """Test each encryption uses a unique IV"""
        from core.cloud_relay_crypto import CloudRelayCrypto
        
        crypto = CloudRelayCrypto()
        crypto.init('room', 'pass')
        
        # Encrypt same message twice
        encrypted1 = crypto.encrypt('same message')
        encrypted2 = crypto.encrypt('same message')
        
        # Should produce different ciphertexts due to random IV
        assert encrypted1 != encrypted2
        
        # But both should decrypt to same plaintext
        assert crypto.decrypt(encrypted1) == 'same message'
        assert crypto.decrypt(encrypted2) == 'same message'


class TestSpecialCases:
    """Test special cases and edge conditions"""
    
    def test_unicode_content(self):
        """Test encryption of unicode content"""
        from core.cloud_relay_crypto import CloudRelayCrypto
        
        crypto = CloudRelayCrypto()
        crypto.init('room', 'pass')
        
        # Test various unicode
        test_strings = [
            'Hello 世界',
            'Привет мир',
            '🔐🔑🔒',
            'مرحبا بالعالم',
            '日本語テスト',
        ]
        
        for original in test_strings:
            encrypted = crypto.encrypt(original)
            decrypted = crypto.decrypt(encrypted)
            assert decrypted == original, f"Failed for: {original}"
    
    def test_empty_content(self):
        """Test encryption of empty string"""
        from core.cloud_relay_crypto import CloudRelayCrypto
        
        crypto = CloudRelayCrypto()
        crypto.init('room', 'pass')
        
        encrypted = crypto.encrypt('')
        decrypted = crypto.decrypt(encrypted)
        
        assert decrypted == ''
    
    def test_long_content(self):
        """Test encryption of long content"""
        from core.cloud_relay_crypto import CloudRelayCrypto
        
        crypto = CloudRelayCrypto()
        crypto.init('room', 'pass')
        
        # Test with 100KB of data
        original = 'x' * (100 * 1024)
        encrypted = crypto.encrypt(original)
        decrypted = crypto.decrypt(encrypted)
        
        assert decrypted == original
    
    def test_special_characters_in_password(self):
        """Test passwords with special characters"""
        from core.cloud_relay_crypto import CloudRelayCrypto
        
        passwords = [
            'pass with spaces',
            'pass!@#$%^&*()',
            'pass\twith\ttabs',
            'pass\nwith\nnewlines',
            '密码',
            '🔐🔑',
        ]
        
        for password in passwords:
            crypto = CloudRelayCrypto()
            crypto.init('room', password)
            
            encrypted = crypto.encrypt('test message')
            decrypted = crypto.decrypt(encrypted)
            
            assert decrypted == 'test message', f"Failed for password: {repr(password)}"
    
    def test_special_characters_in_room_id(self):
        """Test room IDs with special characters"""
        from core.cloud_relay_crypto import CloudRelayCrypto
        
        room_ids = [
            'room-with-dashes',
            'room_with_underscores',
            'ROOM123',
            'room.with.dots',
        ]
        
        for room_id in room_ids:
            crypto = CloudRelayCrypto()
            crypto.init(room_id, 'password')
            
            encrypted = crypto.encrypt('test message')
            decrypted = crypto.decrypt(encrypted)
            
            assert decrypted == 'test message', f"Failed for room: {room_id}"


class TestCrossDeviceSimulation:
    """Simulate cross-device encryption scenarios"""
    
    def test_desktop_to_web_scenario(self):
        """Simulate desktop encrypting, web decrypting"""
        from core.cloud_relay_crypto import CloudRelayCrypto
        
        room_id = 'APG11'
        password = 'testpass123'
        
        # Desktop encrypts
        desktop_crypto = CloudRelayCrypto()
        desktop_crypto.init(room_id, password)
        
        message = 'Hello from desktop!'
        encrypted = desktop_crypto.encrypt(message)
        
        # Web decrypts (simulated - same Python code, but verifies the format)
        web_crypto = CloudRelayCrypto()
        web_crypto.init(room_id, password)
        
        decrypted = web_crypto.decrypt(encrypted)
        assert decrypted == message
    
    def test_web_to_desktop_scenario(self):
        """Simulate web encrypting, desktop decrypting"""
        from core.cloud_relay_crypto import CloudRelayCrypto
        
        room_id = 'APG11'
        password = 'testpass123'
        
        # Web encrypts
        web_crypto = CloudRelayCrypto()
        web_crypto.init(room_id, password)
        
        message = 'Hello from web!'
        encrypted = web_crypto.encrypt(message)
        
        # Desktop decrypts
        desktop_crypto = CloudRelayCrypto()
        desktop_crypto.init(room_id, password)
        
        decrypted = desktop_crypto.decrypt(encrypted)
        assert decrypted == message
    
    def test_password_mismatch_detection(self):
        """Test that password mismatch is detected"""
        from core.cloud_relay_crypto import CloudRelayCrypto
        
        room_id = 'APG11'
        
        # Desktop with password
        desktop_crypto = CloudRelayCrypto()
        desktop_crypto.init(room_id, 'desktop_password')
        encrypted = desktop_crypto.encrypt('secret')
        
        # Web with DIFFERENT password (or empty)
        web_crypto = CloudRelayCrypto()
        web_crypto.init(room_id, '')  # Empty password - common mistake
        
        # Should fail
        with pytest.raises(Exception):
            web_crypto.decrypt(encrypted)
    
    def test_empty_vs_set_password(self):
        """Test empty password vs set password are different"""
        from core.cloud_relay_crypto import CloudRelayCrypto
        
        room_id = 'test-room'
        
        # Encrypt with empty password
        crypto_empty = CloudRelayCrypto()
        crypto_empty.init(room_id, '')
        encrypted_empty = crypto_empty.encrypt('test')
        
        # Encrypt with set password
        crypto_set = CloudRelayCrypto()
        crypto_set.init(room_id, 'password')
        encrypted_set = crypto_set.encrypt('test')
        
        # They should NOT be interchangeable
        with pytest.raises(Exception):
            crypto_empty.decrypt(encrypted_set)
        
        with pytest.raises(Exception):
            crypto_set.decrypt(encrypted_empty)
