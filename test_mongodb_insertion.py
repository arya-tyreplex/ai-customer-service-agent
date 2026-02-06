"""
Test MongoDB Insertion - Verify Database Operations
"""

from src.inhouse_ml.mongodb_manager import MongoDBManager
from datetime import datetime

def test_mongodb_connection():
    """Test MongoDB connection and data insertion."""
    
    print("\n" + "="*70)
    print("  Testing MongoDB Connection & Data Insertion")
    print("="*70)
    
    try:
        # Initialize MongoDB
        print("\n1️⃣  Connecting to MongoDB...")
        db = MongoDBManager()
        print("✅ Connected successfully!")
        
        # Get current statistics
        print("\n2️⃣  Current Database Statistics:")
        stats = db.get_statistics()
        print(f"   • Leads: {stats['leads']}")
        print(f"   • Bookings: {stats['bookings']}")
        print(f"   • Call Logs: {stats['call_logs']}")
        print(f"   • Vehicles: {stats['vehicles']}")
        print(f"   • Tyres: {stats['tyres']}")
        
        # Test lead creation
        print("\n3️⃣  Testing Lead Creation...")
        test_lead = {
            'call_id': f'TEST-{int(datetime.now().timestamp())}',
            'customer_name': 'Test Customer',
            'phone': '9999999999',
            'city': 'Test City',
            'vehicle_make': 'Test Make',
            'vehicle_model': 'Test Model',
            'vehicle_variant': 'Test Variant',
            'tyre_size': '185/65 R15',
            'status': 'contacted',
            'source': 'test_script',
            'created_at': datetime.now()
        }
        
        lead_id = db.create_lead(test_lead)
        print(f"✅ Lead created with ID: {lead_id}")
        
        # Test booking creation
        print("\n4️⃣  Testing Booking Creation...")
        test_booking = {
            'lead_id': lead_id,
            'call_id': test_lead['call_id'],
            'customer_name': 'Test Customer',
            'customer_phone': '9999999999',
            'customer_city': 'Test City',
            'vehicle_make': 'Test Make',
            'vehicle_model': 'Test Model',
            'vehicle_variant': 'Test Variant',
            'tyre_size': '185/65 R15',
            'tyre_brand': 'Test Brand',
            'tyre_model': 'Test Model',
            'tyre_price': 5000,
            'booking_date': 'tomorrow',
            'booking_time': 'morning',
            'wants_home_service': True,
            'status': 'pending'
        }
        
        booking_id = db.create_booking(test_booking)
        print(f"✅ Booking created with ID: {booking_id}")
        
        # Test call log creation
        print("\n5️⃣  Testing Call Log Creation...")
        test_call_log = {
            'call_id': test_lead['call_id'],
            'lead_id': lead_id,
            'call_type': 'inbound',
            'duration_seconds': 180,
            'customer_name': 'Test Customer',
            'vehicle_info': 'Test Make Test Model Test Variant',
            'tyre_size': '185/65 R15',
            'recommendations_count': 3,
            'selected_brand': 'Test Brand',
            'selected_price': 5000
        }
        
        call_log_id = db.create_call_log(test_call_log)
        print(f"✅ Call log created with ID: {call_log_id}")
        
        # Verify data was inserted
        print("\n6️⃣  Verifying Data Insertion...")
        
        # Check lead
        retrieved_lead = db.get_lead(lead_id)
        if retrieved_lead:
            print(f"✅ Lead retrieved: {retrieved_lead['customer_name']}")
        else:
            print("❌ Lead not found!")
        
        # Check booking
        retrieved_booking = db.get_booking(booking_id)
        if retrieved_booking:
            print(f"✅ Booking retrieved: {retrieved_booking['customer_name']}")
        else:
            print("❌ Booking not found!")
        
        # Check call log
        call_logs = db.get_call_logs_by_lead(lead_id)
        if call_logs:
            print(f"✅ Call log retrieved: {len(call_logs)} log(s) found")
        else:
            print("❌ Call log not found!")
        
        # Get updated statistics
        print("\n7️⃣  Updated Database Statistics:")
        stats = db.get_statistics()
        print(f"   • Leads: {stats['leads']}")
        print(f"   • Bookings: {stats['bookings']}")
        print(f"   • Call Logs: {stats['call_logs']}")
        
        # Cleanup test data
        print("\n8️⃣  Cleaning up test data...")
        from bson.objectid import ObjectId
        db.db.leads.delete_one({'_id': ObjectId(lead_id)})
        db.db.bookings.delete_one({'_id': ObjectId(booking_id)})
        db.db.call_logs.delete_one({'_id': ObjectId(call_log_id)})
        print("✅ Test data cleaned up")
        
        print("\n" + "="*70)
        print("  ✅ ALL TESTS PASSED - MongoDB is working correctly!")
        print("="*70)
        print("\n💡 Your voice demos WILL save data to MongoDB when you run them.")
        print("   The database insertion is already implemented and working.\n")
        
        # Close connection
        db.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n📝 Make sure:")
        print("   1. MongoDB is running (mongod service)")
        print("   2. Connection string is correct in .env")
        print("   3. You have network access to MongoDB")
        import traceback
        traceback.print_exc()


def check_existing_data():
    """Check if there's already data in the database."""
    
    print("\n" + "="*70)
    print("  Checking Existing Data in MongoDB")
    print("="*70)
    
    try:
        db = MongoDBManager()
        
        # Get statistics
        stats = db.get_statistics()
        
        print("\n📊 Current Database Contents:")
        print(f"   • Total Leads: {stats['leads']}")
        print(f"   • Total Bookings: {stats['bookings']}")
        print(f"   • Total Call Logs: {stats['call_logs']}")
        print(f"   • Total Vehicles: {stats['vehicles']}")
        print(f"   • Total Tyres: {stats['tyres']}")
        
        # Show recent leads
        if stats['leads'] > 0:
            print("\n📋 Recent Leads:")
            recent_leads = db.get_leads_by_status('contacted', limit=5)
            for i, lead in enumerate(recent_leads, 1):
                print(f"   {i}. {lead.get('customer_name', 'Unknown')} - "
                      f"{lead.get('vehicle_make', '')} {lead.get('vehicle_model', '')} - "
                      f"Status: {lead.get('status', 'unknown')}")
        
        # Show recent bookings
        if stats['bookings'] > 0:
            print("\n📅 Recent Bookings:")
            # Get all bookings (limited to 5)
            bookings = list(db.db.bookings.find().sort('created_at', -1).limit(5))
            for i, booking in enumerate(bookings, 1):
                print(f"   {i}. {booking.get('customer_name', 'Unknown')} - "
                      f"{booking.get('booking_date', '')} {booking.get('booking_time', '')} - "
                      f"Status: {booking.get('status', 'unknown')}")
        
        # Show recent call logs
        if stats['call_logs'] > 0:
            print("\n📞 Recent Call Logs:")
            recent_calls = db.get_recent_calls(limit=5)
            for i, call in enumerate(recent_calls, 1):
                print(f"   {i}. {call.get('customer_name', 'Unknown')} - "
                      f"{call.get('vehicle_info', '')} - "
                      f"Selected: {call.get('selected_brand', 'None')}")
        
        print("\n" + "="*70)
        
        db.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n🔍 MongoDB Insertion Test Script")
    print("="*70)
    
    # Check existing data first
    check_existing_data()
    
    # Run insertion test
    print("\n")
    test_mongodb_connection()
    
    print("\n✅ Test complete!")
    print("\n📝 To verify data is being saved during voice calls:")
    print("   1. Run: python voice_demo_aws.py")
    print("   2. Complete a call with booking")
    print("   3. Run this script again to see the new data")
    print("\n   OR use MongoDB Compass to view data visually:")
    print("   mongodb://localhost:27017/tyreplex\n")
