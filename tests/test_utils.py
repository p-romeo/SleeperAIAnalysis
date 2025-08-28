"""Unit tests for utility modules."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.utils.config import AppConfig, ConfigManager
from src.utils.encryption import EncryptionManager
from src.utils.logger import setup_logger


class TestAppConfig:
    """Test AppConfig class."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = AppConfig()
        assert config.ai_provider == "mock"
        assert config.ai_api_key == ""
        assert config.sleeper_username == ""
        assert config.cache_enabled is True
        assert config.cache_duration_hours == 24
    
    def test_custom_values(self):
        """Test custom configuration values."""
        config = AppConfig(
            ai_provider="openai",
            ai_api_key="test-key",
            sleeper_username="testuser",
            cache_enabled=False
        )
        assert config.ai_provider == "openai"
        assert config.ai_api_key == "test-key"
        assert config.sleeper_username == "testuser"
        assert config.cache_enabled is False
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = AppConfig(ai_provider="anthropic", sleeper_username="user")
        config_dict = config.to_dict()
        
        assert config_dict["ai_provider"] == "anthropic"
        assert config_dict["sleeper_username"] == "user"
        assert "ai_api_key" in config_dict
    
    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "ai_provider": "openai",
            "sleeper_username": "testuser",
            "cache_enabled": False
        }
        config = AppConfig.from_dict(data)
        
        assert config.ai_provider == "openai"
        assert config.sleeper_username == "testuser"
        assert config.cache_enabled is False


class TestEncryptionManager:
    """Test EncryptionManager class."""
    
    def test_initialization(self):
        """Test encryption manager initialization."""
        manager = EncryptionManager()
        assert manager.salt == b'sleeper_optimizer_salt_v2'
    
    def test_custom_salt(self):
        """Test custom salt initialization."""
        custom_salt = b'custom_salt'
        manager = EncryptionManager(salt=custom_salt)
        assert manager.salt == custom_salt
    
    def test_derive_key(self):
        """Test key derivation."""
        manager = EncryptionManager()
        password = "test_password"
        key = manager.derive_key(password)
        
        assert isinstance(key, bytes)
        assert len(key) > 0
    
    def test_encrypt_decrypt(self):
        """Test encryption and decryption."""
        manager = EncryptionManager()
        password = "test_password"
        data = "test_data"
        
        encrypted = manager.encrypt_data(data, password)
        decrypted = manager.decrypt_data(encrypted, password)
        
        assert decrypted == data
    
    def test_verify_password(self):
        """Test password verification."""
        manager = EncryptionManager()
        password = "test_password"
        data = "test_data"
        
        encrypted = manager.encrypt_data(data, password)
        
        assert manager.verify_password(encrypted, password) is True
        assert manager.verify_password(encrypted, "wrong_password") is False


class TestConfigManager:
    """Test ConfigManager class."""
    
    @patch('pathlib.Path.home')
    def test_initialization(self, mock_home):
        """Test configuration manager initialization."""
        mock_home.return_value = Path("/fake/home")
        manager = ConfigManager()
        
        assert manager.config_dir == Path("/fake/home/.sleeper_optimizer")
        assert manager.config_file == Path("/fake/home/.sleeper_optimizer/config.encrypted")
    
    def test_validate_config_valid(self):
        """Test valid configuration validation."""
        config = AppConfig(
            sleeper_username="testuser",
            ai_provider="mock"
        )
        manager = ConfigManager()
        
        assert manager.validate_config(config) is True
    
    def test_validate_config_missing_username(self):
        """Test configuration validation with missing username."""
        config = AppConfig(
            sleeper_username="",
            ai_provider="mock"
        )
        manager = ConfigManager()
        
        assert manager.validate_config(config) is False
    
    def test_validate_config_missing_api_key(self):
        """Test configuration validation with missing API key."""
        config = AppConfig(
            sleeper_username="testuser",
            ai_provider="openai",
            ai_api_key=""
        )
        manager = ConfigManager()
        
        assert manager.validate_config(config) is False
    
    def test_validate_config_invalid_provider(self):
        """Test configuration validation with invalid provider."""
        config = AppConfig(
            sleeper_username="testuser",
            ai_provider="invalid_provider"
        )
        manager = ConfigManager()
        
        assert manager.validate_config(config) is False


class TestLogger:
    """Test logger utilities."""
    
    def test_setup_logger(self):
        """Test logger setup."""
        logger = setup_logger("test_logger", level="DEBUG")
        
        assert logger.name == "test_logger"
        assert logger.level == 10  # DEBUG level
    
    def test_get_logger(self):
        """Test getting existing logger."""
        from src.utils.logger import get_logger
        
        logger1 = setup_logger("test_logger")
        logger2 = get_logger("test_logger")
        
        assert logger1 is logger2


if __name__ == "__main__":
    pytest.main([__file__])
