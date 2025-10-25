"""
Data models for the customer service agent.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import json


@dataclass
class ConversationMetadata:
    """Metadata about a conversation session."""

    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    total_interactions: int = 0
    total_tool_calls: int = 0
    last_interaction: Optional[str] = None
    customer_id: Optional[str] = None
    sentiment_scores: List[float] = field(default_factory=list)
    conversation_topics: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "created_at": self.created_at,
            "total_interactions": self.total_interactions,
            "total_tool_calls": self.total_tool_calls,
            "last_interaction": self.last_interaction,
            "customer_id": self.customer_id,
            "sentiment_scores": self.sentiment_scores,
            "conversation_topics": self.conversation_topics,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationMetadata":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class EvaluationResult:
    """Result of interaction evaluation."""

    timestamp: str
    interaction_id: int
    user_input: str
    agent_response: str
    score: float
    reasoning: str
    tool_used: Optional[str] = None
    sentiment_score: Optional[float] = None
    response_time: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp,
            "interaction_id": self.interaction_id,
            "user_input": self.user_input,
            "agent_response": self.agent_response,
            "score": self.score,
            "reasoning": self.reasoning,
            "tool_used": self.tool_used,
            "sentiment_score": self.sentiment_score,
            "response_time": self.response_time,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvaluationResult":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class ToolCall:
    """Represents a tool call with its result."""

    name: str
    arguments: Dict[str, Any]
    result: str
    success: bool = True
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "arguments": self.arguments,
            "result": self.result,
            "success": self.success,
            "error_message": self.error_message,
        }


@dataclass
class WorkflowStep:
    """Represents a step in a multi-step workflow."""

    name: str
    instruction: str
    required_tools: List[str] = field(default_factory=list)
    expected_output: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "instruction": self.instruction,
            "required_tools": self.required_tools,
            "expected_output": self.expected_output,
        }


@dataclass
class WorkflowResult:
    """Result of a workflow execution."""

    step_number: int
    step_name: str
    instruction: str
    response: str
    tool_calls: List[ToolCall] = field(default_factory=list)
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "step_number": self.step_number,
            "step_name": self.step_name,
            "instruction": self.instruction,
            "response": self.response,
            "tool_calls": [tc.to_dict() for tc in self.tool_calls],
            "success": self.success,
            "error": self.error,
        }
