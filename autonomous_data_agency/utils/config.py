"""Configuration management for the autonomous data agency."""

import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """Configuration for language models."""

    provider: str = Field(default="openai", description="LLM provider (openai, anthropic, etc.)")
    model: str = Field(default="gpt-4", description="Model name")
    temperature: float = Field(default=0.7, description="Temperature for generation")
    max_tokens: Optional[int] = Field(default=None, description="Maximum tokens to generate")
    api_key: Optional[str] = Field(default=None, description="API key for the provider")


class AgencyConfig(BaseModel):
    """Configuration for the agency."""

    name: str = Field(default="Autonomous Data Agency", description="Name of the agency")
    max_iterations: int = Field(default=10, description="Maximum iterations per task")
    enable_logging: bool = Field(default=True, description="Enable logging")
    log_level: str = Field(default="INFO", description="Logging level")
    llm_config: LLMConfig = Field(default_factory=LLMConfig, description="LLM configuration")


class ConfigManager:
    """
    Manages configuration for the autonomous data agency.
    
    This class handles loading configuration from environment variables,
    configuration files, and provides defaults.
    """

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Optional path to a configuration file
        """
        # Load environment variables
        load_dotenv()
        
        self.config_file = config_file
        self._config: Optional[AgencyConfig] = None

    def load_config(self) -> AgencyConfig:
        """
        Load configuration from environment and/or file.
        
        Returns:
            AgencyConfig object
        """
        if self._config is not None:
            return self._config

        # Build LLM config from environment
        llm_config = LLMConfig(
            provider=os.getenv("LLM_PROVIDER", "openai"),
            model=os.getenv("LLM_MODEL", "gpt-4"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "2000")) if os.getenv("LLM_MAX_TOKENS") else None,
            api_key=os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY"),
        )

        # Build agency config
        self._config = AgencyConfig(
            name=os.getenv("AGENCY_NAME", "Autonomous Data Agency"),
            max_iterations=int(os.getenv("MAX_ITERATIONS", "10")),
            enable_logging=os.getenv("ENABLE_LOGGING", "true").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            llm_config=llm_config,
        )

        return self._config

    def get_config(self) -> AgencyConfig:
        """
        Get the current configuration.
        
        Returns:
            AgencyConfig object
        """
        if self._config is None:
            return self.load_config()
        return self._config

    def update_config(self, **kwargs: Any) -> None:
        """
        Update configuration values.
        
        Args:
            **kwargs: Configuration parameters to update
        """
        if self._config is None:
            self.load_config()
        
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)

    def get_llm_config(self) -> LLMConfig:
        """
        Get LLM configuration.
        
        Returns:
            LLMConfig object
        """
        config = self.get_config()
        return config.llm_config
