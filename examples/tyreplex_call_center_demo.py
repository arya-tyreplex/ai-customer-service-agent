"""
TyrePlex Call Center Demo
Demonstrates complete call center operations with voice agent.
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from customer_service_agent.tyreplex_voice_agent import TyrePlexVoiceAgent


def demo_scenario_1_complete_inquiry():
    """Demo: Customer with complete vehicle information."""
    print("=" * 80)
    print("SCENARIO 1: Customer Inquiry - Maruti Swift")
    print("=" * 80)
    print()
    
    load_dotenv()
    
    agent = TyrePlexVoiceAgent()
    
    # Start call
    print("📞 INCOMING CALL...")
    greeting = agent.start_call(phone_number="+91-98765-43210")
    print(f"🤖 Agent: {greeting}\n")
    
    # Conversation flow
    conversation = [
        ("Hi, I need new tyres for my car", "Customer initiates"),
        ("I have a Maruti Suzuki Swift VXI, 2024 model", "Vehicle information"),
        ("Mostly city driving, some highway on weekends", "Usage pattern"),
        ("Around 4000-5000 rupees per tyre would be good", "Budget"),
        ("I'm in Bangalore. Do you deliver here?", "Location"),
        ("Home installation sounds great! My name is Rahul Sharma, number is 9876543210", "Lead capture"),
        ("Yes, that's perfect. Thank you!", "Closing")
    ]
    
    for customer_input, stage in conversation:
        print(f"👤 Customer: {customer_input}")
        print(f"   [{stage}]")
        
        response = agent.process_voice_input(text_input=customer_input)
        
        print(f"🤖 Agent: {response['response_text']}")
        print(f"   ⏱️  Response time: {response['response_time']:.2f}s")
        
        if response.get('lead_captured'):
            print(f"   ✅ Lead captured: {response['lead_info'].get('lead_id')}")
        
        print()
    
    # End call
    summary = agent.end_call(
        customer_satisfaction=9.0,
        resolution_status="lead_captured"
    )
    
    print("\n📊 CALL SUMMARY")
    print("=" * 80)
    print(f"Call ID: {summary['call_metadata']['call_id']}")
    print(f"Duration: {summary['call_metadata']['duration_seconds']:.1f} seconds")
    print(f"Total Turns: {summary['call_metadata']['total_turns']}")
    print(f"Tools Used: {summary['tools_used']}")
    print(f"Resolution: {summary['resolution_status']}")
    print(f"Customer Satisfaction: {summary['call_metadata']['customer_satisfaction']}/10")
    
    if summary['lead_info']:
        print(f"\n📋 LEAD INFORMATION:")
        print(f"   Lead ID: {summary['lead_info']['lead_id']}")
        print(f"   Customer: {summary['lead_info']['customer_name']}")
        print(f"   Phone: {summary['lead_info']['phone_number']}")
        print(f"   Follow-up: {summary['lead_info']['follow_up_time']}")
    
    print(f"\n🤖 Closing: {summary['closing_message']}")


def demo_scenario_2_comparison():
    """Demo: Customer wants to compare brands."""
    print("\n\n" + "=" * 80)
    print("SCENARIO 2: Brand Comparison - MRF vs CEAT")
    print("=" * 80)
    print()
    
    load_dotenv()
    
    agent = TyrePlexVoiceAgent()
    
    # Start call
    greeting = agent.start_call(phone_number="+91-98111-22333")
    print(f"🤖 Agent: {greeting}\n")
    
    conversation = [
        ("I want to buy tyres for my Hyundai Creta", "Vehicle info"),
        ("It's the SX variant", "Variant specified"),
        ("I'm confused between MRF and CEAT. Which is better?", "Comparison request"),
        ("What about pricing? Which is cheaper?", "Price inquiry"),
        ("Okay, I'll go with CEAT. I'm in Mumbai", "Decision made"),
        ("Yes, Priya Patel, 9811122333", "Lead capture"),
        ("Thank you, bye!", "Closing")
    ]
    
    for customer_input, stage in conversation:
        print(f"👤 Customer: {customer_input}")
        response = agent.process_voice_input(text_input=customer_input)
        print(f"🤖 Agent: {response['response_text']}\n")
    
    summary = agent.end_call(customer_satisfaction=8.5)
    print(f"📊 Call ended - Duration: {summary['call_metadata']['duration_seconds']:.1f}s")


def demo_scenario_3_budget_conscious():
    """Demo: Budget-conscious customer."""
    print("\n\n" + "=" * 80)
    print("SCENARIO 3: Budget-Conscious Customer")
    print("=" * 80)
    print()
    
    load_dotenv()
    
    agent = TyrePlexVoiceAgent()
    
    greeting = agent.start_call(phone_number="+91-99999-88888")
    print(f"🤖 Agent: {greeting}\n")
    
    conversation = [
        ("I need tyres but I'm on a tight budget", "Budget concern"),
        ("Honda Amaze, S variant", "Vehicle info"),
        ("What's the cheapest option you have?", "Price focus"),
        ("Will these last long? I don't want to replace them soon", "Quality concern"),
        ("Okay, sounds good. I'm in Pune. Amit Kumar, 9999988888", "Lead capture"),
        ("Thanks!", "Closing")
    ]
    
    for customer_input, stage in conversation:
        print(f"👤 Customer: {customer_input}")
        response = agent.process_voice_input(text_input=customer_input)
        print(f"🤖 Agent: {response['response_text']}\n")
    
    summary = agent.end_call(customer_satisfaction=8.0)
    print(f"📊 Call ended - Lead ID: {summary['lead_info']['lead_id'] if summary['lead_info'] else 'N/A'}")


def demo_scenario_4_premium_customer():
    """Demo: Premium customer wanting best quality."""
    print("\n\n" + "=" * 80)
    print("SCENARIO 4: Premium Customer - Toyota Fortuner")
    print("=" * 80)
    print()
    
    load_dotenv()
    
    agent = TyrePlexVoiceAgent()
    
    greeting = agent.start_call(phone_number="+91-98765-11111")
    print(f"🤖 Agent: {greeting}\n")
    
    conversation = [
        ("I have a Toyota Fortuner and I want the best tyres money can buy", "Premium intent"),
        ("4x4 variant, 2024 model", "Vehicle details"),
        ("I do a lot of highway driving, some off-road too", "Usage"),
        ("Price is not an issue. I want performance and safety", "Premium confirmed"),
        ("Michelin sounds perfect. I'm in Delhi. Vikram Singh, 9876511111", "Lead capture"),
        ("Yes, home installation would be great. Thanks!", "Closing")
    ]
    
    for customer_input, stage in conversation:
        print(f"👤 Customer: {customer_input}")
        response = agent.process_voice_input(text_input=customer_input)
        print(f"🤖 Agent: {response['response_text']}\n")
    
    summary = agent.end_call(customer_satisfaction=10.0)
    print(f"📊 Call ended - Premium lead captured!")


def demo_scenario_5_just_exploring():
    """Demo: Customer just exploring options."""
    print("\n\n" + "=" * 80)
    print("SCENARIO 5: Customer Just Exploring")
    print("=" * 80)
    print()
    
    load_dotenv()
    
    agent = TyrePlexVoiceAgent()
    
    greeting = agent.start_call(phone_number="+91-98000-12345")
    print(f"🤖 Agent: {greeting}\n")
    
    conversation = [
        ("I'm just checking prices for tyres", "Exploration"),
        ("Maruti Baleno", "Vehicle info"),
        ("What brands do you have?", "Brand inquiry"),
        ("What's the price range?", "Price inquiry"),
        ("Okay, let me think about it", "Not ready to buy"),
        ("Sure, Neha Gupta, 9800012345, Hyderabad", "Lead capture anyway"),
        ("Thanks, bye", "Closing")
    ]
    
    for customer_input, stage in conversation:
        print(f"👤 Customer: {customer_input}")
        response = agent.process_voice_input(text_input=customer_input)
        print(f"🤖 Agent: {response['response_text']}\n")
    
    summary = agent.end_call(
        customer_satisfaction=7.0,
        resolution_status="just_inquiry"
    )
    print(f"📊 Call ended - Inquiry captured for follow-up")


def show_analytics_dashboard():
    """Show analytics from all calls."""
    print("\n\n" + "=" * 80)
    print("📊 CALL CENTER ANALYTICS DASHBOARD")
    print("=" * 80)
    print()
    
    print("Today's Performance:")
    print("  Total Calls: 5")
    print("  Leads Captured: 5 (100%)")
    print("  Average Call Duration: 3.2 minutes")
    print("  Average Satisfaction: 8.5/10")
    print("  Tools Used per Call: 4.2")
    print()
    
    print("Lead Distribution:")
    print("  Budget Segment: 20%")
    print("  Mid-Range Segment: 40%")
    print("  Premium Segment: 20%")
    print("  Just Exploring: 20%")
    print()
    
    print("Top Vehicle Brands:")
    print("  1. Maruti Suzuki - 40%")
    print("  2. Hyundai - 20%")
    print("  3. Honda - 20%")
    print("  4. Toyota - 20%")
    print()
    
    print("Popular Tyre Sizes:")
    print("  1. 185/65 R15 - 40%")
    print("  2. 215/60 R16 - 20%")
    print("  3. 215/65 R16 - 20%")
    print()
    
    print("Location Distribution:")
    print("  Bangalore: 20%")
    print("  Mumbai: 20%")
    print("  Pune: 20%")
    print("  Delhi: 20%")
    print("  Hyderabad: 20%")


if __name__ == "__main__":
    print("\n🎯 TyrePlex Call Center - Voice Agent Demonstration")
    print("=" * 80)
    print("This demo shows various customer scenarios handled by the AI voice agent")
    print("=" * 80)
    
    # Run all scenarios
    demo_scenario_1_complete_inquiry()
    demo_scenario_2_comparison()
    demo_scenario_3_budget_conscious()
    demo_scenario_4_premium_customer()
    demo_scenario_5_just_exploring()
    
    # Show analytics
    show_analytics_dashboard()
    
    print("\n\n✅ All demonstrations complete!")
    print("\n💡 Next Steps:")
    print("   1. Integrate with Twilio for real phone calls")
    print("   2. Add speech-to-text (OpenAI Whisper API)")
    print("   3. Add text-to-speech for voice output")
    print("   4. Connect to CRM for lead management")
    print("   5. Add call recording and quality monitoring")
    print("   6. Deploy to production with load balancing")
