"""Encryption utilities for secure data storage."""

import base64
import secrets
from typing import str as String
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class EncryptionService:
    """Service for encrypting and decrypting memory content."""
    
    def __init__(self, key: String):
        """Initialize encryption service with key."""
        self._cipher_suite = self._create_cipher_suite(key)
    
    def _create_cipher_suite(self, key: String) -> Fernet:
        """Create cipher suite from key."""
        if isinstance(key, str):
            key = key.encode()
        
        # Use PBKDF2 to derive a proper key from the input
        salt = b'memorylink_salt_2024'  # Static salt for consistency
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        derived_key = base64.urlsafe_b64encode(kdf.derive(key))
        return Fernet(derived_key)
    
    def encrypt(self, data: String) -> String:
        """Encrypt string data."""
        if not data:
            return data
        
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            encrypted_data = self._cipher_suite.encrypt(data)
            return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
        
        except Exception as e:
            raise ValueError(f"Encryption failed: {str(e)}")
    
    def decrypt(self, encrypted_data: String) -> String:
        """Decrypt string data."""
        if not encrypted_data:
            return encrypted_data
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            decrypted_data = self._cipher_suite.decrypt(encrypted_bytes)
            return decrypted_data.decode('utf-8')
        
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
    
    def encrypt_dict(self, data: dict) -> dict:
        """Encrypt sensitive fields in a dictionary."""
        if not data:
            return data
        
        encrypted_data = data.copy()
        
        # Encrypt text content
        if 'text' in encrypted_data:
            encrypted_data['text'] = self.encrypt(encrypted_data['text'])
        
        # Encrypt any metadata that might contain sensitive info
        if 'metadata' in encrypted_data and isinstance(encrypted_data['metadata'], dict):
            encrypted_metadata = {}
            for key, value in encrypted_data['metadata'].items():
                if isinstance(value, str) and len(value) > 0:
                    encrypted_metadata[key] = self.encrypt(value)
                else:
                    encrypted_metadata[key] = value
            encrypted_data['metadata'] = encrypted_metadata
        
        return encrypted_data
    
    def decrypt_dict(self, encrypted_data: dict) -> dict:
        """Decrypt sensitive fields in a dictionary."""
        if not encrypted_data:
            return encrypted_data
        
        decrypted_data = encrypted_data.copy()
        
        # Decrypt text content
        if 'text' in decrypted_data:
            decrypted_data['text'] = self.decrypt(decrypted_data['text'])
        
        # Decrypt metadata
        if 'metadata' in decrypted_data and isinstance(decrypted_data['metadata'], dict):
            decrypted_metadata = {}
            for key, value in decrypted_data['metadata'].items():
                if isinstance(value, str) and len(value) > 0:
                    try:
                        decrypted_metadata[key] = self.decrypt(value)
                    except ValueError:
                        # If decryption fails, assume it wasn't encrypted
                        decrypted_metadata[key] = value
                else:
                    decrypted_metadata[key] = value
            decrypted_data['metadata'] = decrypted_metadata
        
        return decrypted_data
    
    @staticmethod
    def generate_key() -> String:
        """Generate a new encryption key."""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8')