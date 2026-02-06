"""
Voice Recognition Diagnostic Tool
Find out why speech recognition is failing
"""

import speech_recognition as sr
import time

def test_audio_capture():
    """Test if microphone captures audio."""
    print("\n" + "="*70)
    print("  Test 1: Audio Capture")
    print("="*70)
    
    recognizer = sr.Recognizer()
    
    # Show current settings
    print(f"\nCurrent settings:")
    print(f"  Energy threshold: {recognizer.energy_threshold}")
    print(f"  Dynamic threshold: {recognizer.dynamic_energy_threshold}")
    print(f"  Pause threshold: {recognizer.pause_threshold}s")
    
    try:
        with sr.Microphone() as source:
            print("\n🔇 Calibrating... (be quiet for 2 seconds)")
            recognizer.adjust_for_ambient_noise(source, duration=2)
            print(f"  Adjusted energy threshold: {recognizer.energy_threshold}")
            
            print("\n🎤 Speak NOW! Say: 'Hello this is a test'")
            print("   (You have 5 seconds)")
            
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            print("\n✅ Audio captured!")
            print(f"   Audio data size: {len(audio.frame_data)} bytes")
            print(f"   Sample rate: {audio.sample_rate} Hz")
            print(f"   Sample width: {audio.sample_width} bytes")
            
            return audio, recognizer
            
    except sr.WaitTimeoutError:
        print("\n❌ No audio detected - microphone not picking up sound")
        return None, None
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None, None


def test_google_recognition(audio, recognizer):
    """Test Google Speech Recognition."""
    print("\n" + "="*70)
    print("  Test 2: Google Speech Recognition")
    print("="*70)
    
    if not audio:
        print("\n❌ No audio to test")
        return False
    
    print("\n🔄 Sending to Google Speech Recognition...")
    print("   (This requires internet connection)")
    
    try:
        start_time = time.time()
        text = recognizer.recognize_google(audio)
        elapsed = time.time() - start_time
        
        print(f"\n✅ SUCCESS!")
        print(f"   Recognized text: '{text}'")
        print(f"   Time taken: {elapsed:.2f} seconds")
        return True
        
    except sr.UnknownValueError:
        print("\n❌ Google could not understand the audio")
        print("\n   Possible reasons:")
        print("   1. Speaking too quietly")
        print("   2. Background noise too loud")
        print("   3. Unclear pronunciation")
        print("   4. Audio quality too poor")
        print("   5. Not speaking English")
        return False
        
    except sr.RequestError as e:
        print(f"\n❌ Google Speech Recognition service error")
        print(f"   Error: {e}")
        print("\n   Possible reasons:")
        print("   1. No internet connection")
        print("   2. Google API temporarily unavailable")
        print("   3. Firewall blocking request")
        return False


def test_internet():
    """Test internet connection."""
    print("\n" + "="*70)
    print("  Test 3: Internet Connection")
    print("="*70)
    
    import urllib.request
    
    try:
        print("\n🔄 Testing connection to Google...")
        urllib.request.urlopen('https://www.google.com', timeout=5)
        print("✅ Internet connection working")
        return True
    except:
        print("❌ No internet connection")
        print("   Google Speech Recognition requires internet!")
        return False


def test_microphone_volume():
    """Test microphone volume levels."""
    print("\n" + "="*70)
    print("  Test 4: Microphone Volume")
    print("="*70)
    
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            print("\n🔇 Measuring ambient noise... (be quiet)")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            ambient = recognizer.energy_threshold
            
            print(f"   Ambient noise level: {ambient:.2f}")
            
            print("\n🎤 Now speak loudly! Say: 'Testing microphone'")
            print("   (Measuring volume...)")
            
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            
            # Estimate volume from audio data
            import audioop
            volume = audioop.rms(audio.frame_data, audio.sample_width)
            
            print(f"\n   Speech volume level: {volume}")
            print(f"   Ambient threshold: {ambient:.2f}")
            
            if volume < ambient * 1.5:
                print("\n⚠️  Speech volume is too low!")
                print("   Your voice is barely louder than background noise")
                print("   Solution: Speak MUCH louder or reduce background noise")
            elif volume < ambient * 3:
                print("\n⚠️  Speech volume is marginal")
                print("   Your voice is not much louder than background")
                print("   Solution: Speak louder or move closer to microphone")
            else:
                print("\n✅ Speech volume is good!")
            
            return True
            
    except sr.WaitTimeoutError:
        print("\n❌ No speech detected")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def main():
    """Run all diagnostics."""
    print("\n" + "="*70)
    print("  Voice Recognition Diagnostic Tool")
    print("="*70)
    print("\nThis will help identify why speech recognition is failing")
    
    input("\nPress Enter to start...")
    
    # Test internet first
    internet_ok = test_internet()
    
    # Test audio capture
    audio, recognizer = test_audio_capture()
    
    # Test volume
    if audio:
        test_microphone_volume()
    
    # Test Google recognition
    if audio and internet_ok:
        google_ok = test_google_recognition(audio, recognizer)
    else:
        google_ok = False
    
    # Summary
    print("\n" + "="*70)
    print("  Diagnostic Summary")
    print("="*70)
    
    if audio and google_ok:
        print("\n✅ Everything is working!")
        print("   Your microphone and speech recognition are fine.")
        print("\n   If voice demo still fails, try:")
        print("   1. Speak louder")
        print("   2. Speak more clearly")
        print("   3. Reduce background noise")
        print("   4. Move closer to microphone")
    else:
        print("\n❌ Issues found:")
        if not internet_ok:
            print("   ❌ No internet connection")
            print("      → Connect to internet")
        if not audio:
            print("   ❌ Microphone not capturing audio")
            print("      → Check Windows Sound settings")
            print("      → Unmute microphone")
            print("      → Increase volume to 100%")
        elif not google_ok:
            print("   ❌ Google can't understand audio")
            print("      → Speak MUCH louder")
            print("      → Speak more clearly")
            print("      → Reduce background noise")
            print("      → Move closer to microphone")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
