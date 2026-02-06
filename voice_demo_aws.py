"""
Professional Call Center Voice Agent - TyrePlex
Using AWS Polly for TTS and AWS Transcribe for STT
Production-ready, reliable voice interaction
"""

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
from dotenv import load_dotenv
import boto3
import pyaudio
import wave

# Load environment variables
load_dotenv()

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
    language: str = 'en'  # 'en' for English, 'hi' for Hindi, 'mix' for Hinglish
    
    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []
        if self.conversation_history is None:
            self.conversation_history = []


class AWSVoiceAgent:
    """Professional call center voice agent using AWS Polly (TTS) and Transcribe (STT)."""
    
    AGENT_NAME = "Priya"
    
    def __init__(self):
        """Initialize the AWS Polly voice agent."""
        print("\n" + "="*70)
        print("  TyrePlex Professional Call Center - AWS Polly")
        print("="*70)
        print("\n🔧 Initializing AWS Polly voice agent...")
        
        # Suppress pygame and setuptools warnings
        import warnings
        warnings.filterwarnings('ignore', category=DeprecationWarning)
        os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
        
        # AWS Configuration
        aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        
        if not aws_access_key or not aws_secret_key:
            print("❌ AWS credentials not found in .env file")
            print("\n📝 Add to .env:")
            print("   AWS_ACCESS_KEY_ID=your_key")
            print("   AWS_SECRET_ACCESS_KEY=your_secret")
            raise ValueError("AWS credentials required")
        
        try:
            # Initialize AWS Polly for TTS
            self.polly_client = boto3.client(
                service_name='polly',
                region_name=aws_region,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key
            )
            
            # Initialize AWS Transcribe for STT
            self.transcribe_client = boto3.client(
                service_name='transcribe',
                region_name=aws_region,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key
            )
            
            # Initialize S3 for Transcribe (needs audio files in S3)
            self.s3_client = boto3.client(
                service_name='s3',
                region_name=aws_region,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key
            )
            
            print(f"✅ AWS Polly initialized (Region: {aws_region})")
            print("✅ Using voice: Kajal (Indian English)")
        except Exception as e:
            print(f"❌ Failed to initialize AWS services: {e}")
            raise
        
        # Initialize PyAudio for recording
        self.audio = pyaudio.PyAudio()
        self.sample_rate = 16000
        self.chunk_size = 1024
        
        # Temporary directory
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
        
        print("✅ AWS Polly voice agent ready!")
        print("💡 Production-ready TTS with Kajal voice\n")
    
    def speak(self, text: str, show_agent: bool = True, lang: str = None):
        """Convert text to speech using AWS Polly."""
        if show_agent:
            print(f"\n🤖 {self.AGENT_NAME}: {text}")
        else:
            print(f"\n{text}")
        
        audio_file = None
        try:
            # Fix language code for AWS Polly
            # AWS Polly uses 'hi-IN' not 'hi', 'en-IN' not 'en'
            if lang == 'hi':
                lang = 'hi-IN'
            elif lang == 'en':
                lang = 'en-IN'
            elif lang is None:
                lang = 'en-IN'
            
            # Call AWS Polly for TTS
            response = self.polly_client.synthesize_speech(
                Text=text,
                OutputFormat='pcm',
                VoiceId='Kajal',  # Indian English female voice
                Engine='neural',  # Use neural engine for better quality
                LanguageCode=lang
            )
            
            # Get audio stream
            audio_stream = response['AudioStream'].read()
            
            # Save to temporary WAV file
            audio_file = os.path.join(self.temp_dir, f"tts_{int(time.time()*1000)}.wav")
            
            # Convert PCM to WAV
            with wave.open(audio_file, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(16000)  # 16kHz
                wav_file.writeframes(audio_stream)
            
            # Play audio using pygame
            import pygame
            os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
            pygame.mixer.init()
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            
            # Wait for playback to finish (with interrupt handling)
            while pygame.mixer.music.get_busy():
                try:
                    pygame.time.Clock().tick(10)
                except KeyboardInterrupt:
                    # Stop playback on interrupt
                    pygame.mixer.music.stop()
                    raise
            
            # Small pause after speaking
            time.sleep(0.1)
                
        except KeyboardInterrupt:
            # Re-raise to allow proper cleanup
            raise
        except Exception as e:
            print(f"   (Voice playback error: {e})")
        finally:
            # Always clean up audio file
            if audio_file:
                try:
                    os.remove(audio_file)
                except:
                    pass
    
    def listen(self, timeout: int = 10) -> str:
        """Listen to microphone and convert to text using Google Speech Recognition (free)."""
        import speech_recognition as sr
        
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 200
        
        try:
            with sr.Microphone() as source:
                print("\n🎤 Listening... (speak NOW - I'm listening for up to 10 seconds)")
                
                # Adjust for ambient noise
                recognizer.adjust_for_ambient_noise(source, duration=0.3)
                
                try:
                    audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                    print("   Audio captured, processing...")
                except sr.WaitTimeoutError:
                    print("⏱️  No speech detected")
                    return ""
            
            # Convert speech to text (Indian English) - FREE!
            print("🔄 Sending to Google Speech Recognition...")
            text = recognizer.recognize_google(audio, language='en-IN')
            print(f"✅ You said: {text}")
            return text
        except KeyboardInterrupt:
            print("\n⏸️  Listening interrupted")
            raise
        except sr.UnknownValueError:
            print("❓ Could not understand audio - please speak louder and clearer")
            return ""
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
            return ""
        except Exception as e:
            print(f"❌ Microphone error: {e}")
            return ""
    
    def extract_name(self, text: str) -> Optional[str]:
        """Extract customer name from text."""
        text_lower = text.lower()
        
        # Hindi/Hinglish patterns
        hindi_patterns = [
            r"mera naam\s+(\w+)",
            r"naam\s+(\w+)\s+hai",
            r"main\s+(\w+)\s+hoon",
            r"(\w+)\s+bol raha",
            r"(\w+)\s+bol rahi",
        ]
        
        # English patterns
        english_patterns = [
            r"i'?m\s+(\w+)",
            r"my name is\s+(\w+)",
            r"this is\s+(\w+)",
            r"(\w+)\s+speaking",
            r"call me\s+(\w+)",
            r"i am\s+(\w+)",
        ]
        
        # Try Hindi patterns first
        for pattern in hindi_patterns:
            match = re.search(pattern, text_lower)
            if match:
                name = match.group(1).capitalize()
                if name not in ['the', 'a', 'an', 'yes', 'no', 'hello', 'hi', 'hai', 'hoon', 'naam', 'mera']:
                    return name
        
        # Try English patterns
        for pattern in english_patterns:
            match = re.search(pattern, text_lower)
            if match:
                name = match.group(1).capitalize()
                if name not in ['the', 'a', 'an', 'yes', 'no', 'hello', 'hi']:
                    return name
        
        # If single word and reasonable length
        words = text.split()
        if len(words) == 1 and 2 < len(words[0]) < 15:
            return words[0].capitalize()
        
        # Try to find a capitalized word (likely a name)
        for word in words:
            if word[0].isupper() and len(word) > 2 and word not in ['The', 'A', 'An', 'Yes', 'No', 'Hello', 'Hi', 'I', 'Am', 'Is', 'Hai', 'Hoon']:
                return word
        
        return None
    
    def extract_vehicle_info(self, text: str) -> dict:
        """Extract vehicle information from text."""
        text_lower = text.lower()
        info = {}
        
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
                'models': ['i20', 'creta', 'venue', 'verna', 'grand i10', 'aura']
            },
            'honda': {
                'name': 'Honda',
                'models': ['city', 'civic', 'amaze', 'jazz', 'wr-v']
            },
            'bmw': {
                'name': 'BMW',
                'models': ['3 series', '5 series', 'x1', 'x3', 'x5', 'z4']
            }
        }
        
        for key, data in makes_models.items():
            if key in text_lower:
                info['make'] = data['name']
                for model in data['models']:
                    if model in text_lower:
                        info['model'] = model.capitalize()
                        break
                break
        
        if info.get('make') and not info.get('model'):
            text_without_make = text_lower
            for key in makes_models.keys():
                text_without_make = text_without_make.replace(key, '').strip()
            words = text_without_make.split()
            if words:
                info['model'] = words[0].upper()
        
        return info
    
    def detect_language(self, text: str) -> str:
        """Detect if user is speaking Hindi or English."""
        hindi_words = ['हाँ', 'नहीं', 'मुझे', 'चाहिए', 'गाड़ी', 'कार', 'टायर', 'नाम', 'मेरा']
        hinglish_words = ['haan', 'nahi', 'chahiye', 'gaadi', 'tyre', 'naam', 'mera']
        
        text_lower = text.lower()
        
        # Check for Hindi script
        if any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in text):
            return 'hi'
        
        # Check for Hinglish words
        if any(word in text_lower for word in hinglish_words):
            return 'mix'
        
        return 'en'
    
    def is_tyreplex_related(self, text: str) -> bool:
        """Check if the query is related to TyrePlex business."""
        text_lower = text.lower()
        
        # TyrePlex-related keywords
        tyreplex_keywords = [
            # Tyre related (including common mispronunciations)
            'tyre', 'tire', 'tyres', 'tires', 'tayer', 'tayre', 'tiles', 'tails',
            'wheel', 'rubber', 'puncture', 'alignment', 'balancing',
            'टायर', 'पहिया', 'व्हील',
            
            # Vehicle related
            'car', 'vehicle', 'bike', 'motorcycle', 'suv', 'truck', 'auto',
            'gaadi', 'gadi', 'gaari', 'gari',
            'गाड़ी', 'कार', 'वाहन', 'बाइक',
            
            # Brand/Model related
            'maruti', 'honda', 'hyundai', 'toyota', 'mahindra', 'tata', 'bmw', 'audi',
            'swift', 'city', 'creta', 'fortuner', 'nexon',
            'mrf', 'ceat', 'apollo', 'jk', 'bridgestone', 'michelin', 'goodyear',
            
            # Service related
            'price', 'cost', 'install', 'fitting', 'service', 'warranty', 'guarantee',
            'book', 'appointment', 'schedule', 'delivery', 'home service',
            'keemat', 'kimat', 'daam', 'dam',
            'कीमत', 'दाम', 'सर्विस', 'बुकिंग',
            
            # Size/Specification
            'size', 'specification', 'tubeless', 'radial',
            'साइज', 'स्पेसिफिकेशन',
            
            # General inquiry (including Hindi/Hinglish)
            'need', 'want', 'looking', 'buy', 'purchase', 'replace', 'change',
            'chahiye', 'chahie', 'lena', 'lene', 'leni', 'kharidna', 'badalna',
            'चाहिए', 'खरीदना', 'बदलना', 'लेना'
        ]
        
        # Check if any keyword is present
        if any(keyword in text_lower for keyword in tyreplex_keywords):
            return True
        
        # Check for common greetings and basic conversation (allowed)
        basic_conversation = [
            'hello', 'hi', 'hey', 'namaste', 'good morning', 'good evening',
            'yes', 'no', 'ok', 'okay', 'sure', 'thanks', 'thank you',
            'haan', 'han', 'nahi', 'nai', 'theek hai', 'thik hai', 'dhanyavaad',
            'my name', 'i am', 'mera naam', 'main', 'ji', 'please'
        ]
        
        if any(phrase in text_lower for phrase in basic_conversation):
            return True
        
        return False
    
    def handle_off_topic(self) -> str:
        """Politely redirect off-topic conversations."""
        if self.state.language == 'hi':
            return "Maaf kijiye, main sirf TyrePlex ke tyres aur services ke baare mein baat kar sakti hoon. Kya aapko tyres chahiye?"
        elif self.state.language == 'mix':
            return "Sorry, main sirf TyrePlex ke tyres ke baare mein help kar sakti hoon. Kya aapko tyres chahiye?"
        else:
            return "I apologize, but I can only help with TyrePlex tyre-related queries. Do you need tyres for your vehicle?"
    
    def present_services(self):
        """Present TyrePlex services to customer."""
        if self.state.language == 'hi':
            self.speak("TyrePlex mein hum yeh services provide karte hain:", lang='hi')
            self.speak("Ek, Tyres ki sale - sabhi brands available hain.", lang='hi')
            self.speak("Do, Free home installation - aapke ghar par fitting.", lang='hi')
            self.speak("Teen, Wheel alignment aur balancing.", lang='hi')
            self.speak("Chaar, Puncture repair aur tyre rotation.", lang='hi')
            self.speak("Paanch, Warranty aur guarantee on all tyres.", lang='hi')
        elif self.state.language == 'mix':
            self.speak("TyrePlex mein hum yeh services provide karte hain:")
            self.speak("1. Tyres ki sale - all brands available.")
            self.speak("2. Free home installation - aapke ghar par fitting.")
            self.speak("3. Wheel alignment aur balancing.")
            self.speak("4. Puncture repair aur tyre rotation.")
            self.speak("5. Warranty aur guarantee on all tyres.")
        else:
            self.speak("At TyrePlex, we provide these services:")
            self.speak("1. Tyre sales - All major brands available.")
            self.speak("2. Free home installation - We come to your location.")
            self.speak("3. Wheel alignment and balancing.")
            self.speak("4. Puncture repair and tyre rotation.")
            self.speak("5. Warranty and guarantee on all tyres.")
    
    def greeting(self):
        """Initial greeting with language preference."""
        # Start with brief bilingual greeting
        self.speak("Hello! Namaste! Thank you for calling TyrePlex. I am Priya.")
        
        # Ask for language preference explicitly
        self.speak("Would you prefer English or Hindi? English ya Hindi?")
        
        for attempt in range(2):
            response = self.listen(timeout=8)
            if response:
                response_lower = response.lower()
                
                # Check language preference
                if any(word in response_lower for word in ['hindi', 'हिंदी', 'हिन्दी']):
                    self.state.language = 'hi'
                    self.speak("Theek hai! Main Hindi mein baat karungi.", lang='hi')
                    break
                elif any(word in response_lower for word in ['english', 'इंग्लिश', 'angrezi']):
                    self.state.language = 'en'
                    self.speak("Perfect! I'll speak in English.")
                    break
                elif any(word in response_lower for word in ['both', 'dono', 'mix', 'hinglish']):
                    self.state.language = 'mix'
                    self.speak("Sure! Main dono languages mein baat kar sakti hoon.")
                    break
                else:
                    # Auto-detect from response
                    detected_lang = self.detect_language(response)
                    self.state.language = detected_lang
                    if detected_lang == 'hi':
                        self.speak("Theek hai! Main Hindi mein baat karungi.", lang='hi')
                    elif detected_lang == 'mix':
                        self.speak("Sure! Main Hinglish mein baat karungi.")
                    else:
                        self.speak("Perfect! I'll speak in English.")
                    break
            else:
                if attempt < 1:
                    self.speak("Sorry, I didn't hear you. English or Hindi?")
        
        # Default to English if no clear preference
        if not self.state.language or self.state.language not in ['en', 'hi', 'mix']:
            self.state.language = 'en'
            self.speak("I'll continue in English.")
        
        # Now ask for name in chosen language
        if self.state.language == 'hi':
            self.speak("Aapka naam kya hai?", lang='hi')
        elif self.state.language == 'mix':
            self.speak("Aapka naam kya hai?")
        else:
            self.speak("What's your name?")
        
        for attempt in range(2):
            response = self.listen(timeout=10)
            if response:
                name = self.extract_name(response)
                if name:
                    self.state.customer_name = name
                    
                    # Greet in chosen language
                    if self.state.language == 'hi':
                        self.speak(f"Namaste {name} ji! Aapka swagat hai TyrePlex mein.", lang='hi')
                    elif self.state.language == 'mix':
                        self.speak(f"Hello {name}! Welcome to TyrePlex.")
                    else:
                        self.speak(f"Nice to meet you {name}! Welcome to TyrePlex.")
                    return True
            else:
                if attempt < 1:
                    if self.state.language == 'hi':
                        self.speak("Sunai nahi diya. Apna naam bataiye.", lang='hi')
                    else:
                        self.speak("I didn't hear you. Please tell me your name.")
        
        # Continue without name
        if self.state.language == 'hi':
            self.speak("Koi baat nahi! Main aapki kaise madad kar sakti hoon?", lang='hi')
        elif self.state.language == 'mix':
            self.speak("No problem! Main aapki kaise help kar sakti hoon?")
        else:
            self.speak("No problem! How can I help you today?")
        return True
    
    def understand_need(self):
        """Understand what customer needs with natural conversation and validation."""
        name = self.state.customer_name or "there"
        
        if self.state.language == 'hi':
            self.speak(f"Toh {name} ji, aaj aap kya chahte hain? Kya aapko tyre chahiye?", lang='hi')
        elif self.state.language == 'mix':
            self.speak(f"So {name}, aaj aap kya chahte hain? Tyre ki zaroorat hai?")
        else:
            self.speak(f"So {name}, what can I do for you today? Looking for tyres?")
        
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
                    if self.state.language == 'hi':
                        self.speak("Maaf kijiye, main sirf tyres ke baare mein help kar sakti hoon. Aap TyrePlex ko call kar sakte hain jab aapko tyres chahiye. Dhanyavaad!", lang='hi')
                    elif self.state.language == 'mix':
                        self.speak("Sorry, main sirf tyres ke baare mein help kar sakti hoon. Jab aapko tyres chahiye tab call kariye. Thank you!")
                    else:
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
        """Get vehicle details step by step: make → model → variant."""
        name = self.state.customer_name or "there"
        
        # Step 1: Get make (brand) if not already have it
        if not self.state.vehicle_make:
            if self.state.language == 'hi':
                self.speak(f"{name} ji, aapki gaadi ka brand kya hai? Jaise Maruti, Honda, BMW?", lang='hi')
            elif self.state.language == 'mix':
                self.speak(f"{name}, aapki car ka brand kya hai? Like Maruti, Honda, BMW?")
            else:
                self.speak(f"{name}, which brand is your car? Like Maruti, Honda, BMW?")
            
            response = self.listen(timeout=10)
            if response:
                vehicle_info = self.extract_vehicle_info(response)
                if vehicle_info.get('make'):
                    self.state.vehicle_make = vehicle_info['make']
                else:
                    # Use response as make
                    self.state.vehicle_make = response.strip().title()
        
        # Step 2: Get model if not already have it
        if self.state.vehicle_make and not self.state.vehicle_model:
            if self.state.language == 'hi':
                self.speak(f"Aur {self.state.vehicle_make} ka kaun sa model hai?", lang='hi')
            elif self.state.language == 'mix':
                self.speak(f"Aur {self.state.vehicle_make} ka kaun sa model?")
            else:
                self.speak(f"And which {self.state.vehicle_make} model?")
            
            response = self.listen(timeout=10)
            if response:
                vehicle_info = self.extract_vehicle_info(response)
                if vehicle_info.get('model'):
                    self.state.vehicle_model = vehicle_info['model']
                else:
                    # Clean and use response as model
                    model = response.replace('I have', '').replace('i have', '').replace('my car is', '').strip()
                    self.state.vehicle_model = model.upper()
        
        # Step 3: Get variant if not already have it
        if self.state.vehicle_make and self.state.vehicle_model and not self.state.vehicle_variant:
            if self.state.language == 'hi':
                self.speak("Aur variant kya hai? Ya standard?", lang='hi')
            elif self.state.language == 'mix':
                self.speak("Aur variant kya hai? Or just standard?")
            else:
                self.speak("And which variant? Or just standard?")
            
            response = self.listen(timeout=8)
            if response:
                self.state.vehicle_variant = response.upper()[:15]
            else:
                self.state.vehicle_variant = "STANDARD"
        
        # Set default variant if still not set
        if not self.state.vehicle_variant:
            self.state.vehicle_variant = "STANDARD"
    
    def get_recommendations(self):
        """Get tyre recommendations with natural conversation."""
        name = self.state.customer_name or "there"
        
        if not all([self.state.vehicle_make, self.state.vehicle_model]):
            if self.state.language == 'hi':
                self.speak(f"{name} ji, mujhe aapki gaadi ki poori jaankari chahiye.", lang='hi')
            elif self.state.language == 'mix':
                self.speak(f"{name}, mujhe aapki car ki complete details chahiye.")
            else:
                self.speak(f"I need your complete vehicle details {name}.")
            return False
        
        if self.state.language == 'hi':
            self.speak("Ek minute, main check karti hoon aapki gaadi ke liye kaun se tyre sahi rahenge...", lang='hi')
        elif self.state.language == 'mix':
            self.speak("Ek minute, let me check aapki car ke liye best tyres...")
        else:
            self.speak("Give me a moment, let me find the perfect tyres for your car...")
        
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
                
                # More natural response
                if self.state.language == 'hi':
                    self.speak(f"Haan! Mil gaye! Aapki {self.state.vehicle_make} {self.state.vehicle_model} ke liye {self.state.tyre_size} size ke tyre chahiye.", lang='hi')
                elif self.state.language == 'mix':
                    self.speak(f"Perfect! Aapki {self.state.vehicle_make} {self.state.vehicle_model} ke liye {self.state.tyre_size} size ke tyres best rahenge.")
                else:
                    self.speak(f"Perfect! Your {self.state.vehicle_make} {self.state.vehicle_model} needs {self.state.tyre_size} size tyres.")
                
                top_3 = self.state.recommendations[:3]
                if top_3:
                    if self.state.language == 'hi':
                        self.speak(f"Mere paas aapke liye {len(top_3)} bahut achhe options hain.", lang='hi')
                    elif self.state.language == 'mix':
                        self.speak(f"Mere paas aapke liye {len(top_3)} great options hain.")
                    else:
                        self.speak(f"I have {len(top_3)} great options for you.")
                    
                    # Present recommendations
                    for i, rec in enumerate(top_3, 1):
                        brand = rec.get('brand', 'Unknown')
                        price = rec.get('price', 0)
                        
                        if self.state.language == 'hi':
                            if i == 1:
                                self.speak(f"Pehla option, {brand} tyres {price} rupees mein.", lang='hi')
                            elif i == 2:
                                self.speak(f"Doosra option, {brand} {price} rupees mein.", lang='hi')
                            else:
                                self.speak(f"Aur teesra option, {brand} {price} rupees mein.", lang='hi')
                        elif self.state.language == 'mix':
                            if i == 1:
                                self.speak(f"Pehla option, {brand} tyres {price} rupees mein.")
                            elif i == 2:
                                self.speak(f"Doosra option, {brand} {price} rupees mein.")
                            else:
                                self.speak(f"Aur teesra option, {brand} {price} rupees mein.")
                        else:
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
                if self.state.language == 'hi':
                    self.speak(f"Hmm, mujhe aapki {self.state.vehicle_model} ke liye exact tyre size nahi mil raha.", lang='hi')
                elif self.state.language == 'mix':
                    self.speak(f"Hmm, mujhe aapki {self.state.vehicle_model} ke liye exact size nahi mil raha.")
                else:
                    self.speak(f"I'm having trouble finding the exact tyre size for your {self.state.vehicle_model}.")
                return False
                
        except Exception as e:
            print(f"\n[DEBUG] Error: {e}")
            if self.state.language == 'hi':
                self.speak("Ek chhoti si technical problem hai. Ek baar phir try karte hain.", lang='hi')
            elif self.state.language == 'mix':
                self.speak("Ek small technical issue hai. Let me try again.")
            else:
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
            if any(word in response_lower for word in ['first', '1', 'one', 'pehla', 'pahla', 'ek']):
                selected = recommendations[0]
                self.speak(f"Great choice! {selected['brand']} at {selected['price']} rupees is an excellent option.")
                return selected
            elif any(word in response_lower for word in ['second', '2', 'two', 'doosra', 'dusra', 'do']):
                if len(recommendations) >= 2:
                    selected = recommendations[1]
                    self.speak(f"Perfect! {selected['brand']} at {selected['price']} rupees. Good value for money.")
                    return selected
            elif any(word in response_lower for word in ['third', '3', 'three', 'teesra', 'tisra', 'teen']):
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
                'source': 'voice_demo_aws',
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
    
    def closing(self):
        """Professional closing."""
        name = self.state.customer_name or "there"
        
        if self.state.language == 'hi':
            self.speak(f"TyrePlex ko call karne ke liye dhanyavaad {name} ji! Aapka din shubh ho!", lang='hi')
            self.speak("Surakshit chalayein!", lang='hi')
        elif self.state.language == 'mix':
            self.speak(f"TyrePlex ko call karne ke liye thank you {name}! Have a great day!")
            self.speak("Drive safe!")
        else:
            self.speak(f"Thank you for calling TyrePlex {name}! Have a great day!")
            self.speak("Drive safe!")
    
    def collect_contact_details(self):
        """Collect customer contact information for booking."""
        name = self.state.customer_name or "there"
        
        # Collect phone number
        if not self.state.customer_phone:
            if self.state.language == 'hi':
                self.speak(f"{name} ji, booking ke liye aapka phone number chahiye. Kripya apna 10 digit mobile number bataiye.", lang='hi')
            elif self.state.language == 'mix':
                self.speak(f"{name}, booking ke liye aapka phone number chahiye. Please apna mobile number bataiye.")
            else:
                self.speak(f"{name}, I'll need your phone number for the booking. Please share your 10-digit mobile number.")
            
            for attempt in range(2):
                response = self.listen(timeout=10)
                if response:
                    # Extract phone number (simple extraction)
                    import re
                    phone_match = re.search(r'\d{10}', response.replace(' ', ''))
                    if phone_match:
                        self.state.customer_phone = phone_match.group(0)
                        if self.state.language == 'hi':
                            self.speak(f"Dhanyavaad! Aapka number {self.state.customer_phone} save ho gaya.", lang='hi')
                        elif self.state.language == 'mix':
                            self.speak(f"Thank you! Aapka number {self.state.customer_phone} save ho gaya.")
                        else:
                            self.speak(f"Thank you! I've saved your number {self.state.customer_phone}.")
                        break
                    elif attempt < 1:
                        if self.state.language == 'hi':
                            self.speak("Maaf kijiye, number samajh nahi aaya. Ek baar phir bataiye.", lang='hi')
                        else:
                            self.speak("Sorry, I didn't catch that. Please say your number again.")
        
        # Collect address/city
        if not self.state.customer_city:
            if self.state.language == 'hi':
                self.speak("Aap kis sheher mein rehte hain? Home installation ke liye.", lang='hi')
            elif self.state.language == 'mix':
                self.speak("Aap kis city mein rehte hain? Home installation ke liye.")
            else:
                self.speak("Which city are you in? This is for home installation.")
            
            response = self.listen(timeout=10)
            if response:
                # Clean up the city name - remove common phrases
                city = response.lower()
                city = city.replace('i am in', '').replace('i\'m in', '').replace('i live in', '')
                city = city.replace('right now', '').replace('currently', '').replace('at', '')
                city = city.strip().title()
                self.state.customer_city = city
                
                if self.state.language == 'hi':
                    self.speak(f"Theek hai, {self.state.customer_city}. Samajh gaya.", lang='hi')
                elif self.state.language == 'mix':
                    self.speak(f"Okay, {self.state.customer_city}. Got it.")
                else:
                    self.speak(f"Got it, {self.state.customer_city}.")
    
    def schedule_installation(self):
        """Schedule installation appointment."""
        name = self.state.customer_name or "there"
        
        if self.state.language == 'hi':
            self.speak(f"{name} ji, installation kab karwana chahte hain?", lang='hi')
            self.speak("Aaj, kal, ya koi aur din?", lang='hi')
        elif self.state.language == 'mix':
            self.speak(f"{name}, installation kab karwana hai?")
            self.speak("Today, tomorrow, ya koi aur din?")
        else:
            self.speak(f"{name}, when would you like the installation?")
            self.speak("Today, tomorrow, or another day?")
        
        response = self.listen(timeout=10)
        if response:
            response_lower = response.lower()
            
            if 'today' in response_lower or 'aaj' in response_lower:
                self.state.booking_date = 'today'
                if self.state.language == 'hi':
                    self.speak("Bahut achha! Aaj hi installation ho jayega.", lang='hi')
                elif self.state.language == 'mix':
                    self.speak("Perfect! Aaj hi installation ho jayega.")
                else:
                    self.speak("Perfect! We'll schedule it for today.")
            elif 'tomorrow' in response_lower or 'kal' in response_lower:
                self.state.booking_date = 'tomorrow'
                if self.state.language == 'hi':
                    self.speak("Theek hai, kal installation schedule karenge.", lang='hi')
                elif self.state.language == 'mix':
                    self.speak("Okay, kal installation schedule karenge.")
                else:
                    self.speak("Okay, we'll schedule it for tomorrow.")
            else:
                self.state.booking_date = response
                if self.state.language == 'hi':
                    self.speak(f"Theek hai, {response} ko installation schedule karenge.", lang='hi')
                elif self.state.language == 'mix':
                    self.speak(f"Okay, {response} ko installation schedule karenge.")
                else:
                    self.speak(f"Okay, we'll schedule it for {response}.")
        
        # Ask for preferred time
        if self.state.language == 'hi':
            self.speak("Kaunsa time aapke liye convenient hai? Subah, dopahar, ya shaam?", lang='hi')
        elif self.state.language == 'mix':
            self.speak("Kaunsa time convenient hai? Morning, afternoon, ya evening?")
        else:
            self.speak("What time works best for you? Morning, afternoon, or evening?")
        
        response = self.listen(timeout=10)
        if response:
            # Clean up the time - extract just the time of day
            time_lower = response.lower()
            if 'morning' in time_lower or 'subah' in time_lower:
                self.state.booking_time = 'morning'
            elif 'afternoon' in time_lower or 'dopahar' in time_lower:
                self.state.booking_time = 'afternoon'
            elif 'evening' in time_lower or 'shaam' in time_lower:
                self.state.booking_time = 'evening'
            else:
                # Use the response as-is if it doesn't match common patterns
                self.state.booking_time = response.strip()
            
            if self.state.language == 'hi':
                self.speak(f"Perfect! {self.state.booking_time} mein hamari team aapke paas aayegi.", lang='hi')
            elif self.state.language == 'mix':
                self.speak(f"Perfect! {self.state.booking_time} mein hamari team aayegi.")
            else:
                self.speak(f"Perfect! Our team will reach you in the {self.state.booking_time}.")
    
    def confirm_booking(self):
        """Confirm booking details with customer."""
        name = self.state.customer_name or "there"
        
        if self.state.language == 'hi':
            self.speak(f"Chaliye {name} ji, main aapki booking confirm karti hoon.", lang='hi')
            self.speak(f"Aapka naam: {name}", lang='hi')
            self.speak(f"Phone number: {self.state.customer_phone}", lang='hi')
            self.speak(f"Gaadi: {self.state.vehicle_make} {self.state.vehicle_model}", lang='hi')
            if self.state.selected_recommendation:
                brand = self.state.selected_recommendation.get('brand')
                price = self.state.selected_recommendation.get('price')
                self.speak(f"Tyre: {brand}, Price: {price} rupees", lang='hi')
            self.speak(f"Installation: {self.state.booking_date}, {self.state.booking_time}", lang='hi')
            self.speak(f"Location: {self.state.customer_city}", lang='hi')
            self.speak("Hamari team aapse 30 minute mein call karegi aur exact time confirm karegi.", lang='hi')
            self.speak("Booking successful! Aapka booking number SMS se aayega.", lang='hi')
        elif self.state.language == 'mix':
            self.speak(f"Okay {name}, let me confirm your booking.")
            self.speak(f"Name: {name}")
            self.speak(f"Phone: {self.state.customer_phone}")
            self.speak(f"Car: {self.state.vehicle_make} {self.state.vehicle_model}")
            if self.state.selected_recommendation:
                brand = self.state.selected_recommendation.get('brand')
                price = self.state.selected_recommendation.get('price')
                self.speak(f"Tyre: {brand}, Price: {price} rupees")
            self.speak(f"Installation: {self.state.booking_date}, {self.state.booking_time}")
            self.speak(f"Location: {self.state.customer_city}")
            self.speak("Hamari team 30 minutes mein call karegi to confirm exact time.")
            self.speak("Booking successful! Aapko SMS se booking number milega.")
        else:
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
    
    def run(self):
        """Run the conversation with complete booking flow."""
        try:
            # Step 1: Greeting
            if not self.greeting():
                return
            
            # Step 2: Ask if they want to know about services
            name = self.state.customer_name or "there"
            if self.state.language == 'hi':
                self.speak(f"{name} ji, kya aap TyrePlex ki services ke baare mein jaanna chahenge?", lang='hi')
            elif self.state.language == 'mix':
                self.speak(f"{name}, kya aap TyrePlex ki services ke baare mein jaanna chahenge?")
            else:
                self.speak(f"{name}, would you like to know about TyrePlex services?")
            
            response = self.listen(timeout=8)
            if response and any(word in response.lower() for word in ['yes', 'sure', 'haan', 'han', 'okay', 'tell', 'know']):
                self.present_services()
            
            # Step 3: Understand need with validation
            if not self.understand_need():
                # Off-topic conversation, end call
                return
            
            # Step 4: Get vehicle details
            self.get_vehicle_details()
            
            # Step 5: Get recommendations (includes selection)
            if self.state.vehicle_make and self.state.vehicle_model:
                if self.get_recommendations():
                    # Step 6: Ask if they want to book
                    for booking_attempt in range(2):  # Give 2 chances
                        if self.state.language == 'hi':
                            self.speak(f"{name} ji, kya aap installation book karna chahenge?", lang='hi')
                        elif self.state.language == 'mix':
                            self.speak(f"{name}, kya aap installation book karna chahenge?")
                        else:
                            self.speak(f"{name}, would you like to book the installation?")
                        
                        response = self.listen(timeout=10)
                        if response and any(word in response.lower() for word in ['yes', 'sure', 'haan', 'han', 'okay', 'book', 'chahiye', 'jarur', 'zarur', 'bilkul']):
                            self.state.wants_booking = True
                            
                            # Step 7: Collect contact details
                            self.collect_contact_details()
                            
                            # Step 8: Schedule installation
                            self.schedule_installation()
                            
                            # Step 9: Confirm booking
                            self.confirm_booking()
                            
                            # Step 10: Save booking to database
                            self._save_booking_to_database()
                            break
                        elif response:
                            # User said no
                            if self.state.language == 'hi':
                                self.speak("Koi baat nahi! Jab aapko booking karni ho, humein call kar sakte hain.", lang='hi')
                            elif self.state.language == 'mix':
                                self.speak("No problem! Jab booking karni ho, call kar sakte hain.")
                            else:
                                self.speak("No problem! Call us when you're ready to book.")
                            break
                        elif booking_attempt < 1:
                            # Didn't hear, try again
                            self.speak("Sorry, I didn't hear you. Would you like to book?")
                        else:
                            # Still didn't hear after 2 attempts
                            self.speak("No problem! Call us when you're ready to book.")
                            break
            
            # Step 11: Closing
            self.closing()
            
        except KeyboardInterrupt:
            print("\n\n👋 Call ended by user")
            try:
                # Try to say goodbye, but don't fail if interrupted again
                if self.state.language == 'hi':
                    self.speak("TyrePlex ko call karne ke liye dhanyavaad. Namaste!", lang='hi')
                elif self.state.language == 'mix':
                    self.speak("TyrePlex ko call karne ke liye thank you. Bye!")
                else:
                    self.speak("Thank you for calling TyrePlex. Goodbye!")
            except KeyboardInterrupt:
                print("   (Goodbye interrupted)")
            except:
                pass
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    def __del__(self):
        """Cleanup."""
        try:
            self.audio.terminate()
        except:
            pass
        
        try:
            if self.db:
                self.db.close()
        except:
            pass


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  TyrePlex Professional Call Center - AWS Polly")
    print("  Production-Ready Voice Agent")
    print("="*70)
    print("\n📝 Requirements:")
    print("  - AWS credentials in .env file")
    print("  - Microphone connected")
    print("\n💡 Features:")
    print("  - AWS Polly (Neural TTS - Kajal voice)")
    print("  - Google Speech Recognition (Free STT)")
    print("  - Low latency")
    print("  - Natural voice quality")
    print("  - Bilingual support (English + Hindi)")
    print("\n" + "="*70)
    
    input("\nPress Enter to start the call...")
    
    try:
        agent = AWSVoiceAgent()
        agent.run()
    except Exception as e:
        print(f"\n❌ Failed to start voice agent: {e}")
        print("\n📝 Make sure you have:")
        print("   1. AWS credentials in .env file")
        print("   2. Microphone connected")
        print("   3. MongoDB running (optional)")

