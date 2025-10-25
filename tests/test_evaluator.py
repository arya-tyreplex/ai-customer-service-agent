"""
Tests for performance evaluator.
"""

import pytest
from unittest.mock import Mock, patch
import json

from customer_service_agent.evaluator import PerformanceEvaluator, EvaluationMetrics
from customer_service_agent.models import EvaluationResult
from customer_service_agent.config import AgentConfig


class TestPerformanceEvaluator:
    """Test cases for PerformanceEvaluator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = AgentConfig(
            openai_api_key="test-key",
            default_model="gpt-3.5-turbo",
            evaluation_threshold=7.0,
        )
        self.mock_client = Mock()
        self.evaluator = PerformanceEvaluator(self.config, self.mock_client)

    @patch("customer_service_agent.evaluator.OpenAI")
    def test_evaluate_interaction(self, mock_openai):
        """Test evaluating an interaction."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = json.dumps(
            {
                "score": 8.5,
                "reasoning": "Helpful and accurate response",
                "improvement_suggestions": ["Could be more empathetic"],
            }
        )
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        result = self.evaluator.evaluate_interaction(
            user_input="Where is my order?",
            agent_response="Your order ORD-12345 was delivered yesterday.",
            interaction_id=1,
            tool_used="lookup_order",
            sentiment_score=0.5,
            response_time=2.1,
        )

        assert result.score == 8.5
        assert "helpful" in result.reasoning.lower()
        assert result.interaction_id == 1
        assert result.tool_used == "lookup_order"
        assert result.sentiment_score == 0.5
        assert result.response_time == 2.1
        assert len(self.evaluator.evaluation_results) == 1

    def test_evaluate_interaction_api_error(self):
        """Test evaluation when API call fails."""
        self.mock_client.chat.completions.create.side_effect = Exception("API error")

        result = self.evaluator.evaluate_interaction(
            user_input="Test input", agent_response="Test response", interaction_id=1
        )

        # Should return default result on error
        assert result.score == 5.0
        assert "failed" in result.reasoning.lower()

    def test_calculate_metrics_empty(self):
        """Test calculating metrics with no evaluations."""
        metrics = self.evaluator.calculate_metrics()

        assert metrics.total_interactions == 0
        assert metrics.average_score == 0
        assert metrics.sentiment_trend == 0
        assert metrics.tool_usage_rate == 0

    def test_calculate_metrics_with_data(self):
        """Test calculating metrics with evaluation data."""
        # Add some evaluation results
        self.evaluator.evaluation_results = [
            EvaluationResult(
                timestamp="2024-01-01T10:00:00",
                interaction_id=1,
                user_input="Test 1",
                agent_response="Response 1",
                score=8.0,
                reasoning="Good",
                tool_used="lookup_order",
                sentiment_score=0.5,
                response_time=1.5,
            ),
            EvaluationResult(
                timestamp="2024-01-01T10:01:00",
                interaction_id=2,
                user_input="Test 2",
                agent_response="Response 2",
                score=9.0,
                reasoning="Excellent",
                tool_used=None,
                sentiment_score=0.8,
                response_time=2.0,
            ),
        ]

        metrics = self.evaluator.calculate_metrics()

        assert metrics.total_interactions == 2
        assert metrics.average_score == 8.5
        assert metrics.sentiment_trend == 0.65  # (0.5 + 0.8) / 2
        assert metrics.tool_usage_rate == 0.5  # 1 out of 2 used tools
        assert metrics.escalation_rate == 0.0
        assert metrics.response_time_avg == 1.75

    def test_generate_performance_report(self):
        """Test generating performance report."""
        # Add evaluation data
        self.evaluator.evaluation_results = [
            EvaluationResult(
                timestamp="2024-01-01T10:00:00",
                interaction_id=1,
                user_input="Where is my order?",
                agent_response="It was delivered.",
                score=8.0,
                reasoning="Helpful response",
                tool_used="lookup_order",
            )
        ]

        report = self.evaluator.generate_performance_report()

        assert "summary" in report
        assert "metrics" in report
        assert "recommendations" in report
        assert report["summary"]["total_evaluated"] == 1
        assert report["metrics"]["average_score"] == 8.0

    def test_get_performance_label(self):
        """Test performance label conversion."""
        evaluator = self.evaluator

        assert evaluator._get_performance_label(9.5) == "Excellent"
        assert evaluator._get_performance_label(8.5) == "Very Good"
        assert evaluator._get_performance_label(7.5) == "Good"
        assert evaluator._get_performance_label(6.5) == "Satisfactory"
        assert evaluator._get_performance_label(5.5) == "Needs Improvement"

    def test_generate_recommendations(self):
        """Test generating recommendations."""
        metrics = EvaluationMetrics(
            average_score=6.0,
            sentiment_trend=-0.5,
            tool_usage_rate=0.2,
            escalation_rate=0.1,
        )

        recommendations = self.evaluator._generate_recommendations(metrics, [])

        assert "improving response quality" in recommendations[0].lower()
        assert "empathetic responses" in recommendations[1].lower()
        assert "effective tool usage" in recommendations[2].lower()

    def test_generate_recommendations_excellent(self):
        """Test generating recommendations for excellent performance."""
        metrics = EvaluationMetrics(
            average_score=9.0,
            sentiment_trend=0.8,
            tool_usage_rate=0.6,
            escalation_rate=0.2,
        )

        recommendations = self.evaluator._generate_recommendations(metrics, [])

        assert "maintain current performance" in recommendations[0].lower()


if __name__ == "__main__":
    pytest.main([__file__])
