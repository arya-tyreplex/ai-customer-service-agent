"""
MongoDB Manager for TyrePlex System
Replaces PostgreSQL with MongoDB
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger
import os


class MongoDBManager:
    """
    MongoDB manager for TyrePlex data.
    Handles vehicles, tyres, leads, bookings, and call logs.
    """
    
    def __init__(self, uri: str = None, db_name: str = "tyreplex"):
        """
        Initialize MongoDB connection.
        
        Args:
            uri: MongoDB connection URI
            db_name: Database name
        """
        self.uri = uri or os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.db_name = db_name
        self.client = None
        self.db = None
        self._connect()
    
    def _connect(self):
        """Connect to MongoDB."""
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            logger.success(f"✅ Connected to MongoDB: {self.db_name}")
            self._create_indexes()
        except ConnectionFailure as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            raise
    
    def _create_indexes(self):
        """Create indexes for better performance."""
        # Vehicles collection
        self.db.vehicles.create_index([
            ("make", ASCENDING),
            ("model", ASCENDING),
            ("variant", ASCENDING)
        ], unique=True)
        
        # Tyres collection
        self.db.tyres.create_index([
            ("brand", ASCENDING),
            ("model", ASCENDING),
            ("size", ASCENDING)
        ])
        self.db.tyres.create_index([("size", ASCENDING)])
        self.db.tyres.create_index([("price", ASCENDING)])
        
        # Leads collection
        self.db.leads.create_index([("phone", ASCENDING)])
        self.db.leads.create_index([("created_at", DESCENDING)])
        self.db.leads.create_index([("status", ASCENDING)])
        
        # Bookings collection
        self.db.bookings.create_index([("lead_id", ASCENDING)])
        self.db.bookings.create_index([("booking_date", ASCENDING)])
        self.db.bookings.create_index([("status", ASCENDING)])
        
        # Call logs collection
        self.db.call_logs.create_index([("lead_id", ASCENDING)])
        self.db.call_logs.create_index([("timestamp", DESCENDING)])
        
        logger.success("✅ Created MongoDB indexes")
    
    # Vehicle operations
    def insert_vehicle(self, vehicle_data: Dict) -> str:
        """Insert vehicle data."""
        try:
            vehicle_data['created_at'] = datetime.utcnow()
            result = self.db.vehicles.insert_one(vehicle_data)
            return str(result.inserted_id)
        except DuplicateKeyError:
            logger.warning(f"Vehicle already exists: {vehicle_data.get('make')} {vehicle_data.get('model')}")
            return None
    
    def get_vehicle(self, make: str, model: str, variant: str) -> Optional[Dict]:
        """Get vehicle by make, model, variant."""
        return self.db.vehicles.find_one({
            "make": make,
            "model": model,
            "variant": variant
        })
    
    def search_vehicles(self, query: str, limit: int = 20) -> List[Dict]:
        """Search vehicles by text."""
        regex = {"$regex": query, "$options": "i"}
        return list(self.db.vehicles.find({
            "$or": [
                {"make": regex},
                {"model": regex},
                {"variant": regex}
            ]
        }).limit(limit))
    
    # Tyre operations
    def insert_tyre(self, tyre_data: Dict) -> str:
        """Insert tyre data."""
        tyre_data['created_at'] = datetime.utcnow()
        result = self.db.tyres.insert_one(tyre_data)
        return str(result.inserted_id)
    
    def get_tyres_by_size(self, size: str, limit: int = 50) -> List[Dict]:
        """Get tyres by size."""
        return list(self.db.tyres.find({"size": size}).limit(limit))
    
    def get_tyres_by_price_range(
        self,
        size: str,
        min_price: float,
        max_price: float
    ) -> List[Dict]:
        """Get tyres by size and price range."""
        return list(self.db.tyres.find({
            "size": size,
            "price": {"$gte": min_price, "$lte": max_price}
        }).sort("price", ASCENDING))
    
    def get_tyres_by_brand(self, brand: str, limit: int = 50) -> List[Dict]:
        """Get tyres by brand."""
        return list(self.db.tyres.find({
            "brand": {"$regex": brand, "$options": "i"}
        }).limit(limit))
    
    # Lead operations
    def create_lead(self, lead_data: Dict) -> str:
        """Create a new lead."""
        lead_data['created_at'] = datetime.utcnow()
        lead_data['status'] = lead_data.get('status', 'new')
        result = self.db.leads.insert_one(lead_data)
        return str(result.inserted_id)
    
    def get_lead(self, lead_id: str) -> Optional[Dict]:
        """Get lead by ID."""
        from bson.objectid import ObjectId
        return self.db.leads.find_one({"_id": ObjectId(lead_id)})
    
    def get_lead_by_phone(self, phone: str) -> Optional[Dict]:
        """Get lead by phone number."""
        return self.db.leads.find_one({"phone": phone})
    
    def update_lead_status(self, lead_id: str, status: str) -> bool:
        """Update lead status."""
        from bson.objectid import ObjectId
        result = self.db.leads.update_one(
            {"_id": ObjectId(lead_id)},
            {"$set": {"status": status, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0
    
    def get_leads_by_status(self, status: str, limit: int = 100) -> List[Dict]:
        """Get leads by status."""
        return list(self.db.leads.find({"status": status})
                   .sort("created_at", DESCENDING)
                   .limit(limit))
    
    # Booking operations
    def create_booking(self, booking_data: Dict) -> str:
        """Create a new booking."""
        booking_data['created_at'] = datetime.utcnow()
        booking_data['status'] = booking_data.get('status', 'pending')
        result = self.db.bookings.insert_one(booking_data)
        return str(result.inserted_id)
    
    def get_booking(self, booking_id: str) -> Optional[Dict]:
        """Get booking by ID."""
        from bson.objectid import ObjectId
        return self.db.bookings.find_one({"_id": ObjectId(booking_id)})
    
    def get_bookings_by_lead(self, lead_id: str) -> List[Dict]:
        """Get all bookings for a lead."""
        return list(self.db.bookings.find({"lead_id": lead_id})
                   .sort("created_at", DESCENDING))
    
    def update_booking_status(self, booking_id: str, status: str) -> bool:
        """Update booking status."""
        from bson.objectid import ObjectId
        result = self.db.bookings.update_one(
            {"_id": ObjectId(booking_id)},
            {"$set": {"status": status, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0
    
    def get_bookings_by_date(self, date: datetime) -> List[Dict]:
        """Get bookings for a specific date."""
        start = datetime(date.year, date.month, date.day)
        end = datetime(date.year, date.month, date.day, 23, 59, 59)
        return list(self.db.bookings.find({
            "booking_date": {"$gte": start, "$lte": end}
        }).sort("booking_date", ASCENDING))
    
    # Call log operations
    def create_call_log(self, call_data: Dict) -> str:
        """Create a call log entry."""
        call_data['timestamp'] = datetime.utcnow()
        result = self.db.call_logs.insert_one(call_data)
        return str(result.inserted_id)
    
    def get_call_logs_by_lead(self, lead_id: str) -> List[Dict]:
        """Get all call logs for a lead."""
        return list(self.db.call_logs.find({"lead_id": lead_id})
                   .sort("timestamp", DESCENDING))
    
    def get_recent_calls(self, limit: int = 100) -> List[Dict]:
        """Get recent call logs."""
        return list(self.db.call_logs.find()
                   .sort("timestamp", DESCENDING)
                   .limit(limit))
    
    # Bulk operations
    def bulk_insert_vehicles(self, vehicles: List[Dict]) -> int:
        """Bulk insert vehicles."""
        for vehicle in vehicles:
            vehicle['created_at'] = datetime.utcnow()
        
        try:
            result = self.db.vehicles.insert_many(vehicles, ordered=False)
            return len(result.inserted_ids)
        except Exception as e:
            logger.warning(f"Some vehicles already exist: {e}")
            return 0
    
    def bulk_insert_tyres(self, tyres: List[Dict]) -> int:
        """Bulk insert tyres."""
        for tyre in tyres:
            tyre['created_at'] = datetime.utcnow()
        
        result = self.db.tyres.insert_many(tyres)
        return len(result.inserted_ids)
    
    # Statistics
    def get_statistics(self) -> Dict:
        """Get database statistics."""
        return {
            'vehicles': self.db.vehicles.count_documents({}),
            'tyres': self.db.tyres.count_documents({}),
            'leads': self.db.leads.count_documents({}),
            'bookings': self.db.bookings.count_documents({}),
            'call_logs': self.db.call_logs.count_documents({}),
            'leads_by_status': {
                'new': self.db.leads.count_documents({'status': 'new'}),
                'contacted': self.db.leads.count_documents({'status': 'contacted'}),
                'qualified': self.db.leads.count_documents({'status': 'qualified'}),
                'converted': self.db.leads.count_documents({'status': 'converted'})
            }
        }
    
    # Cleanup
    def clear_collection(self, collection_name: str) -> int:
        """Clear a collection."""
        result = self.db[collection_name].delete_many({})
        return result.deleted_count
    
    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


# Example usage
if __name__ == "__main__":
    # Initialize
    db = MongoDBManager()
    
    # Test vehicle insertion
    vehicle = {
        "make": "Maruti Suzuki",
        "model": "Swift",
        "variant": "VXI",
        "vehicle_type": "Hatchback",
        "fuel_type": "Petrol",
        "front_tyre_size": "185/65 R15",
        "rear_tyre_size": "185/65 R15"
    }
    
    vehicle_id = db.insert_vehicle(vehicle)
    logger.info(f"Inserted vehicle: {vehicle_id}")
    
    # Test tyre insertion
    tyre = {
        "brand": "MRF",
        "model": "ZVTV",
        "size": "185/65 R15",
        "price": 4200,
        "mrp": 4500,
        "tube_type": "Tubeless"
    }
    
    tyre_id = db.insert_tyre(tyre)
    logger.info(f"Inserted tyre: {tyre_id}")
    
    # Get statistics
    stats = db.get_statistics()
    logger.info(f"Database statistics: {stats}")
    
    # Close connection
    db.close()
