# core/encryption.py
"""
Hybrid encryption system using AES for content and ECC for key exchange.
This is completely different from the simple RSA in the chat app.
"""

import os
import json
import base64
from typing import Dict, Tuple, Optional
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
import hashlib
import secrets

class HybridEncryption:
    """
    Advanced encryption using:
    - ECC for key exchange (more efficient than RSA)
    - AES-GCM for content encryption
    - ChaCha20-Poly1305 for streaming
    """
    
    def __init__(self):
        self.backend = default_backend()
        self.private_key = None
        self.public_key = None
        self.device_id = self._generate_device_id()
        self.peer_public_keys = {}  # Store multiple peer keys
        self._generate_keypair()
    
    def _generate_device_id(self) -> str:
        """Generate unique device identifier"""
        return hashlib.sha256(
            f"{os.environ.get('COMPUTERNAME', 'unknown')}{os.getpid()}".encode()
        ).hexdigest()[:16]
    
    def _generate_keypair(self):
        """Generate ECC keypair - more efficient than RSA"""
        self.private_key = ec.generate_private_key(
            ec.SECP384R1(), 
            self.backend
        )
        self.public_key = self.private_key.public_key()
    
    def export_public_key(self) -> str:
        """Export public key for sharing with peers"""
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return base64.b64encode(pem).decode('utf-8')
    
    def import_peer_key(self, peer_id: str, public_key_b64: str):
        """Import and store peer's public key"""
        pem = base64.b64decode(public_key_b64)
        public_key = serialization.load_pem_public_key(pem, self.backend)
        self.peer_public_keys[peer_id] = public_key
    
    def encrypt_content(self, content: bytes, content_type: str = 'text') -> Dict:
        """
        Encrypt content with metadata.
        Different from chat: includes content type, compression, etc.
        """
        # Generate ephemeral symmetric key
        symmetric_key = secrets.token_bytes(32)
        
        # Compress if beneficial
        compressed = self._compress_if_needed(content, content_type)
        
        # Encrypt with AES-GCM
        cipher = Cipher(
            algorithms.AES(symmetric_key),
            modes.GCM(os.urandom(12)),
            backend=self.backend
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(compressed) + encryptor.finalize()
        
        # Encrypt symmetric key for each peer
        encrypted_keys = {}
        for peer_id, peer_key in self.peer_public_keys.items():
            shared_key = self._derive_shared_key(peer_key)
            encrypted_key = self._encrypt_symmetric_key(symmetric_key, shared_key)
            encrypted_keys[peer_id] = base64.b64encode(encrypted_key).decode()
        
        return {
            'device_id': self.device_id,
            'content_type': content_type,
            'encrypted_content': base64.b64encode(ciphertext).decode(),
            'encrypted_keys': encrypted_keys,
            'tag': base64.b64encode(encryptor.tag).decode(),
            'iv': base64.b64encode(cipher.mode.initialization_vector).decode(),
            'compressed': compressed != content
        }
    
    def decrypt_content(self, encrypted_data: Dict) -> Tuple[bytes, str]:
        """Decrypt received content"""
        # Get our encrypted key
        encrypted_key = base64.b64decode(
            encrypted_data['encrypted_keys'][self.device_id]
        )
        
        # Derive shared key with sender
        sender_id = encrypted_data['device_id']
        peer_key = self.peer_public_keys.get(sender_id)
        if not peer_key:
            raise ValueError(f"No public key for device {sender_id}")
        
        shared_key = self._derive_shared_key(peer_key)
        symmetric_key = self._decrypt_symmetric_key(encrypted_key, shared_key)
        
        # Decrypt content
        iv = base64.b64decode(encrypted_data['iv'])
        tag = base64.b64decode(encrypted_data['tag'])
        ciphertext = base64.b64decode(encrypted_data['encrypted_content'])
        
        cipher = Cipher(
            algorithms.AES(symmetric_key),
            modes.GCM(iv, tag),
            backend=self.backend
        )
        decryptor = cipher.decryptor()
        content = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Decompress if needed
        if encrypted_data.get('compressed'):
            content = self._decompress(content)
        
        return content, encrypted_data['content_type']
    
    def _derive_shared_key(self, peer_public_key) -> bytes:
        """Derive shared key using ECDH"""
        shared_key = self.private_key.exchange(
            ec.ECDH(), 
            peer_public_key
        )
        
        # Derive key using HKDF
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'clipboard-sync',
            backend=self.backend
        ).derive(shared_key)
        
        return derived_key
    
    def _encrypt_symmetric_key(self, key: bytes, shared_key: bytes) -> bytes:
        """Encrypt symmetric key with shared key"""
        cipher = ChaCha20Poly1305(shared_key)
        nonce = os.urandom(12)
        ciphertext = cipher.encrypt(nonce, key, None)
        return nonce + ciphertext
    
    def _decrypt_symmetric_key(self, encrypted: bytes, shared_key: bytes) -> bytes:
        """Decrypt symmetric key"""
        nonce = encrypted[:12]
        ciphertext = encrypted[12:]
        cipher = ChaCha20Poly1305(shared_key)
        return cipher.decrypt(nonce, ciphertext, None)
    
    def _compress_if_needed(self, content: bytes, content_type: str) -> bytes:
        """Compress content if it reduces size"""
        import zlib
        
        # Don't compress already compressed formats
        if content_type in ['image/jpeg', 'image/png', 'video', 'zip']:
            return content
        
        compressed = zlib.compress(content, level=6)
        
        # Only use compressed if smaller
        if len(compressed) < len(content) * 0.9:
            return compressed
        return content
    
    def _decompress(self, content: bytes) -> bytes:
        """Decompress content"""
        import zlib
        return zlib.decompress(content)
    
    def create_signature(self, content: bytes) -> str:
        """Create digital signature for content verification"""
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import utils
        
        chosen_hash = hashes.SHA256()
        hasher = hashes.Hash(chosen_hash)
        hasher.update(content)
        digest = hasher.finalize()
        
        signature = self.private_key.sign(
            digest,
            ec.ECDSA(utils.Prehashed(chosen_hash))
        )
        return base64.b64encode(signature).decode()
    
    def verify_signature(self, content: bytes, signature: str, peer_id: str) -> bool:
        """Verify content signature"""
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import utils
        from cryptography.exceptions import InvalidSignature
        
        peer_key = self.peer_public_keys.get(peer_id)
        if not peer_key:
            return False
        
        try:
            chosen_hash = hashes.SHA256()
            hasher = hashes.Hash(chosen_hash)
            hasher.update(content)
            digest = hasher.finalize()
            
            peer_key.verify(
                base64.b64decode(signature),
                digest,
                ec.ECDSA(utils.Prehashed(chosen_hash))
            )
            return True
        except InvalidSignature:
            return False