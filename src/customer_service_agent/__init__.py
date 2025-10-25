"""
AI Customer Service Agent - A production-ready customer service AI agent system.
"""

__version__ = "1.0.0"
__author__ = "Bhavik Jikadara"
__email__ = "bhavikjikadara@yahoo.com"

from .agent import CustomerServiceAgent
from .config import AgentConfig
from .models import (
    ConversationMetadata,
    EvaluationResult,
    WorkflowStep,
    WorkflowResult,
    ToolCall,
)
from .tools import create_tool_registry, CustomerServiceTools
from .evaluator import PerformanceEvaluator, EvaluationMetrics
from .utils import (
    setup_logging,
    format_performance_report,
    sentiment_score_to_label,
    ConversationLogger,
)

__all__ = [
    # Main agent
    "CustomerServiceAgent",
    # Configuration
    "AgentConfig",
    # Models
    "ConversationMetadata",
    "EvaluationResult",
    "WorkflowStep",
    "WorkflowResult",
    "ToolCall",
    # Tools
    "create_tool_registry",
    "CustomerServiceTools",
    # Evaluation
    "PerformanceEvaluator",
    "EvaluationMetrics",
    # Utilities
    "setup_logging",
    "format_performance_report",
    "sentiment_score_to_label",
    "ConversationLogger",
]
