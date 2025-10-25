"""
Tests for the CustomerServiceAgent class.
"""

import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from customer_service_agent import CustomerServiceAgent, AgentConfig
from customer_service_agent.models import WorkflowStep


class TestCustomerServiceAgent:
    """Test cases for CustomerServiceAgent."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = AgentConfig(
            openai_api_key="test-key",
            default_model="gpt-3.5-turbo",
            enable_evaluation=False,
            max_conversation_history=10,
        )

    @patch("customer_service_agent.agent.OpenAI")
    def test_agent_initialization(self, mock_openai):
        """Test agent initialization."""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.models.list.return_value = []

        agent = CustomerServiceAgent(config=self.config)

        assert agent.model == "gpt-3.5-turbo"
        assert agent.config == self.config
        assert agent.client_available == True

    @patch("customer_service_agent.agent.OpenAI")
    def test_agent_initialization_no_api_key(self, mock_openai):
        """Test agent initialization without API key."""
        config = AgentConfig(openai_api_key="")

        agent = CustomerServiceAgent(config=config)

        assert agent.client_available == False
        assert agent.is_demo_mode == True

    @patch("customer_service_agent.agent.CustomerServiceAgent._call_openai_api")
    def test_chat_basic(self, mock_api_call):
        """Test basic chat functionality."""
        # Mock API response
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Hello! How can I help you today?"
        mock_message.tool_calls = []
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_api_call.return_value = mock_response

        agent = CustomerServiceAgent(config=self.config)
        agent.client_available = True

        response = agent.chat("Hello", customer_id="test-customer")

        assert "help" in response.lower()
        assert agent.metadata.total_interactions == 1
        assert agent.metadata.customer_id == "test-customer"

    @patch("customer_service_agent.agent.CustomerServiceAgent._call_openai_api")
    def test_chat_with_tool_calls(self, mock_api_call):
        """Test chat with tool calls."""
        # Mock first API call with tool call
        mock_response1 = Mock()
        mock_choice1 = Mock()
        mock_message1 = Mock()
        mock_message1.content = None
        mock_tool_call = Mock()
        mock_tool_call.function.name = "lookup_order"
        mock_tool_call.function.arguments = '{"order_number": "ORD-12345"}'
        mock_tool_call.id = "call_123"
        mock_message1.tool_calls = [mock_tool_call]
        mock_choice1.message = mock_message1
        mock_response1.choices = [mock_choice1]

        # Mock second API call with final response
        mock_response2 = Mock()
        mock_choice2 = Mock()
        mock_message2 = Mock()
        mock_message2.content = "I found your order. It was delivered on 2025-09-18."
        mock_choice2.message = mock_message2
        mock_response2.choices = [mock_choice2]

        mock_api_call.side_effect = [mock_response1, mock_response2]

        agent = CustomerServiceAgent(config=self.config)
        agent.client_available = True

        response = agent.chat("Where is my order ORD-12345?")

        assert "delivered" in response.lower()
        assert agent.metadata.total_tool_calls == 1

    def test_workflow_execution(self):
        """Test workflow execution."""
        agent = CustomerServiceAgent(config=self.config)
        agent.client_available = False  # Use demo mode for predictable results

        workflow_steps = [
            WorkflowStep(name="Test Step 1", instruction="Say hello"),
            WorkflowStep(name="Test Step 2", instruction="Say goodbye"),
        ]

        results = agent.execute_workflow(workflow_steps)

        assert len(results) == 2
        assert results[0].step_number == 1
        assert results[0].step_name == "Test Step 1"
        assert results[0].success == True
        assert results[1].step_number == 2
        assert results[1].step_name == "Test Step 2"

    def test_conversation_reset(self):
        """Test conversation reset functionality."""
        agent = CustomerServiceAgent(config=self.config)
        agent.metadata.customer_id = "test-customer"
        agent.metadata.total_interactions = 5

        # Add some conversation history
        agent.conversation_history.extend(
            [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
            ]
        )

        agent.reset_conversation()

        # Should keep system prompt and customer ID
        assert len(agent.conversation_history) == 1
        assert agent.conversation_history[0]["role"] == "system"
        assert agent.metadata.total_interactions == 0
        assert agent.metadata.customer_id == "test-customer"  # Customer ID preserved

    def test_agent_info(self):
        """Test agent information retrieval."""
        agent = CustomerServiceAgent(config=self.config)

        info = agent.get_agent_info()

        assert "model" in info
        assert "demo_mode" in info
        assert "total_interactions" in info
        assert "available_tools" in info
        assert "lookup_order" in info["available_tools"]

    def test_performance_report_no_data(self):
        """Test performance report with no evaluation data."""
        agent = CustomerServiceAgent(config=self.config)
        agent.config.enable_evaluation = False

        report = agent.get_performance_report()

        assert "No evaluation data" in report

    @patch("customer_service_agent.agent.CustomerServiceAgent._call_openai_api")
    def test_sentiment_analysis_disabled(self, mock_api_call):
        """Test that sentiment analysis is skipped when disabled."""
        config = AgentConfig(openai_api_key="test-key", enable_sentiment_analysis=False)
        agent = CustomerServiceAgent(config=config)

        # Mock the chat response
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Test response"
        mock_message.tool_calls = []
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_api_call.return_value = mock_response

        response = agent.chat("I'm very angry!")

        # Should not call sentiment analysis API
        assert mock_api_call.call_count == 1  # Only the chat call, no sentiment call
        assert response == "Test response"


if __name__ == "__main__":
    pytest.main([__file__])
