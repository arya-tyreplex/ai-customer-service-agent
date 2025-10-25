"""
Basic usage example for the Customer Service Agent.
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from customer_service_agent import CustomerServiceAgent, AgentConfig


def main():
    """Demonstrate basic agent usage."""
    print("🤖 AI Customer Service Agent - Basic Usage Example")
    print("=" * 50)

    # Load environment variables
    load_dotenv()

    # Initialize agent
    print("🔄 Initializing agent...")
    agent = CustomerServiceAgent()

    print(f"✅ Agent initialized (Demo mode: {agent.is_demo_mode})")
    print(f"📊 Available tools: {', '.join(agent.get_agent_info()['available_tools'])}")
    print()

    # Example conversation
    conversations = [
        ("Hi, I'd like to check the status of my order ORD-12345", "CUST-001"),
        ("The headphones I received are broken. I need a refund!", "CUST-001"),
        ("Do you have smart watches in stock?", "CUST-002"),
        ("I was charged twice for my order! This is urgent!", "CUST-003"),
    ]

    for user_message, customer_id in conversations:
        print(f"👤 Customer {customer_id}: {user_message}")
        response = agent.chat(user_message, customer_id)
        print(f"🤖 Agent: {response}")
        print("-" * 80)

    # Show performance report
    print("\n📊 PERFORMANCE REPORT")
    print("=" * 50)
    print(agent.get_performance_report())

    # Show conversation summary
    print("\n📝 CONVERSATION SUMMARY")
    print("=" * 50)
    summary = agent.get_conversation_summary()
    print(summary)

    # Show agent info
    print("\n🔧 AGENT INFORMATION")
    print("=" * 50)
    info = agent.get_agent_info()
    for key, value in info.items():
        print(f"{key.replace('_', ' ').title()}: {value}")


if __name__ == "__main__":
    main()
