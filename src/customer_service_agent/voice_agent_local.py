"""
In-House Voice Agent - No External APIs
Uses local speech recognition and TTS
"""

import speech_recognition as sr
import pyttsx3
from typing import Dict, Optional
from loguru import logger
from src.customer_service_agent.integrated_agent import IntegratedTyrePlexAgent


class LocalVoiceAgent:
    """
    Local voice agent using:
    - SpeechRecognition for speech-to-text (offline)
    - pyttsx3 for text-to-speech (offline)
    - In-house ML models for understanding
    """
    
    def __init__(self):
        """Initialize local voice agent."""
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        
        # Initialize text-to-speech
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)  # Speed
        self.tts_engine.setProperty('volume', 0.9)  # Volume
        
        # Initialize integrated agent (ML + CSV)
        self.agent = IntegratedTyrePlexAgent()
        
        # Conversation state
        self.conversation_state = {
            'stage': 'greeting',
            'vehicle_make': None,
            'vehicle_model': None,
            'vehicle_variant': None,
            'customer_name': None,
            'customer_phone': None,
            'selected_tyre': None
        }
        
        logger.success("✅ Local voice agent initialized")
    
    def speak(self, text: str):
        """Convert text to speech (offline)."""
        logger.info(f"🤖 Agent: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def listen(self) -> Optional[str]:
        """Listen to microphone and convert to text (offline)."""
        with sr.Microphone() as source:
            logger.info("🎤 Listening...")
            
            # Adjust for ambient noise
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            try:
                # Listen for audio
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
                # Convert to text (offline using Sphinx)
                text = self.recognizer.recognize_sphinx(audio)
                logger.info(f"👤 Customer: {text}")
                return text.lower()
                
            except sr.WaitTimeoutError:
                logger.warning("⚠️  No speech detected")
                return None
            except sr.UnknownValueError:
                logger.warning("⚠️  Could not understand audio")
                return None
            except Exception as e:
                logger.error(f"❌ Error: {e}")
                return None
    
    def process_input(self, text: str) -> str:
        """Process customer input and generate response."""
        if not text:
            return "I didn't catch that. Could you please repeat?"
        
        # Classify intent using in-house ML
        intent_result = self.agent.classify_customer_intent(text)
        intent = intent_result.get('intent', 'unknown')
        
        logger.info(f"🧠 Intent: {intent}")
        
        # Handle based on conversation stage and intent
        if self.conversation_state['stage'] == 'greeting':
            return self.handle_greeting(text, intent)
        
        elif self.conversation_state['stage'] == 'vehicle_make':
            return self.handle_vehicle_make(text)
        
        elif self.conversation_state['stage'] == 'vehicle_model':
            return self.handle_vehicle_model(text)
        
        elif self.conversation_state['stage'] == 'vehicle_variant':
            return self.handle_vehicle_variant(text)
        
        elif self.conversation_state['stage'] == 'recommendation':
            return self.handle_recommendation(text)
        
        elif self.conversation_state['stage'] == 'booking':
            return self.handle_booking(text)
        
        else:
            return "How can I help you today?"
    
    def handle_greeting(self, text: str, intent: str) -> str:
        """Handle initial greeting."""
        if intent == 'vehicle_inquiry':
            # Extract vehicle info from text
            brands = self.agent.get_all_brands()
            
            # Simple keyword matching for vehicle make
            for brand in ['maruti', 'suzuki', 'hyundai', 'honda', 'toyota', 'bmw']:
                if brand in text:
                    self.conversation_state['vehicle_make'] = brand.title()
                    self.conversation_state['stage'] = 'vehicle_model'
                    return f"Great! Which {brand.title()} model do you have?"
            
            self.conversation_state['stage'] = 'vehicle_make'
            return "Which vehicle brand do you have? For example, Maruti, Hyundai, or Honda?"
        
        else:
            return "Hello! Welcome to TyrePlex. I can help you find the right tyres for your vehicle. Which vehicle do you have?"
    
    def handle_vehicle_make(self, text: str) -> str:
        """Handle vehicle make input."""
        # Search for vehicle make
        vehicles = self.agent.search_vehicles(text)
        
        if vehicles:
            self.conversation_state['vehicle_make'] = vehicles[0]['make']
            self.conversation_state['stage'] = 'vehicle_model'
            return f"Got it, {vehicles[0]['make']}. Which model?"
        else:
            return "I couldn't find that brand. Could you spell it for me?"
    
    def handle_vehicle_model(self, text: str) -> str:
        """Handle vehicle model input."""
        make = self.conversation_state['vehicle_make']
        vehicles = self.agent.search_vehicles(f"{make} {text}")
        
        if vehicles:
            self.conversation_state['vehicle_model'] = vehicles[0]['model']
            self.conversation_state['stage'] = 'vehicle_variant'
            return f"Which variant of {vehicles[0]['model']}?"
        else:
            return "I couldn't find that model. Could you repeat?"
    
    def handle_vehicle_variant(self, text: str) -> str:
        """Handle vehicle variant and provide recommendations."""
        make = self.conversation_state['vehicle_make']
        model = self.conversation_state['vehicle_model']
        
        # Get recommendations
        result = self.agent.identify_vehicle_and_recommend(
            make, model, text, budget_range='mid'
        )
        
        if result.get('tyre_size'):
            self.conversation_state['vehicle_variant'] = text
            self.conversation_state['stage'] = 'recommendation'
            
            response = f"Perfect! Your {make} {model} uses {result['tyre_size']['front']} tyres. "
            
            if result.get('recommendations'):
                response += f"I have {len(result['recommendations'])} options. "
                response += f"Top recommendation is {result['recommendations'][0]['brand']} "
                response += f"at {result['recommendations'][0]['price']} rupees. "
                response += "Would you like to book this?"
            
            return response
        else:
            return "I couldn't find tyre information for that variant. Could you check the variant name?"
    
    def handle_recommendation(self, text: str) -> str:
        """Handle recommendation response."""
        if any(word in text for word in ['yes', 'sure', 'ok', 'book']):
            self.conversation_state['stage'] = 'booking'
            return "Great! Can I have your name and phone number?"
        else:
            return "Would you like to hear other options or compare brands?"
    
    def handle_booking(self, text: str) -> str:
        """Handle booking information."""
        # Extract name and phone (simple pattern matching)
        words = text.split()
        
        # Look for phone number (10 digits)
        phone = None
        for word in words:
            if word.isdigit() and len(word) == 10:
                phone = word
                break
        
        if phone:
            self.conversation_state['customer_phone'] = phone
            return f"Perfect! I've created your booking. You'll receive a confirmation SMS shortly. Is there anything else I can help you with?"
        else:
            return "I need your 10-digit phone number to create the booking."
    
    def run_conversation(self):
        """Run interactive voice conversation."""
        logger.info("🎙️  Starting voice conversation...")
        
        # Initial greeting
        self.speak("Hello! Welcome to TyrePlex. I can help you find the right tyres for your vehicle. Which vehicle do you have?")
        
        # Conversation loop
        while True:
            # Listen to customer
            customer_input = self.listen()
            
            if not customer_input:
                continue
            
            # Check for exit
            if any(word in customer_input for word in ['bye', 'exit', 'quit', 'thank you']):
                self.speak("Thank you for calling TyrePlex. Have a great day!")
                break
            
            # Process input and generate response
            response = self.process_input(customer_input)
            
            # Speak response
            self.speak(response)
    
    def test_tts(self):
        """Test text-to-speech."""
        self.speak("Hello! This is TyrePlex voice agent. I am working correctly.")
    
    def test_stt(self):
        """Test speech-to-text."""
        logger.info("Testing speech recognition...")
        text = self.listen()
        if text:
            logger.success(f"✅ Recognized: {text}")
        else:
            logger.error("❌ Failed to recognize speech")


# CLI usage
if __name__ == "__main__":
    import sys
    
    logger.info("=" * 70)
    logger.info("TyrePlex Local Voice Agent")
    logger.info("=" * 70)
    
    # Initialize agent
    agent = LocalVoiceAgent()
    
    # Test mode
    if len(sys.argv) > 1:
        if sys.argv[1] == "test-tts":
            agent.test_tts()
        elif sys.argv[1] == "test-stt":
            agent.test_stt()
        else:
            logger.error("Unknown test mode")
    else:
        # Run conversation
        try:
            agent.run_conversation()
        except KeyboardInterrupt:
            logger.info("\n\nConversation ended by user")
