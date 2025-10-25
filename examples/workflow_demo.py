"""
Workflow execution example for the Customer Service Agent.
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from customer_service_agent import CustomerServiceAgent, WorkflowStep


def main():
    """Demonstrate workflow execution."""
    print("🤖 AI Customer Service Agent - Workflow Demo")
    print("=" * 50)

    # Load environment variables
    load_dotenv()

    # Initialize agent
    print("🔄 Initializing agent...")
    agent = CustomerServiceAgent()
    print(f"✅ Agent initialized (Demo mode: {agent.is_demo_mode})")
    print()

    # Define a complex workflow
    workflow_steps = [
        WorkflowStep(
            name="Order Lookup",
            instruction="Look up order ORD-67890 and provide details",
            required_tools=["lookup_order"],
        ),
        WorkflowStep(
            name="Inventory Check",
            instruction="Check if Smart Watch Ultra is in stock",
            required_tools=["check_inventory"],
        ),
        WorkflowStep(
            name="Customer Update",
            instruction="Based on the order status and inventory, provide a comprehensive update to the customer about their order and product availability",
        ),
        WorkflowStep(
            name="Alternative Suggestions",
            instruction="If the smart watch is out of stock, suggest similar available products",
        ),
    ]

    print("🚀 Executing workflow...")
    print()

    results = agent.execute_workflow(workflow_steps)

    # Display results
    for result in results:
        print(f"📋 Step {result.step_number}: {result.step_name}")
        print(f"   Instruction: {result.instruction}")
        print(f"   Status: {'✅ Success' if result.success else '❌ Failed'}")

        if result.error:
            print(f"   Error: {result.error}")

        # Show response preview
        response_preview = (
            result.response[:150] + "..."
            if len(result.response) > 150
            else result.response
        )
        print(f"   Response: {response_preview}")
        print()

    # Show workflow summary
    successful_steps = sum(1 for r in results if r.success)
    print(
        f"📊 Workflow Summary: {successful_steps}/{len(results)} steps completed successfully"
    )

    # Show final conversation state
    print("\n💬 Final Conversation State")
    print("=" * 50)
    history = agent.get_conversation_history()
    for msg in history[-4:]:  # Show last 4 messages
        role_icon = "👤" if msg["role"] == "user" else "🤖"
        print(f"{role_icon} {msg['role'].title()}: {msg['content'][:100]}...")


if __name__ == "__main__":
    main()
