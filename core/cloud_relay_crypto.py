"""
End-to-End Encryption for Cloud Relay
Uses AES-256-GCM with PBKDF2 key derivation
Compatible with the JavaScript crypto.js implementation
"""

import os
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


class CloudRelayCrypto:
    """End-to-end encryption for cloud relay clipboard sync"""
    
    def __init__(self):
        self.key = None
        self.room_id = None
        self.password = None
    
    def init(self, room_id: str, password: str = '') -> None:
        """
        Initialize encryption with room ID and optional password
        
        Args:
            room_id: The room ID (used as part of key derivation)
            password: Optional password for extra security
        """
        self.room_id = room_id
        self.password = password
        
        # Create key material from room_id + password
        key_material = (room_id + password).encode('utf-8')
        
        # Use room ID as salt (consistent across devices in same room)
        salt = f'clipboard-sync-{room_id}'.encode('utf-8')
        
        # Derive key using PBKDF2 (same parameters as JavaScript)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits for AES-256
            salt=salt,
            iterations=100000,
        )
        
        self.key = kdf.derive(key_material)
    
    def encrypt(self, content: str) -> str:
        """
        Encrypt content
        
        Args:
            content: Plain text content to encrypt
            
        Returns:
            Base64 encoded encrypted content with IV
        """
        if self.key is None:
            raise ValueError("Encryption not initialized. Call init() first.")
        
        # Generate random IV (12 bytes for GCM)
        iv = os.urandom(12)
        
        # Create cipher and encrypt
        aesgcm = AESGCM(self.key)
        data = content.encode('utf-8')
        encrypted = aesgcm.encrypt(iv, data, None)
        
        # Combine IV + encrypted data
        combined = iv + encrypted
        
        # Return as base64
        return base64.b64encode(combined).decode('utf-8')
    
    def decrypt(self, encrypted_base64: str) -> str:
        """
        Decrypt content
        
        Args:
            encrypted_base64: Base64 encoded encrypted content with IV
            
        Returns:
            Decrypted plain text
        """
        if self.key is None:
            raise ValueError("Encryption not initialized. Call init() first.")
        
        # Decode base64
        combined = base64.b64decode(encrypted_base64)
        
        # Extract IV and encrypted data
        iv = combined[:12]
        encrypted = combined[12:]
        
        # Decrypt
        aesgcm = AESGCM(self.key)
        decrypted = aesgcm.decrypt(iv, encrypted, None)
        
        return decrypted.decode('utf-8')
    
    def is_initialized(self) -> bool:
        """Check if encryption is initialized"""
        return self.key is not None


# Singleton instance
cloud_relay_crypto = CloudRelayCrypto()
