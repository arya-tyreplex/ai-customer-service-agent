"""
Microphone Diagnostic Tool
Test your microphone before using voice demo
"""

import speech_recognition as sr
import pyaudio

def list_microphones():
    """List all available microphones."""
    print("\n" + "="*70)
    print("  Available Microphones")
    print("="*70)
    
    try:
        mic_list = sr.Microphone.list_microphone_names()
        print(f"\nFound {len(mic_list)} audio device(s):\n")
        for i, name in enumerate(mic_list):
            print(f"  {i}: {name}")
        print("\n" + "="*70)
        return mic_list
    except Exception as e:
        print(f"\n❌ Error listing microphones: {e}")
        return []


def test_audio_devices():
    """Test PyAudio devices."""
    print("\n" + "="*70)
    print("  PyAudio Devices")
    print("="*70)
    
    try:
        p = pyaudio.PyAudio()
        device_count = p.get_device_count()
        print(f"\nFound {device_count} audio device(s):\n")
        
        for i in range(device_count):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:  # Input device
                print(f"  [{i}] {info['name']}")
                print(f"      Input channels: {info['maxInputChannels']}")
                print(f"      Sample rate: {info['defaultSampleRate']}")
                print()
        
        p.terminate()
        print("="*70)
    except Exception as e:
        print(f"\n❌ Error testing audio devices: {e}")


def test_microphone_recording():
    """Test microphone by recording and recognizing speech."""
    print("\n" + "="*70)
    print("  Microphone Recording Test")
    print("="*70)
    
    recognizer = sr.Recognizer()
    
    # Show current settings
    print(f"\nCurrent settings:")
    print(f"  Energy threshold: {recognizer.energy_threshold}")
    print(f"  Dynamic threshold: {recognizer.dynamic_energy_threshold}")
    print(f"  Pause threshold: {recognizer.pause_threshold}s")
    
    try:
        with sr.Microphone() as source:
            print("\n🔇 Calibrating for ambient noise...")
            print("   (Please be quiet for 2 seconds)")
            recognizer.adjust_for_ambient_noise(source, duration=2)
            
            print(f"\n✅ Calibration complete!")
            print(f"   New energy threshold: {recognizer.energy_threshold}")
            
            print("\n🎤 Speak now! Say something like:")
            print("   'Hello, this is a microphone test'")
            print("   (You have 5 seconds)")
            
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            print("\n✅ Audio captured!")
            print("   Processing with Google Speech Recognition...")
            
            try:
                text = recognizer.recognize_google(audio)
                print(f"\n✅ SUCCESS! Recognized text:")
                print(f"   '{text}'")
                print("\n🎉 Your microphone is working perfectly!")
                return True
                
            except sr.UnknownValueError:
                print("\n⚠️  Audio captured but speech not understood")
                print("   Possible issues:")
                print("   - Speaking too quietly")
                print("   - Background noise too loud")
                print("   - Unclear pronunciation")
                print("\n💡 Try again and speak louder and clearer")
                return False
                
            except sr.RequestError as e:
                print(f"\n❌ Speech recognition service error: {e}")
                print("   Check your internet connection")
                print("   (Google Speech Recognition requires internet)")
                return False
    
    except sr.WaitTimeoutError:
        print("\n⚠️  No audio detected (timeout)")
        print("   Possible issues:")
        print("   - Microphone not connected")
        print("   - Microphone muted in Windows settings")
        print("   - Wrong microphone selected as default")
        print("   - Microphone volume too low")
        print("\n💡 Check Windows Sound settings:")
        print("   1. Right-click speaker icon in taskbar")
        print("   2. Select 'Sound settings'")
        print("   3. Check 'Input' device and volume")
        return False
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False
    
    finally:
        print("\n" + "="*70)


def main():
    """Run all microphone diagnostics."""
    print("\n" + "="*70)
    print("  TyrePlex Voice Demo - Microphone Diagnostic")
    print("="*70)
    
    # List microphones
    list_microphones()
    
    # Test PyAudio devices
    test_audio_devices()
    
    # Test recording
    input("\nPress Enter to test microphone recording...")
    result = test_microphone_recording()
    
    # Summary
    print("\n" + "="*70)
    print("  Summary")
    print("="*70)
    
    if result:
        print("\n✅ Microphone is working!")
        print("\n📝 You can now run the voice demo:")
        print("   ./run.sh demo")
        print("   Choose option 2")
    else:
        print("\n❌ Microphone test failed")
        print("\n📝 Troubleshooting steps:")
        print("   1. Check microphone is connected")
        print("   2. Check Windows Sound settings")
        print("   3. Unmute microphone")
        print("   4. Increase microphone volume")
        print("   5. Select correct default microphone")
        print("\n📝 Or use text demo instead:")
        print("   ./run.sh demo")
        print("   Choose option 1")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
