"""
TyrePlex In-House ML System - Interactive Demo
Run this to see the system in action!
"""

import sys
from pathlib import Path
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")


def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def demo_ml_models():
    """Demo ML models."""
    print_header("DEMO 1: ML Models (In-House)")
    
    try:
        from src.ml_system.ml_inference import MLInferenceEngine
        
        engine = MLInferenceEngine()
        logger.success("✅ ML models loaded")
        
        # Demo 1: Complete recommendation
        print("\n🚗 Customer: 'I have a Maruti Suzuki Swift VXI'")
        print("   Agent: Let me find the best tyres for you...\n")
        
        result = engine.get_complete_recommendation(
            vehicle_make="Maruti Suzuki",
            vehicle_model="Swift",
            vehicle_variant="VXI",
            vehicle_type="Hatchback",
            fuel_type="Petrol",
            vehicle_price=700000
        )
        
        if result.get('tyre_size'):
            size = result['tyre_size']
            print(f"   ✅ Tyre Size: {size['tyre_size']} (Confidence: {size['confidence_percent']:.1f}%)")
            
            if result.get('brand_prices'):
                print(f"\n   💰 Top Recommendations:")
                for i, bp in enumerate(result['brand_prices'][:5], 1):
                    print(f"      {i}. {bp['brand']:15s} - {bp['formatted_price']:12s} (Confidence: {bp['confidence']:.1f}%)")
        
        # Demo 2: Intent classification
        print("\n\n💬 Customer Messages:")
        test_messages = [
            "I have a BMW Z4",
            "What is the price of MRF tyres?",
            "Compare Apollo and CEAT",
            "I want to book an appointment"
        ]
        
        for msg in test_messages:
            intent = engine.classify_intent(msg)
            print(f"   '{msg}'")
            print(f"   → Intent: {intent['intent']} ({intent['confidence_percent']:.1f}%)\n")
        
        logger.success("✅ ML models demo complete!")
        return True
        
    except Exception as e:
        logger.error(f"❌ ML models not available: {e}")
        logger.info("Run: ./run.sh train")
        return False


def demo_csv_processing():
    """Demo CSV processing."""
    print_header("DEMO 2: CSV Data Processing")
    
    try:
        from src.customer_service_agent.csv_tools import CSVTyrePlexTools
        
        tools = CSVTyrePlexTools()
        logger.success("✅ CSV data loaded")
        
        # Get all brands
        brands_result = tools.get_all_brands()
        if brands_result.get('success'):
            brands = brands_result['brands']
            print(f"\n📦 Available Brands ({len(brands)}):")
            for i, brand in enumerate(brands[:10], 1):
                print(f"   {i:2d}. {brand}")
            if len(brands) > 10:
                print(f"   ... and {len(brands) - 10} more")
        
        # Demo vehicle lookup
        print("\n\n🔍 Vehicle Lookup Demo:")
        print("   Customer: 'I have a BMW Z4 M40i'")
        
        result = tools.identify_vehicle_tyre_size("BMW", "Z4", "BMW Z4 M40i Petrol AT")
        
        if result.get('success'):
            print(f"   ✅ Found vehicle!")
            print(f"      Front tyre: {result['front_tyre_size']}")
            print(f"      Rear tyre: {result['rear_tyre_size']}")
            print(f"      Same size: {result['same_size']}")
            
            # Get recommendations
            print(f"\n   💰 Tyre Recommendations (Mid-range):")
            tyres = tools.get_tyre_recommendations(result['front_tyre_size'], budget_range='mid')
            
            if tyres.get('success'):
                for i, tyre in enumerate(tyres['recommendations'][:5], 1):
                    print(f"      {i}. {tyre['brand']:15s} {tyre['model']:20s} - ₹{tyre['price']:,.0f}")
        else:
            print(f"   ⚠️  Vehicle not found in database")
            print(f"      (This is OK if you don't have BMW data)")
        
        # Demo brand comparison
        print("\n\n⚖️  Brand Comparison Demo:")
        print("   Customer: 'Compare MRF and CEAT for 185/65 R15'")
        
        comparison = tools.compare_tyre_brands("185/65 R15", "MRF", "CEAT")
        
        if comparison.get('success'):
            print(f"   ✅ Comparison:")
            print(f"      MRF:  ₹{comparison['brand1']['avg_price']:,.0f} ({comparison['brand1']['count']} options)")
            print(f"      CEAT: ₹{comparison['brand2']['avg_price']:,.0f} ({comparison['brand2']['count']} options)")
            print(f"      Cheaper: {comparison['cheaper_brand']}")
            print(f"      Difference: ₹{comparison['price_difference']:,.0f}")
        
        logger.success("✅ CSV processing demo complete!")
        return True
        
    except Exception as e:
        logger.error(f"❌ CSV data not available: {e}")
        logger.info("Run: ./run.sh process")
        return False


def demo_integrated_agent():
    """Demo integrated agent."""
    print_header("DEMO 3: Integrated Agent (ML + CSV)")
    
    try:
        from src.customer_service_agent.integrated_agent import IntegratedTyrePlexAgent
        
        agent = IntegratedTyrePlexAgent()
        logger.success("✅ Integrated agent initialized")
        
        # Check status
        status = agent.get_system_status()
        print(f"\n📊 System Status:")
        print(f"   ML Available: {status['ml_available']}")
        print(f"   CSV Available: {status['csv_available']}")
        print(f"   Status: {status['recommendation']}")
        
        # Demo conversation
        print("\n\n💬 Customer Conversation Demo:")
        print("-" * 70)
        
        # Step 1: Intent classification
        print("\n👤 Customer: 'I have a Maruti Suzuki Swift VXI'")
        intent = agent.classify_customer_intent("I have a Maruti Suzuki Swift VXI")
        print(f"🤖 Agent (thinking): Intent detected - {intent['intent']}")
        
        # Step 2: Vehicle identification
        print(f"🤖 Agent: 'Great! Let me find the best tyres for your Swift...'")
        result = agent.identify_vehicle_and_recommend(
            "Maruti Suzuki", "Swift", "VXI", "mid"
        )
        
        if result.get('tyre_size'):
            print(f"🤖 Agent: 'Your Swift needs {result['tyre_size']['front']} tyres.'")
            print(f"          'Here are my top recommendations:'")
            
            if result.get('recommendations'):
                for i, rec in enumerate(result['recommendations'][:3], 1):
                    print(f"          '{i}. {rec['brand']} - ₹{rec['price']:,.0f}'")
        
        # Step 3: Brand comparison
        print(f"\n👤 Customer: 'Can you compare MRF and CEAT?'")
        comparison = agent.compare_brands("185/65 R15", "MRF", "CEAT")
        
        if comparison.get('success'):
            print(f"🤖 Agent: 'Sure! Here's the comparison:'")
            print(f"          'MRF: ₹{comparison['brand1']['price']:,.0f}'")
            print(f"          'CEAT: ₹{comparison['brand2']['price']:,.0f}'")
            print(f"          '{comparison['cheaper_brand']} is cheaper by ₹{comparison['price_difference']:,.0f}'")
        
        # Step 4: Availability check
        print(f"\n👤 Customer: 'Is MRF available?'")
        availability = agent.check_availability("MRF", "ZLX", "Delhi")
        print(f"🤖 Agent: 'Yes! MRF tyres are available.'")
        print(f"          'Delivery: {availability['delivery_time']}'")
        
        print("\n" + "-" * 70)
        
        logger.success("✅ Integrated agent demo complete!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Integrated agent error: {e}")
        return False


def demo_rest_api():
    """Demo REST API."""
    print_header("DEMO 4: REST API")
    
    print("\n📡 REST API Endpoints:")
    print("\n   Health Check:")
    print("   $ curl http://localhost:5000/health")
    
    print("\n   Vehicle Identification:")
    print("   $ curl -X POST http://localhost:5000/api/vehicle/identify \\")
    print("       -H 'Content-Type: application/json' \\")
    print("       -d '{")
    print("         \"make\": \"Maruti Suzuki\",")
    print("         \"model\": \"Swift\",")
    print("         \"variant\": \"VXI\",")
    print("         \"budget_range\": \"mid\"")
    print("       }'")
    
    print("\n   Search Vehicles:")
    print("   $ curl http://localhost:5000/api/vehicle/search?q=BMW")
    
    print("\n   Get All Brands:")
    print("   $ curl http://localhost:5000/api/brands")
    
    print("\n   Classify Intent:")
    print("   $ curl -X POST http://localhost:5000/api/intent/classify \\")
    print("       -H 'Content-Type: application/json' \\")
    print("       -d '{\"text\": \"I have a BMW Z4\"}'")
    
    print("\n   Compare Brands:")
    print("   $ curl -X POST http://localhost:5000/api/tyres/compare \\")
    print("       -H 'Content-Type: application/json' \\")
    print("       -d '{")
    print("         \"tyre_size\": \"185/65 R15\",")
    print("         \"brand1\": \"MRF\",")
    print("         \"brand2\": \"CEAT\"")
    print("       }'")
    
    print("\n   Get System Stats:")
    print("   $ curl http://localhost:5000/api/stats")
    
    print("\n\n🚀 To start the REST API:")
    print("   $ ./run.sh run")
    print("   Or:")
    print("   $ python src/api/rest_api.py")
    
    logger.success("✅ REST API demo complete!")
    return True


def main():
    """Run all demos."""
    print_header("TyrePlex In-House ML System - Interactive Demo")
    
    print("\n🎯 This demo showcases:")
    print("   1. ML Models (Brand, Price, Size, Intent)")
    print("   2. CSV Data Processing")
    print("   3. Integrated Agent (ML + CSV)")
    print("   4. REST API")
    
    print("\n📝 Note: All processing happens locally on your laptop")
    print("   No external APIs, no data leaves your machine!")
    
    input("\n\nPress Enter to start the demo...")
    
    # Run demos
    results = []
    
    results.append(demo_ml_models())
    input("\n\nPress Enter to continue...")
    
    results.append(demo_csv_processing())
    input("\n\nPress Enter to continue...")
    
    results.append(demo_integrated_agent())
    input("\n\nPress Enter to continue...")
    
    results.append(demo_rest_api())
    
    # Summary
    print_header("Demo Complete!")
    
    passed = sum(1 for r in results if r)
    total = len(results)
    
    print(f"\n✅ {passed}/{total} demos ran successfully")
    
    if passed == total:
        print("\n🎉 All systems working perfectly!")
        print("\n📝 Next Steps:")
        print("   1. Start REST API: ./run.sh run")
        print("   2. Test with curl commands shown above")
        print("   3. Integrate into your application")
        print("   4. Add Twilio for voice calls (later)")
    else:
        print("\n⚠️  Some systems not available yet")
        print("\n📝 Quick Fix:")
        print("   $ ./run.sh all")
    
    print("\n💡 For more info:")
    print("   - README.md - Full documentation")
    print("   - QUICKSTART.md - Quick start guide")
    print("   - INHOUSE_SYSTEM.md - System architecture")
    
    print("")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        logger.error(f"❌ Demo error: {e}")
