"""Configuration management for the application."""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

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
    """Manages application configuration."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Directory for config files. Defaults to user home.
        """
        if config_dir is None:
            config_dir = Path.home() / ".sleeper_optimizer"
        
        self.config_dir = config_dir
        self.config_file = config_dir / "config.json"
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Config directory: {self.config_dir}")
    
    def save_config(self, config: AppConfig) -> None:
        """
        Save configuration to JSON file.
        
        Args:
            config: Configuration to save
        """
        try:
            config_dict = config.to_dict()
            
            with open(self.config_file, 'w') as f:
                json.dump(config_dict, f, indent=2)
            
            logger.info("Configuration saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise
    
    def load_config(self) -> Optional[AppConfig]:
        """
        Load configuration from JSON file.
            
        Returns:
            Configuration object or None if failed
        """
        if not self.config_file.exists():
            logger.info("No configuration file found")
            return None
        
        try:
            with open(self.config_file, 'r') as f:
                config_dict = json.load(f)
            
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
