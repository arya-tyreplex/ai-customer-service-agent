"""
Professional Call Center Voice Agent - TyrePlex
Natural human-like voice using Google TTS
"""

import speech_recognition as sr
from gtts import gTTS
import pygame
import os
import tempfile
import time
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, List, Dict
from src.customer_service_agent.integrated_agent import IntegratedTyrePlexAgent
from src.inhouse_ml.mongodb_manager import MongoDBManager
from loguru import logger
import re

# Configure logger
logger.remove()
logger.add(lambda msg: None)  # Suppress logs for cleaner voice interaction


@dataclass
class ConversationState:
    """Track conversation context."""
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    customer_address: Optional[str] = None
    customer_city: Optional[str] = None
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_variant: Optional[str] = None
    tyre_size: Optional[str] = None
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    recommendations: List = None
    selected_recommendation: Optional[Dict] = None
    wants_booking: bool = False
    booking_date: Optional[str] = None
    booking_time: Optional[str] = None
    wants_home_service: bool = False
    conversation_history: List = None
    
    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []
        if self.conversation_history is None:
            self.conversation_history = []


class NaturalVoiceAgent:
    """Professional call center voice agent with natural human-like voice."""
    
    AGENT_NAME = "Priya"
    
    def __init__(self):
        """Initialize the natural voice agent."""
        print("\n" + "="*70)
        print("  TyrePlex Professional Call Center - Natural Voice")
        print("="*70)
        print("\n🔧 Initializing natural voice agent...")
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        
        # Optimize for better recognition
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.dynamic_energy_ratio = 1.5
        self.recognizer.pause_threshold = 0.8
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 0.5
        
        self.microphone = sr.Microphone()
        
        # Initialize pygame for audio playback
        pygame.mixer.init()
        
        # Temporary directory for audio files
        self.temp_dir = tempfile.gettempdir()
        
        # Initialize TyrePlex agent
        self.agent = IntegratedTyrePlexAgent()
        
        # Initialize MongoDB for saving conversation data
        try:
            self.db = MongoDBManager()
            print("✅ Database connected")
        except Exception as e:
            print(f"⚠️  Database connection failed: {e}")
            print("   Conversation data will not be saved")
            self.db = None
        
        # Conversation state
        self.state = ConversationState()
        
        # Call tracking
        self.call_id = f"CALL-{int(time.time()*1000)}"
        self.lead_id = None
        
        print("✅ Natural voice agent ready!")
        print("💡 Using Google TTS for natural human-like voice\n")
    
    def speak(self, text: str, show_agent: bool = True):
        """Convert text to natural speech and play."""
        if show_agent:
            print(f"\n🤖 {self.AGENT_NAME}: {text}")
        else:
            print(f"\n{text}")
        
        try:
            # Generate speech using Google TTS (Indian English, female voice)
            tts = gTTS(text=text, lang='en', tld='co.in', slow=False)
            
            # Save to temporary file
            audio_file = os.path.join(self.temp_dir, f"tts_{int(time.time()*1000)}.mp3")
            tts.save(audio_file)
            
            # Play audio
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            # Clean up
            try:
                os.remove(audio_file)
            except:
                pass
                
        except Exception as e:
            print(f"   (Voice playback error: {e})")
    
    def listen(self, timeout: int = 10) -> str:
        """Listen to microphone and convert to text."""
        with self.microphone as source:
            print("\n🎤 Listening... (speak NOW - I'm listening for up to 10 seconds)")
            
            # Adjust for ambient noise
            self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
            
            try:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                print("   Audio captured, processing...")
            except sr.WaitTimeoutError:
                print("⏱️  No speech detected")
                return ""
        
        try:
            # Convert speech to text (Indian English)
            print("🔄 Sending to Google Speech Recognition...")
            text = self.recognizer.recognize_google(audio, language='en-IN')
            print(f"✅ You said: {text}")
            return text
        except sr.UnknownValueError:
            print("❓ Could not understand audio - please speak louder and clearer")
            return ""
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
            return ""
    
    def extract_name(self, text: str) -> Optional[str]:
        """Extract customer name from text."""
        text_lower = text.lower()
        
        patterns = [
            r"i'?m\s+(\w+)",
            r"my name is\s+(\w+)",
            r"this is\s+(\w+)",
            r"(\w+)\s+speaking",
            r"call me\s+(\w+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                name = match.group(1).capitalize()
                if name not in ['the', 'a', 'an', 'yes', 'no', 'hello', 'hi']:
                    return name
        
        words = text.split()
        if len(words) == 1 and len(words[0]) > 2:
            return words[0].capitalize()
        
        return None
    
    def is_tyreplex_related(self, text: str) -> bool:
        """Check if the query is related to TyrePlex business."""
        text_lower = text.lower()
        
        # TyrePlex-related keywords
        tyreplex_keywords = [
            # Tyre related
            'tyre', 'tire', 'wheel', 'rubber', 'puncture', 'alignment', 'balancing',
            'टायर', 'पहिया', 'व्हील',
            
            # Vehicle related
            'car', 'vehicle', 'bike', 'motorcycle', 'suv', 'truck', 'auto',
            'गाड़ी', 'कार', 'वाहन', 'बाइक',
            
            # Brand/Model related
            'maruti', 'honda', 'hyundai', 'toyota', 'mahindra', 'tata', 'bmw', 'audi',
            'swift', 'city', 'creta', 'fortuner', 'nexon',
            'mrf', 'ceat', 'apollo', 'jk', 'bridgestone', 'michelin', 'goodyear',
            
            # Service related
            'price', 'cost', 'install', 'fitting', 'service', 'warranty', 'guarantee',
            'book', 'appointment', 'schedule', 'delivery', 'home service',
            'कीमत', 'दाम', 'सर्विस', 'बुकिंग',
            
            # Size/Specification
            'size', 'specification', 'tubeless', 'radial',
            'साइज', 'स्पेसिफिकेशन',
            
            # General inquiry
            'need', 'want', 'looking', 'buy', 'purchase', 'replace', 'change',
            'chahiye', 'चाहिए', 'खरीदना', 'बदलना'
        ]
        
        # Check if any keyword is present
        if any(keyword in text_lower for keyword in tyreplex_keywords):
            return True
        
        # Check for common greetings and basic conversation (allowed)
        basic_conversation = [
            'hello', 'hi', 'hey', 'namaste', 'good morning', 'good evening',
            'yes', 'no', 'ok', 'okay', 'sure', 'thanks', 'thank you',
            'haan', 'nahi', 'theek hai', 'dhanyavaad',
            'my name', 'i am', 'mera naam', 'main'
        ]
        
        if any(phrase in text_lower for phrase in basic_conversation):
            return True
        
        return False
    
    def handle_off_topic(self) -> str:
        """Politely redirect off-topic conversations."""
        return "I apologize, but I can only help with TyrePlex tyre-related queries. Do you need tyres for your vehicle?"
    
    def extract_vehicle_info(self, text: str) -> dict:
        """Extract vehicle information from text."""
        text_lower = text.lower()
        info = {}
        
        # Car makes with their models
        makes_models = {
            'maruti': {
                'name': 'Maruti Suzuki',
                'models': ['swift', 'baleno', 'dzire', 'alto', 'wagon r', 'ertiga', 'brezza', 'ciaz']
            },
            'suzuki': {
                'name': 'Maruti Suzuki',
                'models': ['swift', 'baleno', 'dzire', 'alto', 'wagon r', 'ertiga', 'brezza', 'ciaz']
            },
            'hyundai': {
                'name': 'Hyundai',
                'models': ['i20', 'creta', 'venue', 'verna', 'grand i10', 'aura', 'elantra']
            },
            'honda': {
                'name': 'Honda',
                'models': ['city', 'civic', 'amaze', 'jazz', 'wr-v', 'accord']
            },
            'toyota': {
                'name': 'Toyota',
                'models': ['fortuner', 'innova', 'glanza', 'urban cruiser', 'camry']
            },
            'mahindra': {
                'name': 'Mahindra',
                'models': ['xuv', 'scorpio', 'thar', 'bolero', 'xuv300', 'xuv700']
            },
            'tata': {
                'name': 'Tata',
                'models': ['nexon', 'harrier', 'safari', 'altroz', 'punch', 'tiago']
            },
            'bmw': {
                'name': 'BMW',
                'models': ['3 series', '5 series', '7 series', 'x1', 'x3', 'x5', 'x7', 'z4']
            },
            'audi': {
                'name': 'Audi',
                'models': ['a3', 'a4', 'a6', 'q3', 'q5', 'q7', 'q8']
            },
            'mercedes': {
                'name': 'Mercedes-Benz',
                'models': ['c class', 'e class', 's class', 'gla', 'glc', 'gle', 'gls']
            },
            'benz': {
                'name': 'Mercedes-Benz',
                'models': ['c class', 'e class', 's class', 'gla', 'glc', 'gle', 'gls']
            }
        }
        
        # Find make
        for key, data in makes_models.items():
            if key in text_lower:
                info['make'] = data['name']
                # Find model for this make
                for model in data['models']:
                    if model in text_lower:
                        info['model'] = model.capitalize()
                        break
                break
        
        # If no model found but make is found, try to extract model from text
        if info.get('make') and not info.get('model'):
            # Remove the make name and get remaining words
            text_without_make = text_lower
            for key in makes_models.keys():
                text_without_make = text_without_make.replace(key, '').strip()
            
            # The remaining text might be the model
            words = text_without_make.split()
            if words:
                info['model'] = words[0].upper()  # Use uppercase for models like Z4, X5
        
        return info
    
    def greeting(self):
        """Initial greeting."""
        greeting = f"Hello! Thank you for calling TyrePlex. I'm {self.AGENT_NAME}. What's your name?"
        self.speak(greeting)
        
        for attempt in range(2):
            response = self.listen(timeout=10)
            if response:
                name = self.extract_name(response)
                if name:
                    self.state.customer_name = name
                    self.speak(f"Nice to meet you {name}!")
                    return True
                else:
                    words = response.split()
                    if len(words) == 1 and len(words[0]) > 2:
                        self.state.customer_name = words[0].capitalize()
                        self.speak(f"Nice to meet you {self.state.customer_name}!")
                        return True
                    elif attempt < 1:
                        self.speak("Sorry, I didn't catch your name. Could you say it again?")
            else:
                if attempt < 1:
                    self.speak("I didn't hear you. Please speak louder.")
        
        self.speak("No problem! How can I help you today?")
        return True
    
    def understand_need(self):
        """Understand what customer needs with validation."""
        name = self.state.customer_name or "there"
        self.speak(f"So {name}, what brings you here today?")
        
        response = self.listen(timeout=10)
        if response:
            # Validate if query is TyrePlex-related
            if not self.is_tyreplex_related(response):
                # Off-topic query
                redirect_message = self.handle_off_topic()
                self.speak(redirect_message)
                
                # Give one more chance
                response = self.listen(timeout=10)
                if response and not self.is_tyreplex_related(response):
                    # Still off-topic, politely end
                    self.speak("I apologize, but I can only assist with tyre-related queries. Please call TyrePlex when you need tyres. Thank you!")
                    return False
            
            # Extract vehicle info if mentioned
            vehicle_info = self.extract_vehicle_info(response)
            if vehicle_info.get('make'):
                self.state.vehicle_make = vehicle_info['make']
            if vehicle_info.get('model'):
                self.state.vehicle_model = vehicle_info['model']
        
        return True
    
    def get_vehicle_details(self):
        """Get vehicle details."""
        name = self.state.customer_name or "there"
        
        # Get make and model together
        if not self.state.vehicle_make or not self.state.vehicle_model:
            for attempt in range(2):
                self.speak(f"Sure {name}! Which car do you have? Tell me the brand and model.")
                response = self.listen(timeout=10)
                if response:
                    vehicle_info = self.extract_vehicle_info(response)
                    print(f"[DEBUG] Extracted: {vehicle_info}")
                    
                    if vehicle_info.get('make'):
                        self.state.vehicle_make = vehicle_info['make']
                    if vehicle_info.get('model'):
                        self.state.vehicle_model = vehicle_info['model']
                    
                    # If we got both, break
                    if self.state.vehicle_make and self.state.vehicle_model:
                        break
                    
                    # If we only got make, ask for model
                    if self.state.vehicle_make and not self.state.vehicle_model:
                        break
                    
                    # Try to match common brands if not extracted
                    if not self.state.vehicle_make:
                        response_lower = response.lower()
                        if 'maruti' in response_lower or 'suzuki' in response_lower:
                            self.state.vehicle_make = 'Maruti Suzuki'
                        elif 'honda' in response_lower:
                            self.state.vehicle_make = 'Honda'
                        elif 'hyundai' in response_lower:
                            self.state.vehicle_make = 'Hyundai'
                        elif 'toyota' in response_lower:
                            self.state.vehicle_make = 'Toyota'
                        elif 'bmw' in response_lower:
                            self.state.vehicle_make = 'BMW'
                        elif 'audi' in response_lower:
                            self.state.vehicle_make = 'Audi'
                        elif 'mercedes' in response_lower or 'benz' in response_lower:
                            self.state.vehicle_make = 'Mercedes-Benz'
                        
                        # Extract model from response
                        if self.state.vehicle_make:
                            words = response.split()
                            if len(words) > 1:
                                self.state.vehicle_model = words[-1].upper()
                            break
                    
                    if attempt < 1:
                        self.speak("I didn't catch that. Please say your car brand and model.")
                else:
                    if attempt < 1:
                        self.speak("I didn't hear you. Please speak louder.")
        
        # Get model if still not extracted
        if self.state.vehicle_make and not self.state.vehicle_model:
            for attempt in range(2):
                # Give correct examples based on make
                if 'Maruti' in self.state.vehicle_make:
                    self.speak(f"Which Maruti model? Like Swift, Baleno, or Dzire?")
                elif 'Honda' in self.state.vehicle_make:
                    self.speak(f"Which Honda model? Like City, Amaze, or Civic?")
                elif 'Hyundai' in self.state.vehicle_make:
                    self.speak(f"Which Hyundai model? Like Creta, i20, or Venue?")
                elif 'BMW' in self.state.vehicle_make:
                    self.speak(f"Which BMW model? Like 3 Series, 5 Series, or X5?")
                else:
                    self.speak(f"Which {self.state.vehicle_make} model?")
                
                response = self.listen(timeout=10)
                if response:
                    vehicle_info = self.extract_vehicle_info(response)
                    if vehicle_info.get('model'):
                        self.state.vehicle_model = vehicle_info['model']
                        break
                    else:
                        # Use the response as model name
                        self.state.vehicle_model = response.upper()
                        break
                else:
                    if attempt < 1:
                        self.speak("I didn't hear you. Please speak louder.")
        
        # Get variant
        if not self.state.vehicle_variant:
            self.speak("And which variant? You can say the variant name or just standard.")
            response = self.listen(timeout=8)
            if response:
                self.state.vehicle_variant = response.upper()[:10]
            else:
                self.state.vehicle_variant = "VXI"
        
        if not self.state.vehicle_variant:
            self.state.vehicle_variant = "VXI"
    
    def get_recommendations(self):
        """Get tyre recommendations."""
        name = self.state.customer_name or "there"
        
        if not all([self.state.vehicle_make, self.state.vehicle_model]):
            self.speak(f"I need your complete vehicle details to help you {name}.")
            return False
        
        self.speak("Let me check what tyres will fit your car...")
        
        try:
            result = self.agent.identify_vehicle_and_recommend(
                self.state.vehicle_make,
                self.state.vehicle_model,
                self.state.vehicle_variant or "VXI",
                budget_range="mid"
            )
            
            print(f"\n[DEBUG] Result: {result}")
            
            if result.get('tyre_size'):
                self.state.tyre_size = result['tyre_size']['front']
                self.state.recommendations = result.get('recommendations', [])
                
                self.speak(f"Perfect! Your {self.state.vehicle_make} {self.state.vehicle_model} needs {self.state.tyre_size} size tyres.")
                
                # Present top 3
                top_3 = self.state.recommendations[:3]
                if top_3:
                    self.speak(f"I have {len(top_3)} great options for you.")
                    
                    # Present recommendations
                    for i, rec in enumerate(top_3, 1):
                        brand = rec.get('brand', 'Unknown')
                        price = rec.get('price', 0)
                        
                        if i == 1:
                            self.speak(f"First option, {brand} tyres at {price} rupees.")
                        elif i == 2:
                            self.speak(f"Second option, {brand} at {price} rupees.")
                        else:
                            self.speak(f"And third option, {brand} at {price} rupees.")
                    
                    # Ask user to pick an option
                    selected_recommendation = self._ask_user_preference(top_3)
                    
                    # Save lead to database with selected recommendation
                    self._save_lead_to_database(selected_recommendation)
                    
                    return True
                else:
                    self.speak(f"I found the tyre size but let me get you some brand options.")
                    return True
            else:
                self.speak(f"Hmm, I'm having trouble finding the exact tyre size for your {self.state.vehicle_model}. Let me connect you with our expert team.")
                return False
                
        except Exception as e:
            print(f"\n[DEBUG] Error: {e}")
            import traceback
            traceback.print_exc()
            self.speak("I'm having a small technical issue. Let me try again.")
            return False
    
    def _ask_user_preference(self, recommendations: List[Dict]) -> Optional[Dict]:
        """Ask user which recommendation they prefer."""
        name = self.state.customer_name or "there"
        
        # Ask which option they prefer
        for attempt in range(3):  # Allow up to 3 attempts
            if attempt == 0:
                self.speak(f"So {name}, which option would you like to go with? First, second, or third?")
            else:
                self.speak("Which one would you prefer?")
            
            response = self.listen(timeout=10)
            
            if not response:
                if attempt < 2:
                    self.speak("I didn't hear you. Please say first, second, or third.")
                continue
            
            response_lower = response.lower()
            
            # Check if user wants to repeat
            if any(word in response_lower for word in ['repeat', 'again', 'tell me again', 'say again', 'what were', 'remind']):
                self.speak("Sure! Let me repeat the options.")
                for i, rec in enumerate(recommendations, 1):
                    brand = rec.get('brand', 'Unknown')
                    price = rec.get('price', 0)
                    if i == 1:
                        self.speak(f"First option, {brand} tyres at {price} rupees.")
                    elif i == 2:
                        self.speak(f"Second option, {brand} at {price} rupees.")
                    else:
                        self.speak(f"Third option, {brand} at {price} rupees.")
                continue
            
            # Check which option they selected
            if 'first' in response_lower or '1' in response_lower or 'one' in response_lower:
                selected = recommendations[0]
                self.speak(f"Great choice! {selected['brand']} at {selected['price']} rupees is an excellent option.")
                return selected
            elif 'second' in response_lower or '2' in response_lower or 'two' in response_lower:
                if len(recommendations) >= 2:
                    selected = recommendations[1]
                    self.speak(f"Perfect! {selected['brand']} at {selected['price']} rupees. Good value for money.")
                    return selected
            elif 'third' in response_lower or '3' in response_lower or 'three' in response_lower:
                if len(recommendations) >= 3:
                    selected = recommendations[2]
                    self.speak(f"Excellent! {selected['brand']} at {selected['price']} rupees. Premium quality.")
                    return selected
            
            # Check if they want more information
            if any(word in response_lower for word in ['tell me more', 'details', 'difference', 'compare']):
                self.speak("All three are high-quality tyres. The main difference is the price and brand reputation.")
                continue
            
            # Check if they're unsure
            if any(word in response_lower for word in ['not sure', 'confused', 'help', 'suggest', 'recommend']):
                self.speak(f"I'd recommend the first option, {recommendations[0]['brand']}. It's our most popular choice and offers great performance.")
                self.speak("Would you like to go with that?")
                confirm = self.listen(timeout=8)
                if confirm and any(word in confirm.lower() for word in ['yes', 'sure', 'ok', 'yeah', 'fine']):
                    selected = recommendations[0]
                    self.speak(f"Perfect! {selected['brand']} at {selected['price']} rupees.")
                    return selected
                continue
            
            # If we couldn't understand, try again
            if attempt < 2:
                self.speak("I didn't catch that. Please say first, second, or third option.")
        
        # If no selection after 3 attempts, default to first
        self.speak(f"No problem! I'll note down the first option, {recommendations[0]['brand']}, for you.")
        return recommendations[0]
    
    def _save_lead_to_database(self, selected_recommendation: Optional[Dict] = None):
        """Save lead data to MongoDB."""
        if not self.db:
            return
        
        try:
            lead_data = {
                'call_id': self.call_id,
                'customer_name': self.state.customer_name or 'Unknown',
                'phone': self.state.customer_phone,
                'city': self.state.customer_city,
                'vehicle_make': self.state.vehicle_make,
                'vehicle_model': self.state.vehicle_model,
                'vehicle_variant': self.state.vehicle_variant,
                'tyre_size': self.state.tyre_size,
                'status': 'contacted',
                'source': 'voice_demo_natural',
                'created_at': datetime.now()
            }
            
            # Add selected recommendation
            if selected_recommendation:
                lead_data['selected_brand'] = selected_recommendation.get('brand')
                lead_data['selected_model'] = selected_recommendation.get('model')
                lead_data['selected_price'] = selected_recommendation.get('price')
                lead_data['recommended_brand'] = selected_recommendation.get('brand')
                lead_data['recommended_model'] = selected_recommendation.get('model')
                lead_data['recommended_price'] = selected_recommendation.get('price')
                # Store selected recommendation for booking
                self.state.selected_recommendation = selected_recommendation
            
            # Check if lead already exists (by name and vehicle)
            existing_lead = self.db.db.leads.find_one({
                'customer_name': lead_data['customer_name'],
                'vehicle_make': lead_data['vehicle_make'],
                'vehicle_model': lead_data['vehicle_model']
            })
            
            if existing_lead:
                # Update existing lead
                self.lead_id = str(existing_lead['_id'])
                self.db.db.leads.update_one(
                    {'_id': existing_lead['_id']},
                    {'$set': {
                        'phone': lead_data.get('phone'),
                        'city': lead_data.get('city'),
                        'tyre_size': lead_data['tyre_size'],
                        'selected_brand': lead_data.get('selected_brand'),
                        'selected_price': lead_data.get('selected_price'),
                        'recommended_brand': lead_data.get('recommended_brand'),
                        'recommended_price': lead_data.get('recommended_price'),
                        'last_contacted': datetime.now()
                    }}
                )
                print(f"\n✅ Updated existing lead: {self.lead_id}")
            else:
                # Create new lead
                self.lead_id = self.db.create_lead(lead_data)
                print(f"\n✅ Saved lead to database: {self.lead_id}")
            
            # Save call log
            self._save_call_log(selected_recommendation)
            
        except Exception as e:
            print(f"\n⚠️  Failed to save lead: {e}")
    
    def _save_call_log(self, selected_recommendation: Optional[Dict] = None):
        """Save call log to database."""
        if not self.db or not self.lead_id:
            return
        
        try:
            call_log = {
                'call_id': self.call_id,
                'lead_id': self.lead_id,
                'call_type': 'inbound',
                'duration_seconds': 0,  # Not tracked in demo
                'customer_name': self.state.customer_name,
                'vehicle_info': f"{self.state.vehicle_make} {self.state.vehicle_model} {self.state.vehicle_variant}",
                'tyre_size': self.state.tyre_size,
                'recommendations_count': len(self.state.recommendations),
                'selected_brand': selected_recommendation.get('brand') if selected_recommendation else None,
                'selected_price': selected_recommendation.get('price') if selected_recommendation else None,
                'timestamp': datetime.now()
            }
            
            self.db.create_call_log(call_log)
            print(f"✅ Saved call log: {self.call_id}")
            
        except Exception as e:
            print(f"⚠️  Failed to save call log: {e}")
    
    def closing(self):
        """Professional closing."""
        name = self.state.customer_name or "there"
        self.speak(f"Thank you for calling TyrePlex {name}! Have a great day!")
        self.speak("Drive safe!")
    
    def present_services(self):
        """Present TyrePlex services to customer."""
        self.speak("At TyrePlex, we provide these services:")
        self.speak("1. Tyre sales - All major brands available.")
        self.speak("2. Free home installation - We come to your location.")
        self.speak("3. Wheel alignment and balancing.")
        self.speak("4. Puncture repair and tyre rotation.")
        self.speak("5. Warranty and guarantee on all tyres.")
    
    def collect_contact_details(self):
        """Collect customer contact information for booking."""
        name = self.state.customer_name or "there"
        
        # Collect phone number
        if not self.state.customer_phone:
            self.speak(f"{name}, I'll need your phone number for the booking. Please share your 10-digit mobile number.")
            
            for attempt in range(2):
                response = self.listen(timeout=10)
                if response:
                    # Extract phone number (simple extraction)
                    import re
                    phone_match = re.search(r'\d{10}', response.replace(' ', ''))
                    if phone_match:
                        self.state.customer_phone = phone_match.group(0)
                        self.speak(f"Thank you! I've saved your number {self.state.customer_phone}.")
                        break
                    elif attempt < 1:
                        self.speak("Sorry, I didn't catch that. Please say your number again.")
        
        # Collect address/city
        if not self.state.customer_city:
            self.speak("Which city are you in? This is for home installation.")
            
            response = self.listen(timeout=10)
            if response:
                self.state.customer_city = response.strip()
                self.speak(f"Got it, {self.state.customer_city}.")
    
    def schedule_installation(self):
        """Schedule installation appointment."""
        name = self.state.customer_name or "there"
        
        self.speak(f"{name}, when would you like the installation?")
        self.speak("Today, tomorrow, or another day?")
        
        response = self.listen(timeout=10)
        if response:
            response_lower = response.lower()
            
            if 'today' in response_lower:
                self.state.booking_date = 'today'
                self.speak("Perfect! We'll schedule it for today.")
            elif 'tomorrow' in response_lower:
                self.state.booking_date = 'tomorrow'
                self.speak("Okay, we'll schedule it for tomorrow.")
            else:
                self.state.booking_date = response
                self.speak(f"Okay, we'll schedule it for {response}.")
        
        # Ask for preferred time
        self.speak("What time works best for you? Morning, afternoon, or evening?")
        
        response = self.listen(timeout=10)
        if response:
            self.state.booking_time = response
            self.speak(f"Perfect! Our team will reach you in the {response}.")
    
    def confirm_booking(self):
        """Confirm booking details with customer."""
        name = self.state.customer_name or "there"
        
        self.speak(f"Alright {name}, let me confirm your booking details.")
        self.speak(f"Name: {name}")
        self.speak(f"Phone: {self.state.customer_phone}")
        self.speak(f"Vehicle: {self.state.vehicle_make} {self.state.vehicle_model}")
        if self.state.selected_recommendation:
            brand = self.state.selected_recommendation.get('brand')
            price = self.state.selected_recommendation.get('price')
            self.speak(f"Tyre: {brand} at {price} rupees")
        self.speak(f"Installation: {self.state.booking_date}, {self.state.booking_time}")
        self.speak(f"Location: {self.state.customer_city}")
        self.speak("Our team will call you within 30 minutes to confirm the exact time.")
        self.speak("Booking successful! You'll receive your booking number via SMS.")
    
    def _save_booking_to_database(self):
        """Save booking to MongoDB."""
        if not self.db or not self.lead_id:
            return
        
        try:
            booking_data = {
                'lead_id': self.lead_id,
                'call_id': self.call_id,
                'customer_name': self.state.customer_name,
                'customer_phone': self.state.customer_phone,
                'customer_city': self.state.customer_city,
                'vehicle_make': self.state.vehicle_make,
                'vehicle_model': self.state.vehicle_model,
                'vehicle_variant': self.state.vehicle_variant,
                'tyre_size': self.state.tyre_size,
                'booking_date': self.state.booking_date,
                'booking_time': self.state.booking_time,
                'wants_home_service': True,  # Always true for voice bookings
                'status': 'pending',
                'created_at': datetime.now()
            }
            
            # Add selected tyre details
            if self.state.selected_recommendation:
                booking_data['tyre_brand'] = self.state.selected_recommendation.get('brand')
                booking_data['tyre_model'] = self.state.selected_recommendation.get('model')
                booking_data['tyre_price'] = self.state.selected_recommendation.get('price')
            
            booking_id = self.db.create_booking(booking_data)
            print(f"\n✅ Saved booking to database: {booking_id}")
            
            # Update lead with contact details
            if self.state.customer_phone:
                from bson.objectid import ObjectId
                self.db.db.leads.update_one(
                    {'_id': ObjectId(self.lead_id)},
                    {'$set': {
                        'phone': self.state.customer_phone,
                        'city': self.state.customer_city,
                        'status': 'qualified',
                        'booking_id': booking_id,
                        'updated_at': datetime.now()
                    }}
                )
                print(f"✅ Updated lead with booking details")
            
        except Exception as e:
            print(f"\n⚠️  Failed to save booking: {e}")
    
    def run(self):
        """Run the conversation with complete booking flow."""
        try:
            # Step 1: Greeting
            if not self.greeting():
                return
            
            # Step 2: Ask if they want to know about services
            name = self.state.customer_name or "there"
            self.speak(f"{name}, would you like to know about TyrePlex services?")
            
            response = self.listen(timeout=8)
            if response and any(word in response.lower() for word in ['yes', 'sure', 'okay', 'tell', 'know']):
                self.present_services()
            
            # Step 3: Understand need with validation
            if not self.understand_need():
                # Off-topic conversation, end call
                return
            
            # Step 4: Get vehicle details
            self.get_vehicle_details()
            
            # Debug: Show what we have
            print(f"\n[DEBUG] Make: {self.state.vehicle_make}, Model: {self.state.vehicle_model}, Variant: {self.state.vehicle_variant}")
            
            # Step 5: Get recommendations (includes selection)
            if self.state.vehicle_make and self.state.vehicle_model:
                if self.get_recommendations():
                    # Step 6: Ask if they want to book
                    self.speak(f"{name}, would you like to book the installation?")
                    
                    response = self.listen(timeout=10)
                    if response and any(word in response.lower() for word in ['yes', 'sure', 'okay', 'book']):
                        self.state.wants_booking = True
                        
                        # Step 7: Collect contact details
                        self.collect_contact_details()
                        
                        # Step 8: Schedule installation
                        self.schedule_installation()
                        
                        # Step 9: Confirm booking
                        self.confirm_booking()
                        
                        # Step 10: Save booking to database
                        self._save_booking_to_database()
                    else:
                        self.speak("No problem! Call us when you're ready to book.")
            else:
                self.speak("I need your complete vehicle details to recommend tyres.")
            
            # Step 11: Closing
            self.closing()
            
        except KeyboardInterrupt:
            print("\n\n👋 Call ended by user")
            self.speak("Thank you for calling TyrePlex. Goodbye!")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            self.speak("I apologize for the technical difficulty. Please call us back. Thank you!")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  TyrePlex Professional Call Center - Natural Voice")
    print("  Human-like voice using Google TTS!")
    print("="*70)
    print("\n📝 Features:")
    print("  - Natural human-like voice (like RJ/Anchor)")
    print("  - Indian English accent")
    print("  - Professional conversation flow")
    print("\n💡 Tips:")
    print("  - Speak clearly and loudly")
    print("  - Wait for agent to finish speaking")
    print("  - Say 'bye' to end call")
    print("\n" + "="*70)
    
    input("\nPress Enter to start the call...")
    
    try:
        agent = NaturalVoiceAgent()
        agent.run()
    except Exception as e:
        print(f"\n❌ Failed to start voice agent: {e}")
        print("\n📝 Make sure you have installed:")
        print("   pip install gTTS pygame")
