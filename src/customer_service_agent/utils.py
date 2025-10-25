"""
Utility functions for the customer service agent.
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, timedelta
from functools import wraps
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

logger = logging.getLogger(__name__)


class DemoModeFallback:
    """Provides fallback functionality when OpenAI API is unavailable."""

    @staticmethod
    def create_demo_response(content: str = None):
        """Create a demo response object that mimics OpenAI's response structure."""
        if content is None:
            content = (
                "[DEMO MODE] OpenAI client unavailable. This is a simulated response "
                "so the application can continue in offline mode."
            )

        class DemoMessage:
            def __init__(self, content):
                self.content = content
                self.tool_calls = []

        class DemoChoice:
            def __init__(self, message):
                self.message = message

        class DemoResponse:
            def __init__(self, choice):
                self.choices = [choice]

        return DemoResponse(DemoChoice(DemoMessage(content)))


def safe_openai_call(max_retries: int = 3):
    """
    Decorator for safe OpenAI API calls with retry logic and demo fallback.
    """

    def decorator(func: Callable):
        @wraps(func)
        @retry(
            stop=stop_after_attempt(max_retries),
            wait=wait_exponential(multiplier=1, min=4, max=10),
            retry=retry_if_exception_type((Exception,)),  # Retry on any exception
        )
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"OpenAI API call failed: {str(e)}")
                if "last_attempt" in str(e):  # Final attempt failed
                    logger.info("Entering demo fallback mode")
                    return DemoModeFallback.create_demo_response()
                raise  # Re-raise to trigger retry

        return wrapper

    return decorator


def format_conversation_history(
    history: List[Dict[str, str]], max_length: int = 10
) -> List[Dict[str, str]]:
    """
    Format and truncate conversation history to manage token usage.
    """
    if len(history) <= max_length:
        return history

    # Always keep system message and recent messages
    system_message = history[0]  # Assuming first message is system
    recent_messages = history[-(max_length - 1) :]  # Keep most recent messages

    return [system_message] + recent_messages


def calculate_response_time(start_time: float) -> float:
    """Calculate response time in seconds."""
    return time.time() - start_time


def validate_order_number(order_number: str) -> bool:
    """Validate order number format."""
    if not order_number:
        return False

    # Basic validation - adjust based on your order number format
    return order_number.startswith("ORD-") and len(order_number) > 4


def sanitize_user_input(text: str, max_length: int = 1000) -> str:
    """Sanitize and truncate user input."""
    if not text:
        return ""

    # Remove excessive whitespace
    sanitized = " ".join(text.split())

    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "..."

    return sanitized


def sentiment_score_to_label(score: float) -> str:
    """Convert sentiment score to human-readable label."""
    if score > 0.6:
        return "Very Positive"
    elif score > 0.2:
        return "Positive"
    elif score > -0.2:
        return "Neutral"
    elif score > -0.6:
        return "Negative"
    else:
        return "Very Negative"


def format_performance_report(data: Dict[str, Any]) -> str:
    """Format performance report as a readable string."""
    metrics = data.get("metrics", {})
    summary = data.get("summary", {})

    report = f"""
╔══════════════════════════════════════════════════════════════╗
║           CUSTOMER SERVICE AGENT PERFORMANCE REPORT          ║
╚══════════════════════════════════════════════════════════════╝

📊 OVERALL SUMMARY
─────────────────────────────────────────────────────────────
Period:              {summary.get('period', 'N/A')}
Total Interactions:  {summary.get('total_evaluated', 0)}
Performance:         {summary.get('overall_performance', 'N/A')}
Trend:               {summary.get('score_trend', 'N/A')}

📈 DETAILED METRICS
─────────────────────────────────────────────────────────────
Average Score:       {metrics.get('average_score', 0):.2f}/10
Sentiment Trend:     {metrics.get('sentiment_trend', 0):.2f}
Tool Usage Rate:     {metrics.get('tool_usage_rate', 0):.2%}
Escalation Rate:     {metrics.get('escalation_rate', 0):.2%}
Avg Response Time:   {metrics.get('response_time_avg', 0):.2f}s

💡 RECOMMENDATIONS
─────────────────────────────────────────────────────────────
"""

    for recommendation in data.get("recommendations", []):
        report += f"• {recommendation}\n"

    report += "\n╚══════════════════════════════════════════════════════════════╝\n"

    return report


class ConversationLogger:
    """Utility for logging conversation data."""

    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file

    def log_interaction(
        self,
        user_input: str,
        agent_response: str,
        customer_id: Optional[str] = None,
        tool_calls: List[Dict] = None,
    ):
        """Log an interaction to file."""
        if not self.log_file:
            return

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "customer_id": customer_id,
            "user_input": user_input,
            "agent_response": agent_response,
            "tool_calls": tool_calls or [],
        }

        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.error(f"Failed to log interaction: {str(e)}")


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """Setup logging configuration."""
    log_config = {
        "level": getattr(logging, log_level.upper()),
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S",
    }

    if log_file:
        log_config["filename"] = log_file
        log_config["filemode"] = "a"

    logging.basicConfig(**log_config)

    # Set third-party loggers to WARNING to reduce noise
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
