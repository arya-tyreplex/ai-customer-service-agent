"""
Main customer service agent implementation.
"""

import json
import logging
import time
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field

from openai import OpenAI
from loguru import logger

from config import AgentConfig
from models import ConversationMetadata, EvaluationResult, WorkflowStep, WorkflowResult
from tools import create_tool_registry, ToolRegistry
from evaluator import PerformanceEvaluator
from utils import (
    safe_openai_call,
    format_conversation_history,
    calculate_response_time,
    sanitize_user_input,
    ConversationLogger,
)


class CustomerServiceAgent:
    """
    A comprehensive customer service agent with tool integration, memory, and evaluation.
    """

    def __init__(
        self, config: Optional[AgentConfig] = None, model: Optional[str] = None
    ):
        """
        Initialize the customer service agent.

        Args:
            config: Agent configuration
            model: Override default model
        """
        self.config = config or AgentConfig.from_env()
        self.model = model or self.config.default_model

        # Initialize OpenAI client
        self.client = None
        self.client_available = False
        self._initialize_openai_client()

        # Initialize core components
        self.tool_registry = create_tool_registry()
        self.evaluator = (
            PerformanceEvaluator(self.config, self.client)  # type: ignore
            if self.client_available
            else None
        )
        self.conversation_logger = ConversationLogger(self.config.log_file)

        # Initialize conversation state
        self.system_prompt = self._create_system_prompt()
        self.conversation_history: List[Dict[str, Any]] = [
            {"role": "system", "content": self.system_prompt}
        ]
        self.metadata = ConversationMetadata()

        logger.info(f"CustomerServiceAgent initialized with model: {self.model}")
        if not self.client_available:
            logger.warning("Running in demo mode - OpenAI client unavailable")

    def _initialize_openai_client(self) -> None:
        """Initialize OpenAI client with error handling."""
        try:
            if not self.config.openai_api_key:
                raise ValueError("OPENAI_API_KEY not configured")

            self.client = OpenAI(api_key=self.config.openai_api_key)

            # Test the client with a simple request
            self.client.models.list()
            self.client_available = True
            logger.info("OpenAI client initialized successfully")

        except Exception as e:
            logger.warning(f"OpenAI client initialization failed: {str(e)}")
            self.client_available = False
            self.client = None

    def _create_system_prompt(self) -> str:
        """Create the system prompt for the agent."""
        return """You are an intelligent customer service agent for TechStore, an online electronics retailer. 

CORE RESPONSIBILITIES:
1. Answer customer inquiries professionally and empathetically
2. Look up order information using tools when order numbers are provided
3. Process refunds and returns for valid requests
4. Check product inventory and provide accurate availability information
5. Escalate complex or urgent issues to human agents when appropriate
6. Provide clear, helpful, and accurate information

GUIDELINES:
- Always be polite, patient, and customer-focused
- Ask for necessary information (like order numbers) when needed
- Use available tools to provide accurate, up-to-date information
- Don't make up information - use tools to look things up
- For angry customers, show empathy and focus on solutions
- Escalate to human agents for: payment issues, account problems, complex technical issues

TOOL USAGE:
- Use lookup_order for order status inquiries
- Use process_refund for refund requests (requires order number and reason)
- Use check_inventory for product availability
- Use escalate_to_human for issues you cannot resolve
- Use get_product_catalog to show available products

Always provide clear next steps and set realistic expectations."""

    @safe_openai_call(max_retries=3)
    def _call_openai_api(self, **kwargs) -> Any:
        """Safe wrapper for OpenAI API calls."""
        if not self.client_available:
            from .utils import DemoModeFallback

            return DemoModeFallback.create_demo_response()

        return self.client.chat.completions.create(**kwargs) # type: ignore

    def _analyze_sentiment(self, message: str) -> Dict[str, Any]:
        """Analyze sentiment of customer message."""
        if not self.config.enable_sentiment_analysis:
            return {"sentiment": "neutral", "score": 0.0}

        try:
            response = self._call_openai_api(
                model="gpt-3.5-turbo",  # Use smaller model for sentiment to save costs
                messages=[
                    {
                        "role": "user",
                        "content": f"""Analyze the sentiment of this customer message and return JSON with:
                    - sentiment: positive, neutral, or negative
                    - score: number from -1 (very negative) to 1 (very positive)
                    - emotions: list of detected emotions
                    
                    Message: {message}
                    
                    Return only valid JSON, no other text.""",
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
            )

            if not self.client_available:
                sentiment_data = {"sentiment": "neutral", "score": 0.0, "emotions": []}
            else:
                sentiment_data = json.loads(response.choices[0].message.content)

            # Store sentiment score for analytics
            if "score" in sentiment_data:
                self.metadata.sentiment_scores.append(sentiment_data["score"])

            return sentiment_data

        except Exception as e:
            logger.error(f"Sentiment analysis failed: {str(e)}")
            return {"sentiment": "neutral", "score": 0.0, "error": str(e)}

    def chat(self, user_message: str, customer_id: Optional[str] = None) -> str:
        """
        Process user message and return agent response.

        Args:
            user_message: The user's message
            customer_id: Optional customer identifier

        Returns:
            The agent's response
        """
        start_time = time.time()

        try:
            logger.info(
                f"Processing message from customer {customer_id}: {user_message[:100]}..."
            )

            # Update metadata
            if customer_id:
                self.metadata.customer_id = customer_id

            # Sanitize input
            sanitized_message = sanitize_user_input(user_message)

            # Analyze sentiment if enabled
            sentiment_data = self._analyze_sentiment(sanitized_message)

            # Add user message to conversation history
            self.conversation_history.append(
                {"role": "user", "content": sanitized_message}
            )

            # Get agent response (may involve tool calls)
            response = self._get_agent_response()

            # Update metadata
            self.metadata.total_interactions += 1
            self.metadata.last_interaction = datetime.now().isoformat()

            # Calculate response time
            response_time = calculate_response_time(start_time)

            # Evaluate interaction if enabled
            if self.config.enable_evaluation and self.evaluator:
                self.evaluator.evaluate_interaction(
                    user_input=sanitized_message,
                    agent_response=response,
                    interaction_id=self.metadata.total_interactions,
                    sentiment_score=sentiment_data.get("score"),
                    response_time=response_time,
                )

            # Log the interaction
            self.conversation_logger.log_interaction(
                user_input=sanitized_message,
                agent_response=response,
                customer_id=customer_id,
            )

            logger.info(f"Message processed successfully in {response_time:.2f}s")
            return response

        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            error_response = "I apologize, but I encountered an error processing your request. Please try again or contact our support team if the issue persists."

            # Log the error
            self.conversation_logger.log_interaction(
                user_input=user_message,
                agent_response=error_response,
                customer_id=customer_id,
            )

            return error_response

    def _get_agent_response(self) -> str:
        """Get response from agent, handling tool calls if needed."""
        # Format conversation history to manage token usage
        formatted_history = format_conversation_history(
            self.conversation_history, self.config.max_conversation_history
        )

        # Initial API call
        response = self._call_openai_api(
            model=self.model,
            messages=formatted_history,
            tools=self.tool_registry.get_all_schemas(),
            tool_choice="auto",
            temperature=self.config.default_temperature,
        )

        response_message = response.choices[0].message
        tool_calls = getattr(response_message, "tool_calls", [])

        # If no tool calls, return direct response
        if not tool_calls:
            final_response = getattr(
                response_message,
                "content",
                "I apologize, but I couldn't generate a response.",
            )
            self.conversation_history.append(
                {"role": "assistant", "content": final_response}
            )
            return final_response

        # Handle tool calls
        self.conversation_history.append(response_message) # type: ignore
        tool_results = []

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            logger.info(f"Executing tool: {function_name} with args: {function_args}")

            try:
                # Execute the tool
                tool_function = self.tool_registry.get_function(function_name)
                function_response = tool_function(**function_args)

                # Add tool response to conversation
                self.conversation_history.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": function_response,
                    }
                )

                tool_results.append(
                    {
                        "name": function_name,
                        "arguments": function_args,
                        "result": function_response,
                        "success": True,
                    }
                )

                self.metadata.total_tool_calls += 1

            except Exception as e:
                error_message = f"Error executing {function_name}: {str(e)}"
                logger.error(error_message)

                self.conversation_history.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": json.dumps({"error": error_message}),
                    }
                )

                tool_results.append(
                    {
                        "name": function_name,
                        "arguments": function_args,
                        "result": error_message,
                        "success": False,
                    }
                )

        # Get final response after tool execution
        final_response = self._call_openai_api(
            model=self.model,
            messages=self.conversation_history,
            temperature=self.config.default_temperature,
        )

        final_message = final_response.choices[0].message.content
        self.conversation_history.append(
            {"role": "assistant", "content": final_message}
        )

        return final_message

    def execute_workflow(
        self, workflow_steps: List[WorkflowStep]
    ) -> List[WorkflowResult]:
        """
        Execute a multi-step workflow.

        Args:
            workflow_steps: List of workflow steps to execute

        Returns:
            List of workflow results
        """
        logger.info(f"Executing workflow with {len(workflow_steps)} steps")
        results = []

        for i, step in enumerate(workflow_steps):
            logger.info(f"Step {i+1}/{len(workflow_steps)}: {step.name}")

            try:
                response = self.chat(step.instruction)

                result = WorkflowResult(
                    step_number=i + 1,
                    step_name=step.name,
                    instruction=step.instruction,
                    response=response,
                    success=True,
                )

                results.append(result)
                logger.info(f"Step {i+1} completed successfully")

            except Exception as e:
                logger.error(f"Step {i+1} failed: {str(e)}")
                results.append(
                    WorkflowResult(
                        step_number=i + 1,
                        step_name=step.name,
                        instruction=step.instruction,
                        response=f"Error: {str(e)}",
                        success=False,
                        error=str(e),
                    )
                )

        return results

    def get_performance_report(self, last_n_interactions: Optional[int] = 50) -> str:
        """
        Generate a comprehensive performance report.

        Args:
            last_n_interactions: Number of recent interactions to include

        Returns:
            Formatted performance report
        """
        if not self.evaluator or not self.evaluator.evaluation_results:
            return "No evaluation data available yet."

        from .utils import format_performance_report

        report_data = self.evaluator.generate_performance_report(last_n_interactions)
        return format_performance_report(report_data)

    def get_conversation_summary(self) -> str:
        """Generate a summary of the current conversation."""
        summary_prompt = """Please provide a concise summary of our conversation so far, including:
        - The main topics discussed
        - Any issues or questions the customer had
        - Solutions or information provided
        - Current status or next steps
        
        Keep it to 3-4 sentences maximum."""

        return self.chat(summary_prompt)

    def get_conversation_history(self, formatted: bool = True) -> List[Dict[str, Any]]:
        """
        Get the conversation history.

        Args:
            formatted: If True, exclude system messages and tool calls

        Returns:
            Conversation history
        """
        if not formatted:
            return self.conversation_history.copy()

        # Return only user and assistant messages for display
        return [
            msg
            for msg in self.conversation_history
            if msg["role"] in ["user", "assistant"] and "content" in msg
        ]

    def reset_conversation(self, keep_system_prompt: bool = True) -> None:
        """
        Reset the conversation history.

        Args:
            keep_system_prompt: Whether to keep the system prompt
        """
        logger.info("Resetting conversation")

        if keep_system_prompt:
            self.conversation_history = [
                {"role": "system", "content": self.system_prompt}
            ]
        else:
            self.conversation_history = []

        # Reset metadata but keep customer_id if set
        current_customer_id = self.metadata.customer_id
        self.metadata = ConversationMetadata()
        self.metadata.customer_id = current_customer_id

        logger.info("Conversation reset complete")

    def save_conversation(self, filepath: str) -> None:
        """Save conversation history to file."""
        data = {
            "conversation_history": self.conversation_history,
            "metadata": self.metadata.to_dict(),
            "saved_at": datetime.now().isoformat(),
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Conversation saved to {filepath}")

    def load_conversation(self, filepath: str) -> None:
        """Load conversation history from file."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.conversation_history = data.get("conversation_history", [])
            self.metadata = ConversationMetadata.from_dict(data.get("metadata", {}))

            logger.info(f"Conversation loaded from {filepath}")

        except Exception as e:
            logger.error(f"Error loading conversation: {str(e)}")
            raise

    @property
    def is_demo_mode(self) -> bool:
        """Check if agent is running in demo mode."""
        return not self.client_available

    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the agent instance."""
        return {
            "model": self.model,
            "demo_mode": self.is_demo_mode,
            "total_interactions": self.metadata.total_interactions,
            "total_tool_calls": self.metadata.total_tool_calls,
            "customer_id": self.metadata.customer_id,
            "available_tools": list(self.tool_registry.tools.keys()),
        }
