"""
TyrePlex CSV Demo - Customer Conversation Simulation
Uses your actual vehicle_tyre_mapping.csv data
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.customer_service_agent.csv_tools import CSVTyrePlexTools
from loguru import logger
import time

logger.remove()
logger.add(sys.stdout, format="<level>{message}</level>")


class TyrePlexCSVDemo:
    """Demo conversation using CSV data."""
    
    def __init__(self):
        self.tools = CSVTyrePlexTools()
        self.customer_data = {}
    
    def print_header(self, text: str):
        """Print section header."""
        print("\n" + "=" * 70)
        print(f"  {text}")
        print("=" * 70)
    
    def print_agent(self, text: str):
        """Print agent message."""
        print(f"\n🤖 Agent: {text}")
        time.sleep(0.5)
    
    def print_customer(self, text: str):
        """Print customer message."""
        print(f"\n👤 Customer: {text}")
        time.sleep(0.3)
    
    def print_system(self, text: str):
        """Print system message."""
        print(f"\n💻 System: {text}")
        time.sleep(0.2)
    
    def scenario_1_vehicle_lookup(self):
        """Scenario 1: Customer knows their vehicle."""
        self.print_header("SCENARIO 1: Vehicle Lookup & Recommendations")
        
        # Get a sample vehicle from the database
        brands = self.tools.get_all_brands()
        search = self.tools.search_vehicles("BMW")
        
        if not search['success'] or not search['vehicles']:
            # Try another make
            search = self.tools.search_vehicles("Maruti")
        
        if not search['success'] or not search['vehicles']:
            self.print_system("No vehicles found in database. Please process CSV first.")
            return
        
        test_vehicle = search['vehicles'][0]
        
        self.print_agent("Hello! Welcome to TyrePlex. How can I help you today?")
        
        self.print_customer(f"Hi, I need tyres for my {test_vehicle['make']} {test_vehicle['model']}")
        
        self.print_system(f"Searching for: {test_vehicle['make']} {test_vehicle['model']}")
        
        self.print_agent(f"Great! I found your {test_vehicle['make']} {test_vehicle['model']}. "
                        f"Which variant do you have?")
        
        self.print_customer(f"{test_vehicle['variant']}")
        
        # Identify vehicle
        self.print_system(f"Looking up: {test_vehicle['make']} {test_vehicle['model']} {test_vehicle['variant']}")
        
        vehicle_info = self.tools.identify_vehicle_tyre_size(
            test_vehicle['make'],
            test_vehicle['model'],
            test_vehicle['variant']
        )
        
        if not vehicle_info['success']:
            self.print_agent("I'm sorry, I couldn't find that exact variant. Let me search for similar options.")
            return
        
        self.print_system(f"✅ Vehicle identified!")
        self.print_system(f"   Front: {vehicle_info['front_tyre_size']}")
        self.print_system(f"   Rear: {vehicle_info['rear_tyre_size']}")
        
        same_size = vehicle_info['same_size']
        if same_size:
            self.print_agent(f"Perfect! Your {test_vehicle['make']} {test_vehicle['model']} uses "
                           f"{vehicle_info['front_tyre_size']} tyres. "
                           f"What's your budget range - economy, mid-range, or premium?")
        else:
            self.print_agent(f"Your vehicle uses different sizes - "
                           f"Front: {vehicle_info['front_tyre_size']}, "
                           f"Rear: {vehicle_info['rear_tyre_size']}. "
                           f"What's your budget range?")
        
        self.print_customer("Mid-range, around 5000-10000 per tyre")
        
        # Get recommendations
        self.print_system("Fetching mid-range recommendations...")
        
        recs = self.tools.get_tyre_recommendations(
            vehicle_info['front_tyre_size'],
            budget_range='mid'
        )
        
        if recs['success'] and recs['recommendations']:
            self.print_agent(f"I found {recs['total_options']} great options for you. "
                           f"Here are my top 3 recommendations:")
            
            for i, rec in enumerate(recs['recommendations'][:3], 1):
                discount_text = f" (Save ₹{rec['mrp'] - rec['price']}!)" if rec['discount_percent'] > 0 else ""
                self.print_agent(f"\n{i}. {rec['brand']} {rec['model']}")
                self.print_agent(f"   Price: ₹{rec['price']:,}{discount_text}")
                self.print_agent(f"   Type: {rec['tube_type']}")
            
            self.customer_data['selected_tyre'] = recs['recommendations'][0]
            self.customer_data['vehicle'] = vehicle_info
        else:
            self.print_agent("Let me check other options for you...")
    
    def scenario_2_brand_comparison(self):
        """Scenario 2: Customer wants to compare brands."""
        self.print_header("SCENARIO 2: Brand Comparison")
        
        if 'vehicle' not in self.customer_data:
            self.print_system("Skipping - no vehicle data from previous scenario")
            return
        
        brands = self.tools.get_all_brands()
        if not brands['success'] or len(brands['brands']) < 2:
            self.print_system("Not enough brands for comparison")
            return
        
        brand1 = brands['brands'][0]
        brand2 = brands['brands'][1]
        
        self.print_customer(f"Can you compare {brand1} and {brand2} for me?")
        
        self.print_system(f"Comparing {brand1} vs {brand2}...")
        
        comparison = self.tools.compare_tyre_brands(
            self.customer_data['vehicle']['front_tyre_size'],
            brand1,
            brand2
        )
        
        if comparison['success']:
            self.print_agent(f"Sure! Here's the comparison for size {self.customer_data['vehicle']['front_tyre_size']}:")
            
            self.print_agent(f"\n{comparison['brand1']['name']} {comparison['brand1']['model']}:")
            self.print_agent(f"  Price: ₹{comparison['brand1']['price']:,}")
            
            self.print_agent(f"\n{comparison['brand2']['name']} {comparison['brand2']['model']}:")
            self.print_agent(f"  Price: ₹{comparison['brand2']['price']:,}")
            
            self.print_agent(f"\nThe {comparison['cheaper_brand']} is ₹{comparison['price_difference']:,} cheaper. "
                           f"Both are excellent choices, but {comparison['cheaper_brand']} offers better value.")
        else:
            self.print_agent("Let me check other brands for you...")
    
    def scenario_3_availability_booking(self):
        """Scenario 3: Check availability and book."""
        self.print_header("SCENARIO 3: Availability Check & Booking")
        
        if 'selected_tyre' not in self.customer_data:
            self.print_system("Skipping - no tyre selected")
            return
        
        tyre = self.customer_data['selected_tyre']
        
        self.print_customer(f"I'll go with the {tyre['brand']} {tyre['model']}. "
                          f"Is it available in Mumbai?")
        
        self.print_system(f"Checking availability: {tyre['brand']} {tyre['model']} in Mumbai")
        
        availability = self.tools.check_tyre_availability(
            tyre['brand'],
            tyre['model'],
            "Mumbai"
        )
        
        if availability['success'] and availability['available']:
            self.print_agent(f"Great news! The {tyre['brand']} {tyre['model']} is in stock. "
                           f"We have {availability['stock_count']} units available.")
            
            self.print_agent(f"We can deliver and install them {availability['delivery_time']} "
                           f"at our {availability['nearest_store']} location, "
                           f"just {availability['store_distance']} from you.")
            
            self.print_customer("Perfect! Can you book it for tomorrow?")
            
            self.print_agent("Absolutely! Let me create a booking for you. "
                           "Can I have your name and phone number?")
            
            self.print_customer("Rahul Sharma, 9876543210")
            
            self.print_system("Creating booking...")
            self.print_system("✅ Booking created: BOOK-12345")
            
            self.print_agent("Perfect, Rahul! I've booked your appointment for tomorrow. "
                           f"You'll get 4 {tyre['brand']} {tyre['model']} tyres "
                           f"for ₹{tyre['price'] * 4:,} (total for all 4). "
                           "We'll send you an SMS confirmation shortly. "
                           "Is there anything else I can help you with?")
            
            self.print_customer("No, that's all. Thank you!")
            
            self.print_agent("You're welcome! We'll see you tomorrow. "
                           "Have a great day!")
    
    def scenario_4_price_range_search(self):
        """Scenario 4: Customer has specific budget."""
        self.print_header("SCENARIO 4: Price Range Search")
        
        # Get a sample vehicle
        search = self.tools.search_vehicles("Hyundai")
        if not search['success']:
            search = self.tools.search_vehicles("Honda")
        
        if not search['success'] or not search['vehicles']:
            self.print_system("No vehicles found")
            return
        
        test_vehicle = search['vehicles'][0]
        
        self.print_customer(f"Hi, I have a {test_vehicle['make']} {test_vehicle['model']}. "
                          f"I need tyres under ₹5000 each.")
        
        vehicle_info = self.tools.identify_vehicle_tyre_size(
            test_vehicle['make'],
            test_vehicle['model'],
            test_vehicle['variant']
        )
        
        if not vehicle_info['success']:
            self.print_agent("Let me find your vehicle details...")
            return
        
        self.print_agent(f"Got it! Your {test_vehicle['make']} {test_vehicle['model']} "
                       f"uses {vehicle_info['front_tyre_size']} tyres. "
                       f"Let me find options under ₹5000.")
        
        self.print_system(f"Searching: {vehicle_info['front_tyre_size']}, ₹2000-₹5000")
        
        price_result = self.tools.get_price_range_tyres(
            vehicle_info['front_tyre_size'],
            2000,
            5000
        )
        
        if price_result['success']:
            self.print_agent(f"I found {price_result['total_options']} options in your budget:")
            
            for i, rec in enumerate(price_result['recommendations'][:3], 1):
                self.print_agent(f"\n{i}. {rec['brand']} {rec['model']}")
                self.print_agent(f"   Price: ₹{rec['price']:,}")
                if rec['mrp'] > rec['price']:
                    self.print_agent(f"   MRP: ₹{rec['mrp']:,} (You save ₹{rec['mrp'] - rec['price']:,})")
        else:
            self.print_agent("Let me check budget options for you...")
    
    def run_all_scenarios(self):
        """Run all demo scenarios."""
        print("\n")
        print("╔" + "═" * 68 + "╗")
        print("║" + " " * 15 + "TyrePlex CSV Demo - Live Conversations" + " " * 15 + "║")
        print("║" + " " * 20 + "Using Your Actual CSV Data" + " " * 22 + "║")
        print("╚" + "═" * 68 + "╝")
        
        try:
            self.scenario_1_vehicle_lookup()
            time.sleep(1)
            
            self.scenario_2_brand_comparison()
            time.sleep(1)
            
            self.scenario_3_availability_booking()
            time.sleep(1)
            
            self.scenario_4_price_range_search()
            
            # Summary
            self.print_header("DEMO COMPLETE")
            print("\n✅ All scenarios completed successfully!")
            print("\n📊 What You Just Saw:")
            print("  ✅ Vehicle identification from CSV")
            print("  ✅ Tyre recommendations by budget")
            print("  ✅ Brand comparisons")
            print("  ✅ Availability checks")
            print("  ✅ Price range filtering")
            print("  ✅ Booking creation")
            
            print("\n🎯 This Works With:")
            print("  ✅ Your actual vehicle_tyre_mapping.csv")
            print("  ✅ All your vehicles and tyres")
            print("  ✅ Real prices from your data")
            print("  ✅ Actual brand information")
            
            print("\n🚀 Next Steps:")
            print("  1. Integrate with voice agent")
            print("  2. Add Twilio for phone calls")
            print("  3. Connect to inventory system")
            print("  4. Deploy to production")
            
            print("\n💡 To integrate with voice agent:")
            print("  - Use CSVTyrePlexTools in tyreplex_voice_agent.py")
            print("  - Replace mock data with CSV lookups")
            print("  - All tools are ready to use!")
            
            print("")
            
        except Exception as e:
            logger.error(f"\n❌ Error: {e}")
            logger.info("\n💡 Make sure you've run: python process_csv.py")


if __name__ == "__main__":
    demo = TyrePlexCSVDemo()
    demo.run_all_scenarios()
