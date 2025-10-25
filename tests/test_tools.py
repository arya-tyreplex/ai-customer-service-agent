"""
Tests for customer service tools.
"""

import pytest
import json
from customer_service_agent.tools import CustomerServiceTools, create_tool_registry


class TestCustomerServiceTools:
    """Test cases for customer service tools."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tools = CustomerServiceTools()

    def test_lookup_order_exists(self):
        """Test looking up an existing order."""
        result = self.tools.lookup_order("ORD-12345")
        result_data = json.loads(result)

        assert result_data["success"] == True
        assert "order" in result_data
        assert result_data["order"]["order_number"] == "ORD-12345"
        assert result_data["order"]["customer_name"] == "John Doe"

    def test_lookup_order_not_found(self):
        """Test looking up a non-existent order."""
        result = self.tools.lookup_order("ORD-99999")
        result_data = json.loads(result)

        assert result_data["success"] == False
        assert "error" in result_data
        assert "not found" in result_data["message"].lower()

    def test_process_refund_valid_order(self):
        """Test processing refund for valid order."""
        result = self.tools.process_refund(
            order_number="ORD-12345", reason="Defective product", amount=100.00
        )
        result_data = json.loads(result)

        assert result_data["success"] == True
        assert result_data["status"] == "Approved"
        assert result_data["refund_amount"] == 100.00
        assert "REF-" in result_data["refund_id"]

    def test_process_refund_invalid_order(self):
        """Test processing refund for invalid order."""
        result = self.tools.process_refund(
            order_number="ORD-99999", reason="Defective product"
        )
        result_data = json.loads(result)

        assert result_data["success"] == False
        assert "not found" in result_data["message"].lower()

    def test_check_inventory_exists(self):
        """Test checking inventory for existing product."""
        result = self.tools.check_inventory("wireless headphones")
        result_data = json.loads(result)

        assert result_data["success"] == True
        assert result_data["in_stock"] == True
        assert result_data["quantity"] == 45

    def test_check_inventory_not_found(self):
        """Test checking inventory for non-existent product."""
        result = self.tools.check_inventory("nonexistent product")
        result_data = json.loads(result)

        assert result_data["success"] == False
        assert result_data["in_stock"] == False
        assert "not found" in result_data["message"].lower()

    def test_escalate_to_human(self):
        """Test escalating to human agent."""
        result = self.tools.escalate_to_human(
            issue_description="Payment issue", priority="high"
        )
        result_data = json.loads(result)

        assert result_data["escalated"] == True
        assert "TICKET-" in result_data["ticket_id"]
        assert result_data["priority"] == "high"
        assert "30 minutes" in result_data["estimated_response_time"]

    def test_get_product_catalog(self):
        """Test getting product catalog."""
        result = self.tools.get_product_catalog()
        result_data = json.loads(result)

        assert "products" in result_data
        assert len(result_data["products"]) > 0
        assert "name" in result_data["products"][0]
        assert "price" in result_data["products"][0]


class TestToolRegistry:
    """Test cases for tool registry."""

    def test_create_tool_registry(self):
        """Test creating tool registry."""
        registry = create_tool_registry()

        expected_tools = [
            "lookup_order",
            "process_refund",
            "check_inventory",
            "escalate_to_human",
            "get_product_catalog",
        ]

        for tool_name in expected_tools:
            assert tool_name in registry.tools
            assert callable(registry.get_function(tool_name))
            assert "name" in registry.get_schema(tool_name)

    def test_get_nonexistent_tool(self):
        """Test getting non-existent tool."""
        registry = create_tool_registry()

        with pytest.raises(ValueError, match="Tool 'nonexistent' not found"):
            registry.get_function("nonexistent")

    def test_get_all_schemas(self):
        """Test getting all tool schemas."""
        registry = create_tool_registry()
        schemas = registry.get_all_schemas()

        assert len(schemas) == 5  # Should have 5 tools
        assert all("function" in schema for schema in schemas)
        assert all("name" in schema["function"] for schema in schemas)


if __name__ == "__main__":
    pytest.main([__file__])
