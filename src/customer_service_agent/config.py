"""
Configuration management for the customer service agent.
"""

import os
from typing import Optional, List
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class AgentConfig:
    """Configuration for the customer service agent."""

    # OpenAI Configuration
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    default_model: str = field(
        default_factory=lambda: os.getenv("DEFAULT_MODEL", "gpt-4o")
    )

    # Agent Behavior
    enable_evaluation: bool = field(
        default_factory=lambda: os.getenv("ENABLE_EVALUATION", "true").lower() == "true"
    )
    enable_sentiment_analysis: bool = field(
        default_factory=lambda: os.getenv("ENABLE_SENTIMENT_ANALYSIS", "true").lower()
        == "true"
    )
    max_conversation_history: int = field(
        default_factory=lambda: int(os.getenv("MAX_CONVERSATION_HISTORY", "50"))
    )
    default_temperature: float = field(
        default_factory=lambda: float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
    )

    # Logging
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    log_file: Optional[str] = field(
        default_factory=lambda: os.getenv("LOG_FILE", "customer_agent.log")
    )

    # Performance
    evaluation_threshold: float = field(
        default_factory=lambda: float(os.getenv("EVALUATION_THRESHOLD", "7.0"))
    )
    max_retries: int = field(default_factory=lambda: int(os.getenv("MAX_RETRIES", "3")))

    def validate(self) -> None:
        """Validate configuration settings."""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required but not set")

        if self.max_conversation_history < 1:
            raise ValueError("MAX_CONVERSATION_HISTORY must be at least 1")

        if not (0 <= self.default_temperature <= 2):
            raise ValueError("DEFAULT_TEMPERATURE must be between 0 and 2")

        if not (0 <= self.evaluation_threshold <= 10):
            raise ValueError("EVALUATION_THRESHOLD must be between 0 and 10")

    @classmethod
    def from_env(cls) -> "AgentConfig":
        """Create configuration from environment variables."""
        config = cls()
        config.validate()
        return config
