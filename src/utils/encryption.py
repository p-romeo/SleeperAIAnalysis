"""Encryption utilities for secure storage of sensitive data."""

import base64
import os
from pathlib import Path
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.exceptions import InvalidKey

from src.utils.logger import get_logger

logger = get_logger(__name__)


class EncryptionManager:
    """Manages encryption and decryption of sensitive data."""
    
    def __init__(self, salt: Optional[bytes] = None):
        """
        Initialize encryption manager.
        
        Args:
            salt: Optional salt for key derivation. If None, uses default.
        """
        self.salt = salt or b'sleeper_optimizer_salt_v2'
        self._key: Optional[bytes] = None
        
    def derive_key(self, password: str, iterations: int = 100000) -> bytes:
        """
        Derive encryption key from password using PBKDF2.
        
        Args:
            password: User password
            iterations: Number of PBKDF2 iterations
            
        Returns:
            Derived encryption key
        """
        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=self.salt,
                iterations=iterations,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            logger.debug("Key derived successfully")
            return key
        except Exception as e:
            logger.error(f"Failed to derive key: {e}")
            raise
    
    def encrypt_data(self, data: str, password: str) -> bytes:
        """
        Encrypt data using password-derived key.
        
        Args:
            data: Data to encrypt
            password: Password for key derivation
            
        Returns:
            Encrypted data
        """
        try:
            key = self.derive_key(password)
            f = Fernet(key)
            encrypted = f.encrypt(data.encode())
            logger.debug("Data encrypted successfully")
            return encrypted
        except Exception as e:
            logger.error(f"Failed to encrypt data: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: bytes, password: str) -> str:
        """
        Decrypt data using password-derived key.
        
        Args:
            encrypted_data: Data to decrypt
            password: Password for key derivation
            
        Returns:
            Decrypted data
        """
        try:
            key = self.derive_key(password)
            f = Fernet(key)
            decrypted = f.decrypt(encrypted_data)
            logger.debug("Data decrypted successfully")
            return decrypted.decode()
        except InvalidKey:
            logger.error("Invalid password or corrupted data")
            raise ValueError("Invalid password or corrupted data")
        except Exception as e:
            logger.error(f"Failed to decrypt data: {e}")
            raise
    
    def verify_password(self, encrypted_data: bytes, password: str) -> bool:
        """
        Verify if password can decrypt data.
        
        Args:
            encrypted_data: Encrypted data to test
            password: Password to test
            
        Returns:
            True if password is correct, False otherwise
        """
        try:
            self.decrypt_data(encrypted_data, password)
            return True
        except (ValueError, Exception):
            return False
