"""
Bidirectional call manager for TyrePlex.
Handles both inbound and outbound calls with FreeSWITCH/Asterisk integration.
"""

from typing import Dict, Optional, Any, List
from datetime import datetime
import json
from loguru import logger

from database import DatabaseManager
from outbound_dialer import OutboundCallScheduler, OutboundCallScripts


class BidirectionalCallHandler:
    """Handles both inbound and outbound calls."""
    
    def __init__(
        self,
        db: DatabaseManager,
        voice_agent=None
    ):
        """
        Initialize call handler.
        
        Args:
            db: Database manager instance
            voice_agent: TyrePlex voice agent instance
        """
        self.db = db
        self.voice_agent = voice_agent
        self.scheduler = OutboundCallScheduler(db)
        self.active_calls = {}
    
    def handle_inbound_call(self, call_data: Dict) -> Dict[str, Any]:
        """
        Handle incoming customer call.
        
        Args:
            call_data: Call information from telephony system
            
        Returns:
            Call session information
        """
        phone_number = call_data.get('caller_id')
        call_id = call_data.get('call_id', f"IN-{datetime.now().strftime('%Y%m%d%H%M%S')}")
        
        logger.info(f"📞 Inbound call received: {call_id} from {phone_number}")
        
        # Check if existing customer
        lead = self.db.get_lead_by_phone(phone_number)
        
        if lead:
            # Existing customer
            logger.info(f"Existing customer: {lead['customer_name']}")
            greeting = f"Welcome back to TyrePlex, {lead['customer_name']}! How can I help you today?"
            context = {
                'call_type': 'inbound',
                'lead_id': lead['lead_id'],
                'customer_name': lead['customer_name'],
                'vehicle': f"{lead.get('vehicle_make', '')} {lead.get('vehicle_model', '')}".strip(),
                'previous_inquiry': True,
                'tyre_size': lead.get('tyre_size'),
                'recommended_brand': lead.get('recommended_brand')
            }
        else:
            # New customer
            logger.info("New customer")
            greeting = "Thank you for calling TyrePlex, India's number one tyre destination. I'm here to help you find the perfect tyres for your vehicle. May I know which vehicle you have?"
            context = {
                'call_type': 'inbound',
                'previous_inquiry': False
            }
        
        # Create call session
        call_session = {
            'call_id': call_id,
            'phone_number': phone_number,
            'call_type': 'inbound',
            'start_time': datetime.now(),
            'context': context,
            'greeting': greeting,
            'lead_id': lead['lead_id'] if lead else None
        }
        
        self.active_calls[call_id] = call_session
        
        logger.info(f"✅ Inbound call session created: {call_id}")
        
        return call_session
    
    def handle_outbound_call(self, lead_id: str) -> Dict[str, Any]:
        """
        Handle outbound call to customer.
        
        Args:
            lead_id: Lead ID to call
            
        Returns:
            Call session information
        """
        # Get lead data
        lead = self.db.get_lead(lead_id)
        if not lead:
            logger.error(f"Lead not found: {lead_id}")
            return {'error': 'Lead not found'}
        
        call_id = f"OUT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        logger.info(f"📞 Outbound call initiated: {call_id} to {lead['phone_number']}")
        
        # Prepare context
        context = {
            'call_type': 'outbound',
            'lead_id': lead_id,
            'customer_name': lead['customer_name'],
            'vehicle': f"{lead.get('vehicle_make', '')} {lead.get('vehicle_model', '')} {lead.get('vehicle_variant', '')}".strip(),
            'tyre_size': lead.get('tyre_size'),
            'recommended_brand': lead.get('recommended_brand'),
            'recommended_model': lead.get('recommended_model'),
            'recommended_price': lead.get('recommended_price'),
            'city': lead.get('city'),
            'urgency': lead.get('urgency')
        }
        
        # Get appropriate call script
        if lead['total_calls'] == 0:
            script = OutboundCallScripts.get_first_followup_script(lead)
        else:
            script = OutboundCallScripts.get_second_followup_script(lead)
        
        # Create call session
        call_session = {
            'call_id': call_id,
            'phone_number': lead['phone_number'],
            'call_type': 'outbound',
            'start_time': datetime.now(),
            'context': context,
            'script': script,
            'lead_id': lead_id
        }
        
        self.active_calls[call_id] = call_session
        
        # Update lead
        self.db.update_lead(lead_id, {
            'last_contacted': datetime.now(),
            'total_calls': lead['total_calls'] + 1,
            'outbound_call_id': call_id
        })
        
        logger.info(f"✅ Outbound call session created: {call_id}")
        
        return call_session
    
    def process_call_input(
        self,
        call_id: str,
        customer_speech: str
    ) -> Dict[str, Any]:
        """
        Process customer speech during call.
        
        Args:
            call_id: Active call ID
            customer_speech: Transcribed customer speech
            
        Returns:
            Agent response
        """
        if call_id not in self.active_calls:
            logger.error(f"Call not found: {call_id}")
            return {'error': 'Call not found'}
        
        call_session = self.active_calls[call_id]
        
        logger.info(f"Processing input for call {call_id}: {customer_speech[:50]}...")
        
        # Use voice agent to process
        if self.voice_agent:
            response = self.voice_agent.process_voice_input(customer_speech)
        else:
            # Fallback response
            response = {
                'response_text': "I understand. Let me help you with that.",
                'should_end_call': False
            }
        
        # Check for lead capture
        if response.get('lead_captured'):
            lead_info = response.get('lead_info')
            if lead_info:
                call_session['lead_id'] = lead_info.get('lead_id')
                
                # Schedule follow-up
                self.scheduler.schedule_follow_up(
                    lead_id=lead_info['lead_id'],
                    delay_hours=2
                )
        
        # Check for booking creation
        if response.get('booking_created'):
            booking_info = response.get('booking_info')
            if booking_info:
                # Schedule reminder
                self.scheduler.schedule_reminder(
                    booking_id=booking_info['booking_id'],
                    reminder_time='1_day_before'
                )
        
        return response
    
    def end_call(
        self,
        call_id: str,
        call_status: str = 'completed',
        customer_satisfaction: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        End call and save logs.
        
        Args:
            call_id: Call ID to end
            call_status: Call status ('completed', 'no_answer', 'busy', 'failed')
            customer_satisfaction: Rating 1-10
            
        Returns:
            Call summary
        """
        if call_id not in self.active_calls:
            logger.error(f"Call not found: {call_id}")
            return {'error': 'Call not found'}
        
        call_session = self.active_calls[call_id]
        end_time = datetime.now()
        duration = (end_time - call_session['start_time']).total_seconds()
        
        logger.info(f"Ending call {call_id}, duration: {duration}s")
        
        # Prepare call log
        call_log = {
            'call_id': call_id,
            'lead_id': call_session.get('lead_id'),
            'call_type': call_session['call_type'],
            'phone_number': call_session['phone_number'],
            'call_status': call_status,
            'start_time': call_session['start_time'],
            'end_time': end_time,
            'duration_seconds': int(duration),
            'transcript': None,  # Would be populated by voice agent
            'intent_detected': None,
            'sentiment': None,
            'tools_used': None,
            'outcome': None,
            'booking_id': None,
            'customer_satisfaction': customer_satisfaction,
            'recording_url': None
        }
        
        # Save to database
        try:
            self.db.save_call_log(call_log)
            logger.info(f"✅ Call log saved: {call_id}")
        except Exception as e:
            logger.error(f"Failed to save call log: {e}")
        
        # Remove from active calls
        del self.active_calls[call_id]
        
        # Prepare summary
        summary = {
            'call_id': call_id,
            'call_type': call_session['call_type'],
            'duration_seconds': int(duration),
            'call_status': call_status,
            'lead_id': call_session.get('lead_id'),
            'customer_satisfaction': customer_satisfaction
        }
        
        return summary
    
    def get_active_calls(self) -> List[Dict]:
        """Get list of active calls."""
        return [
            {
                'call_id': call_id,
                'call_type': session['call_type'],
                'phone_number': session['phone_number'],
                'duration': (datetime.now() - session['start_time']).total_seconds()
            }
            for call_id, session in self.active_calls.items()
        ]


class FreeSWITCHIntegration:
    """
    Integration with FreeSWITCH telephony system.
    
    Note: This is a placeholder for actual FreeSWITCH integration.
    You'll need to install and configure FreeSWITCH separately.
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8021,
        password: str = "ClueCon"
    ):
        """
        Initialize FreeSWITCH connection.
        
        Args:
            host: FreeSWITCH ESL host
            port: FreeSWITCH ESL port
            password: FreeSWITCH ESL password
        """
        self.host = host
        self.port = port
        self.password = password
        self.connected = False
    
    def connect(self):
        """Connect to FreeSWITCH."""
        logger.info(f"Connecting to FreeSWITCH at {self.host}:{self.port}")
        
        # TODO: Implement actual FreeSWITCH connection
        # from ESL import ESLconnection
        # self.conn = ESLconnection(self.host, str(self.port), self.password)
        
        self.connected = True
        logger.info("✅ Connected to FreeSWITCH")
    
    def originate_call(
        self,
        destination: str,
        context: Dict,
        callback_url: str
    ) -> str:
        """
        Originate outbound call.
        
        Args:
            destination: Phone number to call
            context: Call context data
            callback_url: Webhook URL for call events
            
        Returns:
            Call ID
        """
        call_id = f"FS-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        logger.info(f"Originating call to {destination}")
        
        # TODO: Implement actual FreeSWITCH originate
        # originate_cmd = f"originate {{origination_caller_id_number=18001234567}}sofia/gateway/provider/{destination} &park()"
        # self.conn.api(originate_cmd)
        
        logger.info(f"✅ Call originated: {call_id}")
        
        return call_id
    
    def hangup_call(self, call_id: str):
        """Hangup a call."""
        logger.info(f"Hanging up call: {call_id}")
        
        # TODO: Implement actual FreeSWITCH hangup
        # self.conn.api(f"uuid_kill {call_id}")
        
        logger.info(f"✅ Call hung up: {call_id}")
    
    def play_audio(self, call_id: str, audio_file: str):
        """Play audio file to call."""
        logger.info(f"Playing audio to call {call_id}: {audio_file}")
        
        # TODO: Implement actual FreeSWITCH playback
        # self.conn.api(f"uuid_broadcast {call_id} {audio_file}")
    
    def disconnect(self):
        """Disconnect from FreeSWITCH."""
        if self.connected:
            logger.info("Disconnecting from FreeSWITCH")
            # TODO: Implement actual disconnect
            self.connected = False


# Example usage
if __name__ == "__main__":
    # Initialize database
    db = DatabaseManager()
    db.connect()
    
    # Initialize call handler
    call_handler = BidirectionalCallHandler(db)
    
    # Simulate inbound call
    inbound_call_data = {
        'caller_id': '+91-9876543210',
        'call_id': 'TEST-IN-001'
    }
    
    session = call_handler.handle_inbound_call(inbound_call_data)
    print(f"\n📞 Inbound call session:")
    print(f"  Call ID: {session['call_id']}")
    print(f"  Greeting: {session['greeting']}")
    
    # Simulate outbound call
    # First create a test lead
    lead_data = {
        'lead_id': f"LEAD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'customer_name': 'Test Customer',
        'phone_number': '+91-9999999999',
        'email': None,
        'vehicle_make': 'Maruti Suzuki',
        'vehicle_model': 'Swift',
        'vehicle_variant': 'VXI',
        'vehicle_type': 'Hatchback',
        'tyre_size': '185/65 R15',
        'recommended_brand': 'MRF',
        'recommended_model': 'ZVTV',
        'recommended_price': 4200.00,
        'city': 'Delhi',
        'address': None,
        'pincode': None,
        'source': 'inbound',
        'status': 'new',
        'urgency': 'within_week',
        'budget_range': 'mid',
        'next_follow_up': datetime.now(),
        'notes': None,
        'total_calls': 0
    }
    
    db.create_lead(lead_data)
    
    outbound_session = call_handler.handle_outbound_call(lead_data['lead_id'])
    print(f"\n📞 Outbound call session:")
    print(f"  Call ID: {outbound_session['call_id']}")
    print(f"  Script preview: {outbound_session['script'][:200]}...")
    
    # Get active calls
    active = call_handler.get_active_calls()
    print(f"\n📊 Active calls: {len(active)}")
    
    db.disconnect()
