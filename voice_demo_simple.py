"""
Simple Voice Demo - No ML Models
Quick testing of AWS Polly voices without loading heavy ML models
Now with language preference!
"""
import os
import tempfile
import time
import wave
from dotenv import load_dotenv
import boto3

# Load environment variables
load_dotenv()

# Suppress warnings
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"

print("\n" + "="*70)
print("  TyrePlex Voice Demo - Simple (No ML)")
print("="*70)

# Get AWS credentials
aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')

if not aws_access_key or not aws_secret_key:
    print("❌ AWS credentials not found")
    exit(1)

# Initialize Polly
polly_client = boto3.client(
    service_name='polly',
    region_name=aws_region,
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key
)

print("✅ AWS Polly initialized\n")

# Voice selection
print("📋 Select voice:")
print("   1. Kajal (Neural) - Most natural, professional")
print("   2. Aditi (Standard) - Bilingual, good for Hindi")
print("   3. Raveena (Standard) - Classic Indian English")

choice = input("\nEnter choice (1/2/3) [default: 1]: ").strip() or "1"

voice_map = {
    '1': ('Kajal', 'neural'),
    '2': ('Aditi', 'standard'),
    '3': ('Raveena', 'standard')
}

voice_id, engine = voice_map.get(choice, ('Kajal', 'neural'))
print(f"\n✅ Selected: {voice_id} ({engine})\n")

def speak(text, lang='en-IN'):
    """Speak using AWS Polly."""
    print(f"🤖 Agent: {text}")
    
    try:
        response = polly_client.synthesize_speech(
            Text=text,
            OutputFormat='pcm',
            VoiceId=voice_id,
            Engine=engine,
            LanguageCode=lang
        )
        
        audio_stream = response['AudioStream'].read()
        
        temp_dir = tempfile.gettempdir()
        audio_file = os.path.join(temp_dir, f"tts_{int(time.time()*1000)}.wav")
        
        with wave.open(audio_file, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)
            wav_file.writeframes(audio_stream)
        
        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        time.sleep(0.1)
        
        try:
            os.remove(audio_file)
        except:
            pass
    
    except Exception as e:
        print(f"   (Error: {e})")

def listen():
    """Listen using Google Speech Recognition."""
    import speech_recognition as sr
    
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 200
    
    try:
        with sr.Microphone() as source:
            print("\n🎤 Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
            print("   Processing...")
        
        text = recognizer.recognize_google(audio, language='en-IN')
        print(f"✅ You: {text}")
        return text
    
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print(f"❌ {e}")
        return ""

# Simple conversation with language preference
print("="*70)
print("  Starting Conversation")
print("="*70)
print("\n💡 Press Ctrl+C to exit\n")

try:
    # Greeting with language preference
    speak("Hello! Namaste! Welcome to TyrePlex. I am Priya.")
    speak("Would you prefer English or Hindi? English ya Hindi?")
    
    response = listen()
    
    # Detect language preference
    lang_pref = 'en'  # default
    if response:
        response_lower = response.lower()
        if any(word in response_lower for word in ['hindi', 'हिंदी']):
            lang_pref = 'hi'
            speak("Theek hai! Main Hindi mein baat karungi.", lang='hi-IN')
        elif any(word in response_lower for word in ['both', 'dono', 'mix']):
            lang_pref = 'mix'
            speak("Sure! Main dono languages mein baat kar sakti hoon.")
        else:
            lang_pref = 'en'
            speak("Perfect! I'll speak in English.")
    
    # Ask for name in chosen language
    if lang_pref == 'hi':
        speak("Aapka naam kya hai?", lang='hi-IN')
    elif lang_pref == 'mix':
        speak("Aapka naam kya hai?")
    else:
        speak("What is your name?")
    
    response = listen()
    if response:
        name = response.split()[-1] if response else "there"
        
        if lang_pref == 'hi':
            speak(f"Namaste {name} ji! Aapka swagat hai.", lang='hi-IN')
        elif lang_pref == 'mix':
            speak(f"Hello {name}! Welcome to TyrePlex.")
        else:
            speak(f"Nice to meet you {name}!")
        
        # Ask about need in chosen language
        if lang_pref == 'hi':
            speak(f"Toh {name} ji, kya aapko tyres chahiye?", lang='hi-IN')
        elif lang_pref == 'mix':
            speak(f"So {name}, kya aapko tyres chahiye?")
        else:
            speak(f"So {name}, do you need tyres for your vehicle?")
        
        response = listen()
        
        if response and any(word in response.lower() for word in ['yes', 'haan', 'han', 'sure', 'chahiye']):
            if lang_pref == 'hi':
                speak("Bahut achha! Aapki gaadi kaun si hai?", lang='hi-IN')
            elif lang_pref == 'mix':
                speak("Great! Aapki car kaun si hai?")
            else:
                speak("Great! Which car do you have? Like Maruti, Honda, or BMW?")
            
            response = listen()
            
            if response:
                if lang_pref == 'hi':
                    speak(f"Perfect! {response}. Main check karti hoon best tyres.", lang='hi-IN')
                    speak("Mere paas bahut achhe options hain. MRF tyres 4500 rupees mein.", lang='hi-IN')
                    speak("Kya aap installation book karna chahenge?", lang='hi-IN')
                elif lang_pref == 'mix':
                    speak(f"Perfect! {response}. Let me check best tyres.")
                    speak("Mere paas excellent options hain. MRF tyres at 4500 rupees.")
                    speak("Kya aap installation book karna chahenge?")
                else:
                    speak(f"Perfect! {response}. Let me check the best tyres for you.")
                    speak("I found some excellent options. MRF tyres at 4500 rupees.")
                    speak("Would you like to book installation?")
                
                response = listen()
                
                if response and any(word in response.lower() for word in ['yes', 'haan', 'han', 'sure', 'chahiye']):
                    if lang_pref == 'hi':
                        speak("Bahut achha! Hamari team 30 minute mein call karegi.", lang='hi-IN')
                        speak("TyrePlex choose karne ke liye dhanyavaad!", lang='hi-IN')
                    elif lang_pref == 'mix':
                        speak("Wonderful! Hamari team 30 minutes mein call karegi.")
                        speak("Thank you for choosing TyrePlex!")
                    else:
                        speak("Wonderful! Our team will call you within 30 minutes.")
                        speak("Thank you for choosing TyrePlex!")
                else:
                    if lang_pref == 'hi':
                        speak("Koi baat nahi! Jab chahiye tab call kariye.", lang='hi-IN')
                    elif lang_pref == 'mix':
                        speak("No problem! Jab chahiye tab call kariye.")
                    else:
                        speak("No problem! Call us when you're ready.")
        else:
            if lang_pref == 'hi':
                speak("Koi baat nahi! Jab tyres chahiye tab call kariye.", lang='hi-IN')
            elif lang_pref == 'mix':
                speak("No problem! Jab tyres chahiye tab call kariye.")
            else:
                speak("No problem! Feel free to call us when you need tyres.")
    
    if lang_pref == 'hi':
        speak("TyrePlex ko call karne ke liye dhanyavaad. Achha din!", lang='hi-IN')
    elif lang_pref == 'mix':
        speak("Thank you for calling TyrePlex. Have a great day!")
    else:
        speak("Thank you for calling TyrePlex. Have a great day!")

except KeyboardInterrupt:
    print("\n\n👋 Call ended")
    try:
        speak("Thank you for calling. Goodbye!")
    except:
        pass

print("\n" + "="*70)
print("  Demo Complete")
print("="*70)
print(f"\n✅ Voice used: {voice_id} ({engine})")
print("\n💡 To test other voices, run: python test_aws_voices.py")
