"""
Outbound call scheduler and dialer for TyrePlex.
Automatically schedules and makes follow-up calls to leads.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import time
from loguru import logger
from database import DatabaseManager


class OutboundCallScheduler:
    """Automatically schedules and makes outbound calls."""
    
    def __init__(self, db: DatabaseManager):
        """
        Initialize outbound call scheduler.
        
        Args:
            db: Database manager instance
        """
        self.db = db
        self.business_hours = {
            'start': 9,  # 9 AM
            'end': 19,   # 7 PM
            'days': [0, 1, 2, 3, 4, 5]  # Monday-Saturday (0=Monday, 6=Sunday)
        }
    
    def check_for_follow_ups(self) -> List[Dict]:
        """
        Check for leads that need follow-up calls.
        
        Returns:
            List of leads to call
        """
        logger.info("Checking for leads needing follow-up...")
        
        # Get leads from database
        leads = self.db.get_leads_for_followup(limit=50)
        
        logger.info(f"Found {len(leads)} leads needing follow-up")
        
        return leads
    
    def schedule_outbound_call(self, lead: Dict) -> Optional[str]:
        """
        Schedule an outbound call to a lead.
        
        Args:
            lead: Lead dictionary
            
        Returns:
            Call ID if scheduled, None if not
        """
        lead_id = lead['lead_id']
        phone_number = lead['phone_number']
        
        logger.info(f"Scheduling outbound call for lead: {lead_id}")
        
        # Check business hours
        if not self.is_business_hours():
            next_time = self.get_next_business_hour()
            logger.info(f"Outside business hours. Rescheduling for {next_time}")
            
            self.db.update_lead(lead_id, {
                'next_follow_up': next_time
            })
            return None
        
        # Generate call ID
        call_id = f"OUT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Update lead
        self.db.update_lead(lead_id, {
            'last_contacted': datetime.now(),
            'total_calls': lead['total_calls'] + 1,
            'outbound_call_id': call_id
        })
        
        logger.info(f"✅ Scheduled outbound call: {call_id}")
        
        return call_id
    
    def is_business_hours(self) -> bool:
        """
        Check if current time is within business hours.
        
        Returns:
            True if within business hours
        """
        now = datetime.now()
        
        # Check day of week (Monday=0, Sunday=6)
        if now.weekday() not in self.business_hours['days']:
            return False
        
        # Check time
        if self.business_hours['start'] <= now.hour < self.business_hours['end']:
            return True
        
        return False
    
    def get_next_business_hour(self) -> datetime:
        """
        Get next available business hour.
        
        Returns:
            Next business hour datetime
        """
        now = datetime.now()
        
        # If after business hours today, schedule for next day 9 AM
        if now.hour >= self.business_hours['end']:
            next_time = now + timedelta(days=1)
            next_time = next_time.replace(
                hour=self.business_hours['start'],
                minute=0,
                second=0,
                microsecond=0
            )
        # If before business hours, schedule for today 9 AM
        elif now.hour < self.business_hours['start']:
            next_time = now.replace(
                hour=self.business_hours['start'],
                minute=0,
                second=0,
                microsecond=0
            )
        # If Sunday, schedule for Monday 9 AM
        elif now.weekday() == 6:
            next_time = now + timedelta(days=1)
            next_time = next_time.replace(
                hour=self.business_hours['start'],
                minute=0,
                second=0,
                microsecond=0
            )
        else:
            # Within business hours, schedule for 1 hour later
            next_time = now + timedelta(hours=1)
        
        # Skip Sunday if next_time falls on Sunday
        if next_time.weekday() == 6:
            next_time = next_time + timedelta(days=1)
        
        return next_time
    
    def schedule_follow_up(
        self,
        lead_id: str,
        delay_hours: int = 2
    ):
        """
        Schedule a follow-up call for a lead.
        
        Args:
            lead_id: Lead ID
            delay_hours: Hours to wait before follow-up
        """
        follow_up_time = datetime.now() + timedelta(hours=delay_hours)
        
        # Adjust to business hours if needed
        if not self._is_time_in_business_hours(follow_up_time):
            follow_up_time = self._adjust_to_business_hours(follow_up_time)
        
        self.db.update_lead(lead_id, {
            'next_follow_up': follow_up_time
        })
        
        logger.info(f"✅ Follow-up scheduled for {lead_id} at {follow_up_time}")
    
    def schedule_reminder(
        self,
        booking_id: str,
        reminder_time: str = '1_day_before'
    ):
        """
        Schedule a reminder call for a booking.
        
        Args:
            booking_id: Booking ID
            reminder_time: When to remind ('1_day_before', '2_hours_before')
        """
        booking = self.db.get_booking(booking_id)
        if not booking:
            logger.error(f"Booking not found: {booking_id}")
            return
        
        booking_datetime = datetime.combine(
            booking['booking_date'],
            datetime.strptime(booking['booking_time_slot'].split('-')[0], '%H:%M').time()
        )
        
        if reminder_time == '1_day_before':
            reminder_datetime = booking_datetime - timedelta(days=1)
        elif reminder_time == '2_hours_before':
            reminder_datetime = booking_datetime - timedelta(hours=2)
        else:
            reminder_datetime = booking_datetime - timedelta(hours=24)
        
        # Create reminder lead
        lead_data = {
            'lead_id': f"REMINDER-{booking_id}",
            'customer_name': booking['customer_name'],
            'phone_number': booking['phone_number'],
            'email': None,
            'vehicle_make': None,
            'vehicle_model': None,
            'vehicle_variant': None,
            'vehicle_type': None,
            'tyre_size': booking['tyre_size'],
            'recommended_brand': booking['tyre_brand'],
            'recommended_model': booking['tyre_model'],
            'recommended_price': booking['price_per_tyre'],
            'city': booking['city'],
            'address': booking['address'],
            'pincode': booking['pincode'],
            'source': 'reminder',
            'status': 'reminder_pending',
            'urgency': 'immediate',
            'budget_range': None,
            'next_follow_up': reminder_datetime,
            'notes': f"Reminder for booking {booking_id}"
        }
        
        try:
            self.db.create_lead(lead_data)
            logger.info(f"✅ Reminder scheduled for booking {booking_id} at {reminder_datetime}")
        except Exception as e:
            logger.error(f"Failed to schedule reminder: {e}")
    
    def _is_time_in_business_hours(self, dt: datetime) -> bool:
        """Check if datetime is in business hours."""
        if dt.weekday() not in self.business_hours['days']:
            return False
        if self.business_hours['start'] <= dt.hour < self.business_hours['end']:
            return True
        return False
    
    def _adjust_to_business_hours(self, dt: datetime) -> datetime:
        """Adjust datetime to next business hour."""
        # If after hours, move to next day 9 AM
        if dt.hour >= self.business_hours['end']:
            dt = dt + timedelta(days=1)
            dt = dt.replace(hour=self.business_hours['start'], minute=0, second=0)
        # If before hours, move to today 9 AM
        elif dt.hour < self.business_hours['start']:
            dt = dt.replace(hour=self.business_hours['start'], minute=0, second=0)
        
        # Skip Sunday
        if dt.weekday() == 6:
            dt = dt + timedelta(days=1)
        
        return dt
    
    def run_scheduler(self, interval_seconds: int = 300):
        """
        Run the scheduler continuously.
        
        Args:
            interval_seconds: Check interval in seconds (default: 5 minutes)
        """
        logger.info(f"Starting outbound call scheduler (interval: {interval_seconds}s)")
        
        while True:
            try:
                # Check for follow-ups
                leads = self.check_for_follow_ups()
                
                # Schedule calls for each lead
                for lead in leads:
                    call_id = self.schedule_outbound_call(lead)
                    if call_id:
                        logger.info(f"Scheduled call {call_id} for lead {lead['lead_id']}")
                
                # Wait before next check
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                logger.info("Scheduler stopped by user")
                break
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(interval_seconds)


class OutboundCallScripts:
    """Call scripts for different outbound scenarios."""
    
    @staticmethod
    def get_first_followup_script(lead: Dict) -> str:
        """Get script for first follow-up call."""
        return f"""
Hello! Am I speaking with {lead['customer_name']}?

[Wait for response]

Hi {lead['customer_name']}! This is calling from TyrePlex regarding your inquiry about tyres for your {lead['vehicle_make']} {lead['vehicle_model']}.

Reference: {lead['lead_id']}

Is this a good time to talk?

[If yes, continue]

Great! Based on your {lead['vehicle_model']}, I have some excellent recommendations:

For city driving, I recommend {lead['recommended_brand']} {lead['recommended_model']} at ₹{lead['recommended_price']} per tyre.

Key features:
- Long tread life
- Fuel efficient
- Low noise

We also have budget options starting from ₹3,500 if you're looking for value.

Which would you prefer?

[Handle customer response and create booking]
"""
    
    @staticmethod
    def get_second_followup_script(lead: Dict) -> str:
        """Get script for second follow-up call."""
        return f"""
Hello! Am I speaking with {lead['customer_name']}?

Hi {lead['customer_name']}! This is calling from TyrePlex. I tried reaching you earlier regarding your tyre inquiry for your {lead['vehicle_model']}.

Reference: {lead['lead_id']}

Do you have a moment?

[If yes]

Great! I wanted to share some special offers we have today:

{lead['recommended_brand']} {lead['recommended_model']} tyres for your {lead['vehicle_model']}:
- Special price: ₹{lead['recommended_price']}
- Free home installation
- Free wheel alignment
- Free balancing

This offer is valid only for today.

Would you like to book?

[Handle response]
"""
    
    @staticmethod
    def get_reminder_script(booking: Dict) -> str:
        """Get script for booking reminder call."""
        return f"""
Hello {booking['customer_name']}! This is calling from TyrePlex.

I'm calling to confirm your tyre fitment appointment tomorrow.

Booking details:
- Booking ID: {booking['booking_id']}
- Date: Tomorrow, {booking['booking_date']}
- Time: {booking['booking_time_slot']}
- Product: {booking['tyre_brand']} {booking['tyre_model']} ({booking['quantity']} tyres)
- Address: {booking['address']}

Our technician will call you 30 minutes before arrival.

Please ensure:
- Vehicle is accessible
- Parking space available
- Someone is present

Is everything confirmed?

[If yes]

Perfect! See you tomorrow at {booking['booking_time_slot'].split('-')[0]}. Have a great day!

[If need to reschedule]

No problem! When would be better for you?
[Reschedule]
"""


# Example usage
if __name__ == "__main__":
    # Initialize database
    db = DatabaseManager()
    db.connect()
    
    # Initialize scheduler
    scheduler = OutboundCallScheduler(db)
    
    # Check business hours
    print(f"Is business hours: {scheduler.is_business_hours()}")
    print(f"Next business hour: {scheduler.get_next_business_hour()}")
    
    # Check for follow-ups
    leads = scheduler.check_for_follow_ups()
    print(f"Leads needing follow-up: {len(leads)}")
    
    # Get script for first lead
    if leads:
        script = OutboundCallScripts.get_first_followup_script(leads[0])
        print(f"\nCall script:\n{script}")
    
    db.disconnect()
