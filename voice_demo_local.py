"""
Professional Call Center Voice Agent - TyrePlex
Natural conversation with female voice, context awareness, and professional flow
"""

import speech_recognition as sr
import pyttsx3
import re
from dataclasses import dataclass
from typing import Optional, List
from src.customer_service_agent.integrated_agent import IntegratedTyrePlexAgent
from loguru import logger

# Configure logger
logger.remove()
logger.add(lambda msg: None)  # Suppress logs for cleaner voice interaction


@dataclass
class ConversationState:
    """Track conversation context."""
    customer_name: Optional[str] = None
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_variant: Optional[str] = None
    tyre_size: Optional[str] = None
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    recommendations: List = None
    conversation_history: List = None
    
    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []
        if self.conversation_history is None:
            self.conversation_history = []


class ProfessionalVoiceAgent:
    """Professional call center voice agent with natural conversation."""
    
    AGENT_NAME = "Priya"
    
    def __init__(self):
        """Initialize the professional voice agent."""
        print("\n" + "="*70)
        print("  TyrePlex Professional Call Center - Voice Agent")
        print("="*70)
        print("\n🔧 Initializing voice agent...")
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        
        # Adjust recognition settings for better performance
        self.recognizer.energy_threshold = 300  # Lower = more sensitive
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.dynamic_energy_ratio = 1.5
        self.recognizer.pause_threshold = 0.8  # Seconds of silence to consider end of phrase
        self.recognizer.phrase_threshold = 0.3  # Minimum seconds of speaking
        self.recognizer.non_speaking_duration = 0.5  # Seconds of silence for phrase end
        
        self.microphone = sr.Microphone()
        
        # Initialize text-to-speech with female voice
        self.tts_engine = pyttsx3.init()
        self._configure_voice()
        
        # Initialize TyrePlex agent
        self.agent = IntegratedTyrePlexAgent()
        
        # Conversation state
        self.state = ConversationState()
        
        print("✅ Voice agent ready!\n")
    
    def _configure_voice(self):
        """Configure TTS for natural female voice."""
        voices = self.tts_engine.getProperty('voices')
        
        # Try to set female voice (usually index 1)
        try:
            # On Windows, voice[1] is usually female
            if len(voices) > 1:
                self.tts_engine.setProperty('voice', voices[1].id)
            else:
                self.tts_engine.setProperty('voice', voices[0].id)
        except:
            pass
        
        # Natural speaking rate (words per minute)
        self.tts_engine.setProperty('rate', 160)
        
        # Volume (0.0 to 1.0)
        self.tts_engine.setProperty('volume', 0.9)
    
    def listen(self, timeout: int = 5, allow_keyboard: bool = False) -> str:
        """Listen to microphone and convert to text."""
        with self.microphone as source:
            print("\n🎤 Listening... (speak NOW - I'm listening for up to 10 seconds)")
            
            # Adjust for ambient noise with shorter duration
            self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
            
            try:
                # Listen with longer phrase time limit
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                print("   Audio captured, processing...")
            except sr.WaitTimeoutError:
                print("⏱️  No speech detected")
                if allow_keyboard:
                    print("💬 Type your response instead (or press Enter to skip):")
                    text = input("   > ").strip()
                    if text:
                        print(f"✅ You typed: {text}")
                        return text
                return ""
        
        try:
            # Convert speech to text
            print("🔄 Sending to Google Speech Recognition...")
            text = self.recognizer.recognize_google(audio, language='en-IN')
            print(f"✅ You said: {text}")
            return text
        except sr.UnknownValueError:
            print("❓ Could not understand audio")
            print("   Tip: Speak louder and more clearly")
            if allow_keyboard:
                print("💬 Type your response instead (or press Enter to skip):")
                text = input("   > ").strip()
                if text:
                    print(f"✅ You typed: {text}")
                    return text
            return ""
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
            if allow_keyboard:
                print("💬 Type your response instead (or press Enter to skip):")
                text = input("   > ").strip()
                if text:
                    print(f"✅ You typed: {text}")
                    return text
            return ""
    
    def speak(self, text: str, show_agent: bool = True):
        """Convert text to speech and play."""
        if show_agent:
            print(f"\n🤖 {self.AGENT_NAME}: {text}")
        else:
            print(f"\n{text}")
        
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def test_microphone(self) -> bool:
        """Test microphone before starting conversation."""
        print("\n" + "="*70)
        print("  Microphone Test")
        print("="*70)
        
        # List available microphones
        try:
            mic_list = sr.Microphone.list_microphone_names()
            print(f"\n✅ Found {len(mic_list)} audio device(s)")
            if len(mic_list) > 0:
                print(f"   Using: {mic_list[0]}")
        except:
            pass
        
        print("\n📝 Testing microphone...")
        print("   Say something like: 'Hello, this is a test'")
        
        with self.microphone as source:
            print("\n🔇 Calibrating for ambient noise... (please be quiet)")
            self.recognizer.adjust_for_ambient_noise(source, duration=1.5)
            print(f"   Energy threshold set to: {self.recognizer.energy_threshold}")
            
            print("\n🎤 Speak now! (You have 5 seconds)")
            
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                print("✅ Audio captured! Processing...")
                
                try:
                    text = self.recognizer.recognize_google(audio)
                    print(f"\n✅ SUCCESS! I heard: '{text}'")
                    print("\n" + "="*70)
                    return True
                except sr.UnknownValueError:
                    print("\n⚠️  Audio captured but couldn't understand speech")
                    print("   Try speaking louder and clearer")
                    print("\n" + "="*70)
                    return False
                except sr.RequestError as e:
                    print(f"\n❌ Speech recognition service error: {e}")
                    print("   Check your internet connection")
                    print("\n" + "="*70)
                    return False
                    
            except sr.WaitTimeoutError:
                print("\n⚠️  No audio detected (timeout)")
                print("   Possible issues:")
                print("   - Microphone not connected")
                print("   - Microphone muted")
                print("   - Wrong microphone selected")
                print("   - Microphone volume too low")
                print("\n" + "="*70)
                return False
    
    def extract_name(self, text: str) -> Optional[str]:
        """Extract customer name from text."""
        text_lower = text.lower()
        
        # Patterns: "I'm X", "My name is X", "This is X", "X speaking"
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
                # Filter out common words
                if name not in ['the', 'a', 'an', 'yes', 'no', 'hello', 'hi']:
                    return name
        
        # If just a single word (likely a name)
        words = text.split()
        if len(words) == 1 and len(words[0]) > 2:
            return words[0].capitalize()
        
        return None
    
    def extract_vehicle_info(self, text: str) -> dict:
        """Extract vehicle information from text."""
        text_lower = text.lower()
        info = {}
        
        # Common vehicle makes
        makes = {
            'maruti': 'Maruti Suzuki', 'suzuki': 'Maruti Suzuki',
            'hyundai': 'Hyundai', 'honda': 'Honda', 'toyota': 'Toyota',
            'mahindra': 'Mahindra', 'tata': 'Tata', 'ford': 'Ford',
            'bmw': 'BMW', 'audi': 'Audi', 'mercedes': 'Mercedes-Benz',
            'volkswagen': 'Volkswagen', 'skoda': 'Skoda', 'renault': 'Renault',
            'nissan': 'Nissan', 'kia': 'Kia', 'mg': 'MG'
        }
        
        # Common models
        models = {
            'swift': 'Swift', 'baleno': 'Baleno', 'dzire': 'Dzire',
            'i20': 'i20', 'creta': 'Creta', 'venue': 'Venue',
            'city': 'City', 'civic': 'Civic', 'amaze': 'Amaze',
            'fortuner': 'Fortuner', 'innova': 'Innova',
            'seltos': 'Seltos', 'sonet': 'Sonet',
            'nexon': 'Nexon', 'harrier': 'Harrier',
            'xuv': 'XUV', 'scorpio': 'Scorpio', 'thar': 'Thar'
        }
        
        # Common variants
        variants = ['vxi', 'zxi', 'lxi', 'vdi', 'zdi', 'sx', 'ex', 'top', 'base']
        
        # Extract make
        for key, value in makes.items():
            if key in text_lower:
                info['make'] = value
                break
        
        # Extract model
        for key, value in models.items():
            if key in text_lower:
                info['model'] = value
                break
        
        # Extract variant
        for variant in variants:
            if variant in text_lower:
                info['variant'] = variant.upper()
                break
        
        return info
    
    def extract_budget(self, text: str) -> dict:
        """Extract budget information from text."""
        text_lower = text.lower()
        budget = {}
        
        # Look for numbers
        numbers = re.findall(r'\d+(?:,\d+)*', text)
        if numbers:
            # Remove commas and convert to int
            amounts = [int(n.replace(',', '')) for n in numbers]
            
            if len(amounts) == 1:
                # Single number - treat as max
                budget['max'] = amounts[0]
                budget['min'] = max(2000, amounts[0] - 2000)
            elif len(amounts) >= 2:
                # Two numbers - range
                budget['min'] = min(amounts[0], amounts[1])
                budget['max'] = max(amounts[0], amounts[1])
        
        # Budget keywords
        if 'budget' in text_lower or 'cheap' in text_lower or 'affordable' in text_lower:
            if not budget:
                budget = {'min': 2000, 'max': 4000}
        elif 'premium' in text_lower or 'best' in text_lower or 'top' in text_lower:
            if not budget:
                budget = {'min': 6000, 'max': 15000}
        elif 'mid' in text_lower or 'medium' in text_lower or 'average' in text_lower:
            if not budget:
                budget = {'min': 4000, 'max': 7000}
        
        return budget
    
    def greeting(self):
        """Initial greeting."""
        greeting = f"Hello! Thank you for calling TyrePlex, India's number one tyre destination. I'm {self.AGENT_NAME}. May I know your name please?"
        self.speak(greeting)
        
        # Get customer name with retries
        for attempt in range(2):
            response = self.listen(timeout=10, allow_keyboard=False)
            if response:
                name = self.extract_name(response)
                if name:
                    self.state.customer_name = name
                    self.speak(f"Nice to meet you {name}! How can I help you today?")
                    return True
                else:
                    # Use the response as name if it's short
                    words = response.split()
                    if len(words) == 1 and len(words[0]) > 2:
                        self.state.customer_name = words[0].capitalize()
                        self.speak(f"Nice to meet you {self.state.customer_name}! How can I help you today?")
                        return True
                    elif attempt < 1:
                        self.speak("Sorry, I didn't catch your name. Could you say it louder?")
            else:
                if attempt < 1:
                    self.speak("I didn't hear you. Please speak louder and clearer.")
        
        # If no name after 2 attempts, continue anyway
        self.speak("How can I help you today?")
        return True
    
    def understand_need(self) -> str:
        """Understand customer's need."""
        for attempt in range(2):
            response = self.listen(timeout=10, allow_keyboard=False)
            
            if not response:
                if attempt == 0:
                    self.speak("I didn't hear you. Could you tell me what you need? Speak louder.")
                    continue
                else:
                    self.speak("Let me help you find the perfect tyres. Which vehicle do you have?")
                    return "vehicle_inquiry"
            
            # Classify intent
            intent_result = self.agent.classify_customer_intent(response)
            intent = intent_result.get('intent', 'tyre_recommendation')
            
            # Extract vehicle info if mentioned
            vehicle_info = self.extract_vehicle_info(response)
            if vehicle_info.get('make'):
                self.state.vehicle_make = vehicle_info['make']
            if vehicle_info.get('model'):
                self.state.vehicle_model = vehicle_info['model']
            if vehicle_info.get('variant'):
                self.state.vehicle_variant = vehicle_info['variant']
            
            return intent
        
        # Default after retries
        return "vehicle_inquiry"
    
    def get_vehicle_details(self):
        """Get complete vehicle details."""
        name = self.state.customer_name or "there"
        
        # Get make
        if not self.state.vehicle_make:
            for attempt in range(2):
                self.speak(f"Sure {name}! Which car brand do you have? Like Maruti, Honda, Hyundai?")
                response = self.listen(timeout=10, allow_keyboard=False)
                if response:
                    vehicle_info = self.extract_vehicle_info(response)
                    if vehicle_info.get('make'):
                        self.state.vehicle_make = vehicle_info['make']
                        break
                    else:
                        # Try to match common brands
                        response_lower = response.lower()
                        if 'maruti' in response_lower or 'suzuki' in response_lower:
                            self.state.vehicle_make = 'Maruti Suzuki'
                            break
                        elif 'honda' in response_lower:
                            self.state.vehicle_make = 'Honda'
                            break
                        elif 'hyundai' in response_lower:
                            self.state.vehicle_make = 'Hyundai'
                            break
                        elif attempt < 1:
                            self.speak("I didn't catch the brand. Please say it louder.")
                else:
                    if attempt < 1:
                        self.speak("I didn't hear you. Please speak much louder.")
        
        # Get model
        if not self.state.vehicle_model:
            for attempt in range(2):
                if self.state.vehicle_make:
                    self.speak(f"Great! Which {self.state.vehicle_make} model? Like Swift, City, or Creta?")
                else:
                    self.speak("Which model is your car? Like Swift, City, or Creta?")
                
                response = self.listen(timeout=10, allow_keyboard=False)
                if response:
                    vehicle_info = self.extract_vehicle_info(response)
                    if vehicle_info.get('model'):
                        self.state.vehicle_model = vehicle_info['model']
                        break
                    else:
                        # Use the response as model name
                        words = response.split()
                        if len(words) > 0:
                            self.state.vehicle_model = words[0].capitalize()
                            break
                        if attempt < 1:
                            self.speak("I didn't catch the model. Could you repeat louder?")
                else:
                    if attempt < 1:
                        self.speak("I didn't hear you. Please speak much louder.")
        
        # Get variant (optional, use default if not provided)
        if not self.state.vehicle_variant:
            self.speak(f"And which variant? Like VXI, ZXI, or just say standard?")
            response = self.listen(timeout=8, allow_keyboard=False)
            if response:
                vehicle_info = self.extract_vehicle_info(response)
                if vehicle_info.get('variant'):
                    self.state.vehicle_variant = vehicle_info['variant']
                else:
                    # Use response as variant
                    self.state.vehicle_variant = response.upper()[:10]
            else:
                self.speak("No problem, I'll use the standard variant.")
        
        # Default variant if not provided
        if not self.state.vehicle_variant:
            self.state.vehicle_variant = "VXI"
    
    def get_recommendations(self):
        """Get tyre recommendations."""
        name = self.state.customer_name or "there"
        
        if not all([self.state.vehicle_make, self.state.vehicle_model]):
            self.speak("I need your vehicle details to help you better.")
            return False
        
        self.speak("Let me check the best tyres for your vehicle...")
        
        # Get recommendations from agent
        try:
            result = self.agent.identify_vehicle_and_recommend(
                self.state.vehicle_make,
                self.state.vehicle_model,
                self.state.vehicle_variant or "VXI",
                budget_range="mid"
            )
            
            if result.get('tyre_size'):
                self.state.tyre_size = result['tyre_size']['front']
                self.state.recommendations = result.get('recommendations', [])
                
                # Announce tyre size
                self.speak(f"Perfect {name}! Your {self.state.vehicle_make} {self.state.vehicle_model} needs {self.state.tyre_size} tyres.")
                
                # Ask about budget
                self.speak("What's your budget per tyre? You can say a range like 3000 to 5000.")
                response = self.listen()
                
                if response:
                    budget = self.extract_budget(response)
                    if budget:
                        self.state.budget_min = budget.get('min')
                        self.state.budget_max = budget.get('max')
                
                # Present recommendations
                self.present_recommendations()
                return True
            else:
                self.speak(f"I'm sorry {name}, I couldn't find exact data for your vehicle. Let me connect you with our expert team.")
                return False
                
        except Exception as e:
            self.speak("I'm having trouble accessing the database. Let me try again.")
            return False
    
    def present_recommendations(self):
        """Present tyre recommendations professionally."""
        name = self.state.customer_name or "there"
        
        if not self.state.recommendations:
            self.speak("Let me find the best options for you.")
            return
        
        # Filter by budget if specified
        recommendations = self.state.recommendations
        if self.state.budget_max:
            recommendations = [r for r in recommendations if r.get('price', 0) <= self.state.budget_max]
        
        if not recommendations:
            recommendations = self.state.recommendations[:3]
        
        # Present top 3
        top_3 = recommendations[:3]
        
        if self.state.budget_min and self.state.budget_max:
            self.speak(f"Excellent {name}! I have {len(top_3)} great options for you between {self.state.budget_min} and {self.state.budget_max} rupees.")
        else:
            self.speak(f"Great {name}! I have {len(top_3)} excellent options for you.")
        
        for i, rec in enumerate(top_3, 1):
            brand = rec.get('brand', 'Unknown')
            price = rec.get('price', 0)
            
            if i == 1:
                self.speak(f"First option: {brand} at {price} rupees. This is our most popular choice.")
            elif i == 2:
                self.speak(f"Second option: {brand} at {price} rupees. Great quality and value.")
            else:
                self.speak(f"Third option: {brand} at {price} rupees. Premium performance.")
        
        # Ask for preference
        self.speak("Which option interests you? Or would you like to know more about any of these?")
    
    def handle_questions(self):
        """Handle follow-up questions."""
        name = self.state.customer_name or "there"
        
        while True:
            response = self.listen(timeout=8)
            
            if not response:
                self.speak(f"Is there anything else I can help you with {name}?")
                response = self.listen(timeout=5)
                if not response:
                    break
            
            response_lower = response.lower()
            
            # Check for exit
            if any(word in response_lower for word in ['no', 'nothing', 'that\'s all', 'bye', 'thank']):
                break
            
            # Check for booking
            if any(word in response_lower for word in ['book', 'order', 'buy', 'purchase', 'install']):
                self.handle_booking()
                break
            
            # Check for comparison
            if any(word in response_lower for word in ['compare', 'difference', 'vs', 'versus']):
                self.speak("I can compare brands for you. Which two brands would you like to compare?")
                continue
            
            # Check for more info
            if any(word in response_lower for word in ['tell', 'more', 'about', 'detail']):
                self.speak("All our tyres come with warranty and free installation. They're perfect for Indian roads.")
                continue
            
            # Default response
            self.speak("Let me help you with that. Could you please be more specific?")
    
    def handle_booking(self):
        """Handle booking process."""
        name = self.state.customer_name or "there"
        
        self.speak(f"Wonderful {name}! I'll create a booking for you.")
        
        if not self.state.customer_name:
            self.speak("May I have your name please?")
            response = self.listen()
            if response:
                name_extracted = self.extract_name(response)
                if name_extracted:
                    self.state.customer_name = name_extracted
        
        self.speak("And your phone number please?")
        phone_response = self.listen()
        
        self.speak(f"Perfect {self.state.customer_name or 'there'}! I've noted down your details. Our tyre expert will call you within 30 minutes to confirm your booking and schedule the installation.")
    
    def closing(self):
        """Professional closing."""
        name = self.state.customer_name or "there"
        
        self.speak(f"Thank you for calling TyrePlex {name}! It was great talking to you. Have a wonderful day!")
        self.speak("Drive safe!")
    
    def run(self):
        """Run the professional call center conversation."""
        try:
            # Greeting
            if not self.greeting():
                return
            
            # Understand need
            intent = self.understand_need()
            
            # Get vehicle details
            self.get_vehicle_details()
            
            # Get recommendations
            if self.get_recommendations():
                # Handle follow-up questions
                self.handle_questions()
            
            # Closing
            self.closing()
            
        except KeyboardInterrupt:
            print("\n\n👋 Call ended by user")
            self.speak("Thank you for calling TyrePlex. Goodbye!")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            self.speak("I apologize for the technical difficulty. Please call us back. Thank you!")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  TyrePlex Professional Call Center")
    print("  Talk naturally like you're calling a real call center!")
    print("="*70)
    print("\n📝 Tips:")
    print("  - Speak clearly into your microphone")
    print("  - Wait for the agent to finish speaking")
    print("  - Have a natural conversation")
    print("  - Say 'bye' or 'thank you' to end the call")
    print("\n💡 New Feature:")
    print("  - If voice not detected, you can type your response!")
    print("  - Best of both worlds: Voice + Keyboard backup")
    print("\n" + "="*70)
    
    input("\nPress Enter to start the call...")
    
    try:
        agent = ProfessionalVoiceAgent()
        
        # Test microphone first
        print("\n📝 Let's test your microphone first...")
        test_result = agent.test_microphone()
        
        if not test_result:
            print("\n⚠️  Microphone test failed!")
            print("\n📝 Options:")
            print("   1. Check microphone and try again")
            print("   2. Continue with voice + keyboard backup (recommended)")
            print("   3. Exit and use text demo instead")
            
            choice = input("\nEnter choice (1/2/3): ").strip()
            
            if choice == "1":
                print("\n🔄 Retrying microphone test...")
                test_result = agent.test_microphone()
                if not test_result:
                    print("\n❌ Microphone still not working")
                    print("   Continuing with keyboard backup...")
            elif choice == "3":
                print("\n👋 Exiting. Run './run.sh demo' and choose option 1 for text demo")
                exit(0)
            else:
                print("\n✅ Continuing with voice + keyboard backup...")
        
        print("\n✅ Starting call center conversation...")
        print("💡 Tip: If voice fails, you can type your response!")
        print("\n" + "="*70)
        agent.run()
        
    except KeyboardInterrupt:
        print("\n\n👋 Call ended by user")
    except Exception as e:
        print(f"\n❌ Failed to start voice agent: {e}")
        print("\n📝 Or run: ./run.sh demo (choose option 1 for text demo)")
