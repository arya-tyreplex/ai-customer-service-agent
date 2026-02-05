"""
Database management for TyrePlex bidirectional calling system.
Handles leads, bookings, and call logs using PostgreSQL.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
from loguru import logger


class DatabaseManager:
    """Manages PostgreSQL database connections and operations."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "tyreplex_calls",
        user: str = "postgres",
        password: str = "postgres"
    ):
        """Initialize database connection."""
        self.connection_params = {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password
        }
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Establish database connection."""
        try:
            self.conn = psycopg2.connect(**self.connection_params)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            logger.info("Database connected successfully")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def disconnect(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("Database disconnected")
    
    def create_tables(self):
        """Create all required tables."""
        
        # Leads table
        leads_table = """
        CREATE TABLE IF NOT EXISTS leads (
            lead_id VARCHAR(50) PRIMARY KEY,
            customer_name VARCHAR(100),
            phone_number VARCHAR(20),
            email VARCHAR(100),
            
            -- Vehicle info
            vehicle_make VARCHAR(50),
            vehicle_model VARCHAR(50),
            vehicle_variant VARCHAR(50),
            vehicle_type VARCHAR(50),
            
            -- Tyre info
            tyre_size VARCHAR(20),
            recommended_brand VARCHAR(50),
            recommended_model VARCHAR(50),
            recommended_price DECIMAL(10,2),
            
            -- Location
            city VARCHAR(50),
            address TEXT,
            pincode VARCHAR(10),
            
            -- Lead details
            source VARCHAR(20),
            status VARCHAR(20),
            urgency VARCHAR(20),
            budget_range VARCHAR(20),
            
            -- Timestamps
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_contacted TIMESTAMP,
            next_follow_up TIMESTAMP,
            
            -- Call tracking
            inbound_call_id VARCHAR(50),
            outbound_call_id VARCHAR(50),
            total_calls INT DEFAULT 0,
            
            -- Notes
            notes TEXT
        );
        
        CREATE INDEX IF NOT EXISTS idx_leads_phone ON leads(phone_number);
        CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
        CREATE INDEX IF NOT EXISTS idx_leads_next_follow_up ON leads(next_follow_up);
        """
        
        # Bookings table
        bookings_table = """
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id VARCHAR(50) PRIMARY KEY,
            lead_id VARCHAR(50),
            
            -- Customer info
            customer_name VARCHAR(100),
            phone_number VARCHAR(20),
            address TEXT,
            city VARCHAR(50),
            pincode VARCHAR(10),
            
            -- Booking details
            booking_date DATE,
            booking_time_slot VARCHAR(20),
            service_type VARCHAR(20),
            
            -- Tyre details
            tyre_brand VARCHAR(50),
            tyre_model VARCHAR(50),
            tyre_size VARCHAR(20),
            quantity INT,
            price_per_tyre DECIMAL(10,2),
            total_price DECIMAL(10,2),
            
            -- Services included
            includes_alignment BOOLEAN DEFAULT TRUE,
            includes_balancing BOOLEAN DEFAULT TRUE,
            includes_disposal BOOLEAN DEFAULT TRUE,
            
            -- Status
            status VARCHAR(20),
            payment_status VARCHAR(20),
            
            -- Timestamps
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            confirmed_at TIMESTAMP,
            completed_at TIMESTAMP,
            
            -- Technician assignment
            technician_id VARCHAR(50),
            technician_name VARCHAR(100),
            
            -- Notes
            special_instructions TEXT,
            
            FOREIGN KEY (lead_id) REFERENCES leads(lead_id)
        );
        
        CREATE INDEX IF NOT EXISTS idx_bookings_date ON bookings(booking_date);
        CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status);
        """
        
        # Call logs table
        call_logs_table = """
        CREATE TABLE IF NOT EXISTS call_logs (
            call_id VARCHAR(50) PRIMARY KEY,
            lead_id VARCHAR(50),
            
            -- Call details
            call_type VARCHAR(20),
            phone_number VARCHAR(20),
            call_status VARCHAR(20),
            
            -- Duration
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            duration_seconds INT,
            
            -- Conversation
            transcript TEXT,
            intent_detected VARCHAR(50),
            sentiment VARCHAR(20),
            
            -- Tools used
            tools_used JSONB,
            
            -- Outcome
            outcome VARCHAR(50),
            booking_id VARCHAR(50),
            
            -- Quality
            customer_satisfaction INT,
            
            -- Recording
            recording_url VARCHAR(255),
            
            FOREIGN KEY (lead_id) REFERENCES leads(lead_id)
        );
        
        CREATE INDEX IF NOT EXISTS idx_call_logs_type ON call_logs(call_type);
        CREATE INDEX IF NOT EXISTS idx_call_logs_start_time ON call_logs(start_time);
        """
        
        try:
            self.cursor.execute(leads_table)
            self.cursor.execute(bookings_table)
            self.cursor.execute(call_logs_table)
            self.conn.commit()
            logger.info("✅ All tables created successfully")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to create tables: {e}")
            raise
    
    # ==================== LEAD OPERATIONS ====================
    
    def create_lead(self, lead_data: Dict[str, Any]) -> str:
        """Create a new lead."""
        query = """
        INSERT INTO leads (
            lead_id, customer_name, phone_number, email,
            vehicle_make, vehicle_model, vehicle_variant, vehicle_type,
            tyre_size, recommended_brand, recommended_model, recommended_price,
            city, address, pincode,
            source, status, urgency, budget_range,
            next_follow_up, notes
        ) VALUES (
            %(lead_id)s, %(customer_name)s, %(phone_number)s, %(email)s,
            %(vehicle_make)s, %(vehicle_model)s, %(vehicle_variant)s, %(vehicle_type)s,
            %(tyre_size)s, %(recommended_brand)s, %(recommended_model)s, %(recommended_price)s,
            %(city)s, %(address)s, %(pincode)s,
            %(source)s, %(status)s, %(urgency)s, %(budget_range)s,
            %(next_follow_up)s, %(notes)s
        )
        """
        
        try:
            self.cursor.execute(query, lead_data)
            self.conn.commit()
            logger.info(f"✅ Lead created: {lead_data['lead_id']}")
            return lead_data['lead_id']
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to create lead: {e}")
            raise
    
    def get_lead(self, lead_id: str) -> Optional[Dict]:
        """Get lead by ID."""
        query = "SELECT * FROM leads WHERE lead_id = %s"
        
        try:
            self.cursor.execute(query, (lead_id,))
            return dict(self.cursor.fetchone()) if self.cursor.rowcount > 0 else None
        except Exception as e:
            logger.error(f"Failed to get lead: {e}")
            return None
    
    def get_lead_by_phone(self, phone_number: str) -> Optional[Dict]:
        """Get lead by phone number."""
        query = "SELECT * FROM leads WHERE phone_number = %s ORDER BY created_at DESC LIMIT 1"
        
        try:
            self.cursor.execute(query, (phone_number,))
            return dict(self.cursor.fetchone()) if self.cursor.rowcount > 0 else None
        except Exception as e:
            logger.error(f"Failed to get lead by phone: {e}")
            return None
    
    def update_lead(self, lead_id: str, updates: Dict[str, Any]):
        """Update lead information."""
        set_clause = ", ".join([f"{key} = %({key})s" for key in updates.keys()])
        query = f"UPDATE leads SET {set_clause} WHERE lead_id = %(lead_id)s"
        
        updates['lead_id'] = lead_id
        
        try:
            self.cursor.execute(query, updates)
            self.conn.commit()
            logger.info(f"✅ Lead updated: {lead_id}")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to update lead: {e}")
            raise
    
    def get_leads_for_followup(self, limit: int = 50) -> List[Dict]:
        """Get leads that need follow-up calls."""
        query = """
        SELECT * FROM leads
        WHERE status IN ('new', 'contacted')
        AND next_follow_up <= NOW()
        AND total_calls < 3
        ORDER BY urgency DESC, created_at ASC
        LIMIT %s
        """
        
        try:
            self.cursor.execute(query, (limit,))
            return [dict(row) for row in self.cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get leads for follow-up: {e}")
            return []
    
    # ==================== BOOKING OPERATIONS ====================
    
    def create_booking(self, booking_data: Dict[str, Any]) -> str:
        """Create a new booking."""
        query = """
        INSERT INTO bookings (
            booking_id, lead_id,
            customer_name, phone_number, address, city, pincode,
            booking_date, booking_time_slot, service_type,
            tyre_brand, tyre_model, tyre_size, quantity,
            price_per_tyre, total_price,
            includes_alignment, includes_balancing, includes_disposal,
            status, payment_status,
            special_instructions
        ) VALUES (
            %(booking_id)s, %(lead_id)s,
            %(customer_name)s, %(phone_number)s, %(address)s, %(city)s, %(pincode)s,
            %(booking_date)s, %(booking_time_slot)s, %(service_type)s,
            %(tyre_brand)s, %(tyre_model)s, %(tyre_size)s, %(quantity)s,
            %(price_per_tyre)s, %(total_price)s,
            %(includes_alignment)s, %(includes_balancing)s, %(includes_disposal)s,
            %(status)s, %(payment_status)s,
            %(special_instructions)s
        )
        """
        
        try:
            self.cursor.execute(query, booking_data)
            self.conn.commit()
            logger.info(f"✅ Booking created: {booking_data['booking_id']}")
            return booking_data['booking_id']
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to create booking: {e}")
            raise
    
    def get_booking(self, booking_id: str) -> Optional[Dict]:
        """Get booking by ID."""
        query = "SELECT * FROM bookings WHERE booking_id = %s"
        
        try:
            self.cursor.execute(query, (booking_id,))
            return dict(self.cursor.fetchone()) if self.cursor.rowcount > 0 else None
        except Exception as e:
            logger.error(f"Failed to get booking: {e}")
            return None
    
    def update_booking(self, booking_id: str, updates: Dict[str, Any]):
        """Update booking information."""
        set_clause = ", ".join([f"{key} = %({key})s" for key in updates.keys()])
        query = f"UPDATE bookings SET {set_clause} WHERE booking_id = %(booking_id)s"
        
        updates['booking_id'] = booking_id
        
        try:
            self.cursor.execute(query, updates)
            self.conn.commit()
            logger.info(f"✅ Booking updated: {booking_id}")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to update booking: {e}")
            raise
    
    def get_upcoming_bookings(self, days: int = 7) -> List[Dict]:
        """Get upcoming bookings."""
        query = """
        SELECT * FROM bookings
        WHERE booking_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '%s days'
        AND status IN ('pending', 'confirmed')
        ORDER BY booking_date, booking_time_slot
        """
        
        try:
            self.cursor.execute(query, (days,))
            return [dict(row) for row in self.cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get upcoming bookings: {e}")
            return []
    
    # ==================== CALL LOG OPERATIONS ====================
    
    def save_call_log(self, call_data: Dict[str, Any]) -> str:
        """Save call log."""
        query = """
        INSERT INTO call_logs (
            call_id, lead_id,
            call_type, phone_number, call_status,
            start_time, end_time, duration_seconds,
            transcript, intent_detected, sentiment,
            tools_used, outcome, booking_id,
            customer_satisfaction, recording_url
        ) VALUES (
            %(call_id)s, %(lead_id)s,
            %(call_type)s, %(phone_number)s, %(call_status)s,
            %(start_time)s, %(end_time)s, %(duration_seconds)s,
            %(transcript)s, %(intent_detected)s, %(sentiment)s,
            %(tools_used)s, %(outcome)s, %(booking_id)s,
            %(customer_satisfaction)s, %(recording_url)s
        )
        """
        
        try:
            # Convert tools_used to JSON if it's a list/dict
            if 'tools_used' in call_data and isinstance(call_data['tools_used'], (list, dict)):
                call_data['tools_used'] = json.dumps(call_data['tools_used'])
            
            self.cursor.execute(query, call_data)
            self.conn.commit()
            logger.info(f"✅ Call log saved: {call_data['call_id']}")
            return call_data['call_id']
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to save call log: {e}")
            raise
    
    def get_call_logs(self, lead_id: str) -> List[Dict]:
        """Get all call logs for a lead."""
        query = """
        SELECT * FROM call_logs
        WHERE lead_id = %s
        ORDER BY start_time DESC
        """
        
        try:
            self.cursor.execute(query, (lead_id,))
            return [dict(row) for row in self.cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get call logs: {e}")
            return []


# Example usage
if __name__ == "__main__":
    # Initialize database
    db = DatabaseManager()
    db.connect()
    
    # Create tables
    db.create_tables()
    
    # Test lead creation
    lead_data = {
        'lead_id': f"LEAD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'customer_name': 'Rahul Sharma',
        'phone_number': '+91-9876543210',
        'email': 'rahul@example.com',
        'vehicle_make': 'Maruti Suzuki',
        'vehicle_model': 'Swift',
        'vehicle_variant': 'VXI',
        'vehicle_type': 'Hatchback',
        'tyre_size': '185/65 R15',
        'recommended_brand': 'MRF',
        'recommended_model': 'ZVTV',
        'recommended_price': 4200.00,
        'city': 'Bangalore',
        'address': 'Koramangala',
        'pincode': '560034',
        'source': 'inbound',
        'status': 'new',
        'urgency': 'within_week',
        'budget_range': 'mid',
        'next_follow_up': datetime.now() + timedelta(hours=2),
        'notes': 'Interested in MRF tyres'
    }
    
    lead_id = db.create_lead(lead_data)
    print(f"✅ Created lead: {lead_id}")
    
    # Test lead retrieval
    lead = db.get_lead(lead_id)
    print(f"✅ Retrieved lead: {lead['customer_name']}")
    
    db.disconnect()
