"""Configuration management for the application."""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

from src.utils.encryption import EncryptionManager
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AppConfig:
    """Application configuration data class."""
    
    ai_provider: str = "mock"
    ai_api_key: str = ""
    sleeper_username: str = ""
    fantasypros_api_key: str = ""  # Optional: for enhanced projections
    cache_enabled: bool = True
    cache_duration_hours: int = 24
    log_level: str = "INFO"
    log_to_file: bool = True
    max_retries: int = 3
    request_timeout: int = 30
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AppConfig":
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


class ConfigManager:
    """Manages application configuration with encryption."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Directory for config files. Defaults to user home.
        """
        if config_dir is None:
            config_dir = Path.home() / ".sleeper_optimizer"
        
        self.config_dir = config_dir
        self.config_file = config_dir / "config.encrypted"
        self.encryption_manager = EncryptionManager()
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Config directory: {self.config_dir}")
    
    def save_config(self, config: AppConfig, password: str) -> None:
        """
        Save encrypted configuration.
        
        Args:
            config: Configuration to save
            password: Password for encryption
        """
        try:
            config_dict = config.to_dict()
            config_json = json.dumps(config_dict, indent=2)
            
            encrypted_data = self.encryption_manager.encrypt_data(config_json, password)
            
            with open(self.config_file, 'wb') as f:
                f.write(encrypted_data)
            
            logger.info("Configuration saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise
    
    def load_config(self, password: str) -> Optional[AppConfig]:
        """
        Load encrypted configuration.
        
        Args:
            password: Password for decryption
            
        Returns:
            Configuration object or None if failed
        """
        if not self.config_file.exists():
            logger.info("No configuration file found")
            return None
        
        try:
            with open(self.config_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_json = self.encryption_manager.decrypt_data(encrypted_data, password)
            config_dict = json.loads(decrypted_json)
            
            config = AppConfig.from_dict(config_dict)
            logger.info("Configuration loaded successfully")
            return config
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return None
    
    def config_exists(self) -> bool:
        """Check if configuration file exists."""
        return self.config_file.exists()
    
    def delete_config(self) -> None:
        """Delete configuration file."""
        try:
            if self.config_file.exists():
                self.config_file.unlink()
                logger.info("Configuration file deleted")
        except Exception as e:
            logger.error(f"Failed to delete configuration: {e}")
    
    def validate_config(self, config: AppConfig) -> bool:
        """
        Validate configuration values.
        
        Args:
            config: Configuration to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not config.sleeper_username:
            logger.error("Sleeper username is required")
            return False
        
        if config.ai_provider in ["openai", "anthropic"] and not config.ai_api_key:
            logger.error(f"API key required for {config.ai_provider}")
            return False
        
        if config.ai_provider not in ["openai", "anthropic", "mock"]:
            logger.error(f"Invalid AI provider: {config.ai_provider}")
            return False
        
        return True
