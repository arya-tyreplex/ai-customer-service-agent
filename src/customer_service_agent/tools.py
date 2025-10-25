"""
Tool implementations for the customer service agent.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


@dataclass
class ToolRegistry:
    """Registry for all available tools."""

    tools: Dict[str, Any] = None

    def __post_init__(self):
        if self.tools is None:
            self.tools = {}

    def register(self, name: str, function: callable, schema: Dict[str, Any]):
        """Register a tool with its function and schema."""
        self.tools[name] = {"function": function, "schema": schema}

    def get_function(self, name: str) -> callable:
        """Get tool function by name."""
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found")
        return self.tools[name]["function"]

    def get_schema(self, name: str) -> Dict[str, Any]:
        """Get tool schema by name."""
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found")
        return self.tools[name]["schema"]

    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """Get schemas for all tools."""
        return [
            {"type": "function", "function": {**schema, "name": name}}
            for name, tool_info in self.tools.items()
            for schema in [tool_info["schema"]]
        ]


class CustomerServiceTools:
    """Implementation of customer service tools."""

    def __init__(self):
        self.orders_db = self._initialize_orders_db()
        self.inventory_db = self._initialize_inventory_db()
        self.refund_requests = []

    def _initialize_orders_db(self) -> Dict[str, Dict[str, Any]]:
        """Initialize simulated orders database."""
        return {
            "ORD-12345": {
                "order_number": "ORD-12345",
                "customer_name": "John Doe",
                "product": "Wireless Headphones Pro",
                "status": "Delivered",
                "order_date": "2025-09-15",
                "delivery_date": "2025-09-18",
                "amount": 129.99,
                "tracking_number": "TRK-789012",
                "customer_email": "john.doe@example.com",
            },
            "ORD-67890": {
                "order_number": "ORD-67890",
                "customer_name": "Jane Smith",
                "product": "Smart Watch Ultra",
                "status": "In Transit",
                "order_date": "2025-10-05",
                "estimated_delivery": "2025-10-10",
                "amount": 399.99,
                "tracking_number": "TRK-456789",
                "customer_email": "jane.smith@example.com",
            },
            "ORD-11111": {
                "order_number": "ORD-11111",
                "customer_name": "Bob Johnson",
                "product": "Phone Case",
                "status": "Processing",
                "order_date": "2025-10-08",
                "estimated_delivery": "2025-10-15",
                "amount": 29.99,
                "tracking_number": None,
                "customer_email": "bob.johnson@example.com",
            },
        }

    def _initialize_inventory_db(self) -> Dict[str, Dict[str, Any]]:
        """Initialize simulated inventory database."""
        return {
            "wireless headphones": {
                "in_stock": True,
                "quantity": 45,
                "price": 129.99,
                "sku": "WH-001",
                "category": "Audio",
            },
            "smart watch": {
                "in_stock": True,
                "quantity": 12,
                "price": 399.99,
                "sku": "SW-001",
                "category": "Wearables",
            },
            "laptop": {
                "in_stock": False,
                "quantity": 0,
                "price": 1299.99,
                "restock_date": "2025-10-15",
                "sku": "LP-001",
                "category": "Computers",
            },
            "phone case": {
                "in_stock": True,
                "quantity": 250,
                "price": 29.99,
                "sku": "PC-001",
                "category": "Accessories",
            },
        }

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def lookup_order(self, order_number: str) -> str:
        """Look up order details by order number."""
        logger.info(f"Looking up order: {order_number}")

        order = self.orders_db.get(order_number)
        if order:
            return json.dumps({"success": True, "order": order})
        else:
            return json.dumps(
                {
                    "success": False,
                    "error": "Order not found",
                    "message": f"No order found with number {order_number}",
                }
            )

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def process_refund(
        self, order_number: str, reason: str, amount: Optional[float] = None
    ) -> str:
        """Process a refund for an order."""
        logger.info(f"Processing refund for order: {order_number}")

        # First lookup the order
        order_data = json.loads(self.lookup_order(order_number))

        if not order_data.get("success"):
            return json.dumps(
                {"success": False, "message": "Cannot process refund - order not found"}
            )

        # Process refund
        order = order_data["order"]
        refund_amount = amount if amount is not None else order.get("amount", 0)

        refund_request = {
            "refund_id": f"REF-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "order_number": order_number,
            "refund_amount": refund_amount,
            "reason": reason,
            "status": "Approved",
            "processing_time": "3-5 business days",
            "timestamp": datetime.now().isoformat(),
        }

        self.refund_requests.append(refund_request)

        return json.dumps(
            {
                "success": True,
                **refund_request,
                "message": "Refund has been approved and will be credited to your original payment method",
            }
        )

    @retry(
        stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=2, max=5)
    )
    def check_inventory(self, product_name: str) -> str:
        """Check if a product is in stock."""
        logger.info(f"Checking inventory for: {product_name}")

        product_key = product_name.lower()
        for key, inventory_data in self.inventory_db.items():
            if key in product_key or product_key in key:
                return json.dumps({"success": True, "product": key, **inventory_data})

        return json.dumps(
            {
                "success": False,
                "in_stock": False,
                "message": "Product not found in our inventory",
            }
        )

    def escalate_to_human(self, issue_description: str, priority: str) -> str:
        """Escalate the issue to a human agent."""
        logger.info(f"Escalating issue with priority: {priority}")

        ticket_id = f"TICKET-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # In a real implementation, this would create a ticket in your support system
        escalation_data = {
            "escalated": True,
            "ticket_id": ticket_id,
            "priority": priority,
            "issue": issue_description,
            "timestamp": datetime.now().isoformat(),
            "estimated_response_time": (
                "30 minutes" if priority in ["high", "urgent"] else "2 hours"
            ),
        }

        return json.dumps(
            {
                **escalation_data,
                "message": f"Your issue has been escalated to our support team. Ticket ID: {ticket_id}",
            }
        )

    def get_product_catalog(self) -> str:
        """Get the current product catalog."""
        catalog = {
            "products": [
                {
                    "name": "Wireless Headphones Pro",
                    "category": "Audio",
                    "price": 129.99,
                    "description": "High-quality wireless headphones with noise cancellation",
                },
                {
                    "name": "Smart Watch Ultra",
                    "category": "Wearables",
                    "price": 399.99,
                    "description": "Advanced smartwatch with health monitoring features",
                },
                {
                    "name": "Gaming Laptop Pro",
                    "category": "Computers",
                    "price": 1299.99,
                    "description": "High-performance gaming laptop",
                },
                {
                    "name": "Phone Case Premium",
                    "category": "Accessories",
                    "price": 29.99,
                    "description": "Durable protective phone case",
                },
            ]
        }

        return json.dumps(catalog)


def create_tool_registry() -> ToolRegistry:
    """Create and configure the tool registry."""
    tools = CustomerServiceTools()
    registry = ToolRegistry()

    # Register all tools
    registry.register(
        name="lookup_order",
        function=tools.lookup_order,
        schema={
            "name": "lookup_order",
            "description": "Look up order details by order number",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_number": {
                        "type": "string",
                        "description": "The order number (e.g., ORD-12345)",
                    }
                },
                "required": ["order_number"],
            },
        },
    )

    registry.register(
        name="process_refund",
        function=tools.process_refund,
        schema={
            "name": "process_refund",
            "description": "Process a refund for an order",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_number": {
                        "type": "string",
                        "description": "The order number to refund",
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for the refund",
                    },
                    "amount": {
                        "type": "number",
                        "description": "Refund amount in USD",
                    },
                },
                "required": ["order_number", "reason"],
            },
        },
    )

    registry.register(
        name="check_inventory",
        function=tools.check_inventory,
        schema={
            "name": "check_inventory",
            "description": "Check if a product is in stock",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "Name of the product",
                    }
                },
                "required": ["product_name"],
            },
        },
    )

    registry.register(
        name="escalate_to_human",
        function=tools.escalate_to_human,
        schema={
            "name": "escalate_to_human",
            "description": "Escalate the issue to a human agent",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_description": {
                        "type": "string",
                        "description": "Description of the issue to escalate",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "urgent"],
                        "description": "Priority level of the issue",
                    },
                },
                "required": ["issue_description", "priority"],
            },
        },
    )

    registry.register(
        name="get_product_catalog",
        function=tools.get_product_catalog,
        schema={
            "name": "get_product_catalog",
            "description": "Get the current product catalog",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    )

    return registry
