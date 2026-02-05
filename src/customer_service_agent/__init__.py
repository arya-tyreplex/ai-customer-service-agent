"""
TyrePlex AI Call Center - Voice-enabled customer service for tyre business.
"""

__version__ = "2.0.0"
__author__ = "Bhavik Jikadara"
__email__ = "bhavikjikadara@yahoo.com"

from .tyreplex_voice_agent import TyrePlexVoiceAgent, CallMetadata, CompanyKnowledgeBase
from .tyreplex_tools import (
    create_tyreplex_tool_registry,
    TyrePlexTools,
    TyrePlexToolRegistry
)

__all__ = [
    # Main agent
    "TyrePlexVoiceAgent",
    # Metadata
    "CallMetadata",
    "CompanyKnowledgeBase",
    # Tools
    "create_tyreplex_tool_registry",
    "TyrePlexTools",
    "TyrePlexToolRegistry",
]
