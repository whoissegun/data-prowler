"""
Configuration management for DataProwler.

This module handles loading, validating, and accessing configuration 
settings from various sources (files, environment variables).
"""

import os
import sys
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union
import yaml
from pydantic import BaseModel, ValidationError

from dataprowler.core.settings.schema import ConfigSchema
from dataprowler.utils.helpers import deep_merge

logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Manages configuration settings for DataProwler.
    
    Handles loading configuration from:
    - Default configuration file
    - User-provided configuration file
    - Environment variables
    """
    
    def __init__(self):
        self._config = None
        self._config_model = None
        self._loaded_files = []
        
    @property
    def config(self) -> Dict[str, Any]:
        """Get the current configuration dictionary"""
        if self._config is None:
            self.load_config()
        return self._config
        
    @property
    def config_model(self) -> ConfigSchema:
        """Get the validated configuration model"""
        if self._config_model is None:
            self._validate_config()
        return self._config_model
        
    def _get_default_config_path(self) -> Path:
        """Get the path to the default configuration file"""
        return Path(__file__).parent / "settings" / "default.yaml"
        
    def _get_user_config_path(self) -> Optional[Path]:
        """
        Find the user configuration file.
        
        Looks in:
        1. Path specified by DATAPROWLER_CONFIG environment variable
        2. Current working directory: ./dataprowler_config.yaml
        3. User home directory: ~/.dataprowler/config.yaml
        """
        # Check environment variable
        if "DATAPROWLER_CONFIG" in os.environ:
            path = Path(os.environ["DATAPROWLER_CONFIG"])
            if path.exists():
                return path
                
        # Check current directory
        cwd_config = Path.cwd() / "dataprowler_config.yaml"
        if cwd_config.exists():
            return cwd_config
            
        # Check home directory
        home_config = Path.home() / ".dataprowler" / "config.yaml"
        if home_config.exists():
            return home_config
            
        return None
        
    def _load_yaml_file(self, file_path: Path) -> Dict[str, Any]:
        """Load a YAML file and return its contents as a dictionary"""
        try:
            with open(file_path, "r") as f:
                config = yaml.safe_load(f)
            self._loaded_files.append(str(file_path))
            return config or {}
        except Exception as e:
            logger.warning(f"Failed to load config file {file_path}: {e}")
            return {}
            
    def _load_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update config with environment variables.
        
        Environment variables in the format DATAPROWLER_SECTION_KEY will be
        incorporated into the configuration. For example:
        
        DATAPROWLER_SCRAPING_TIMEOUT=30 becomes {"scraping": {"timeout": 30}}
        """
        result = config.copy()
        prefix = "DATAPROWLER_"
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                parts = key[len(prefix):].lower().split("_")
                
                # Convert value to appropriate type
                if value.isdigit():
                    value = int(value)
                elif value.lower() in ("true", "false"):
                    value = value.lower() == "true"
                elif value.replace(".", "").isdigit() and value.count(".") == 1:
                    value = float(value)
                    
                # Navigate to the right nested dictionary
                current = result
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                    
                # Set the value
                current[parts[-1]] = value
                
        return result
        
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from all sources and merge them.
        
        Priority order (highest to lowest):
        1. Environment variables
        2. User configuration file
        3. Default configuration file
        """
        # Load default config
        default_config = self._load_yaml_file(self._get_default_config_path())
        
        # Load user config if it exists
        user_config_path = self._get_user_config_path()
        user_config = self._load_yaml_file(user_config_path) if user_config_path else {}
        
        # Merge configs with user config overriding defaults
        merged_config = deep_merge(default_config, user_config)
        
        # Apply environment variables
        final_config = self._load_env_vars(merged_config)
        
        self._config = final_config
        return final_config
        
    def _validate_config(self) -> ConfigSchema:
        """Validate the configuration against the schema"""
        try:
            config_model = ConfigSchema(**self.config)
            self._config_model = config_model
            return config_model
        except ValidationError as e:
            logger.error(f"Configuration validation failed: {e}")
            # You could choose to exit here, or use a default config
            # depending on how critical correct configuration is
            raise
            
    def reload(self) -> Dict[str, Any]:
        """Reload the configuration from all sources"""
        self._config = None
        self._config_model = None
        return self.load_config()
        
    def get_setting(self, path: str, default: Any = None) -> Any:
        """
        Get a setting from the configuration using dot notation.
        
        Example:
            config.get_setting("scraping.timeout", 30)
        """
        config = self.config
        parts = path.split(".")
        
        for part in parts:
            if isinstance(config, dict) and part in config:
                config = config[part]
            else:
                return default
                
        return config
        
    def __str__(self) -> str:
        """String representation showing loaded config files"""
        if not self._loaded_files:
            return "ConfigManager (no files loaded)"
        return f"ConfigManager (loaded: {', '.join(self._loaded_files)})"


# Create a singleton instance
config_manager = ConfigManager()

# Convenience function to get a setting
def get_setting(path: str, default: Any = None) -> Any:
    """Get a configuration setting using dot notation"""
    return config_manager.get_setting(path, default)