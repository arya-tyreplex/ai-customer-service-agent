"""
Quick test script for Coqui TTS
Tests if TTS is working and measures latency
"""

import time
import os
import tempfile

print("="*70)
print("  Testing Coqui TTS - Free & Low Latency")
print("="*70)

print("\n1. Importing TTS...")
try:
    from TTS.api import TTS
    print("✅ TTS imported successfully")
except ImportError as e:
    print(f"❌ Failed to import TTS: {e}")
    print("\n📝 Install with: pip install TTS")
    exit(1)

print("\n2. Initializing TTS model...")
print("   (First time will download model ~100MB)")
try:
    start = time.time()
    tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False, gpu=False)
    init_time = time.time() - start
    print(f"✅ TTS initialized in {init_time:.2f} seconds")
except Exception as e:
    print(f"❌ Failed to initialize TTS: {e}")
    exit(1)

print("\n3. Testing speech synthesis...")
test_phrases = [
    "Hello! Welcome to TyrePlex.",
    "I can help you find the perfect tyres for your vehicle.",
    "This is a test of the Coqui TTS system."
]

temp_dir = tempfile.gettempdir()
total_time = 0

for i, phrase in enumerate(test_phrases, 1):
    print(f"\n   Test {i}: '{phrase}'")
    
    try:
        audio_file = os.path.join(temp_dir, f"test_tts_{i}.wav")
        
        # Measure synthesis time
        start = time.time()
        tts.tts_to_file(text=phrase, file_path=audio_file)
        synthesis_time = time.time() - start
        total_time += synthesis_time
        
        # Check file size
        file_size = os.path.getsize(audio_file) / 1024  # KB
        
        print(f"   ✅ Synthesized in {synthesis_time*1000:.0f}ms")
        print(f"   📁 File size: {file_size:.1f} KB")
        
        # Clean up
        try:
            os.remove(audio_file)
        except:
            pass
            
    except Exception as e:
        print(f"   ❌ Failed: {e}")

avg_time = (total_time / len(test_phrases)) * 1000
print(f"\n4. Performance Summary:")
print(f"   Average latency: {avg_time:.0f}ms per phrase")
print(f"   Total time: {total_time:.2f}s for {len(test_phrases)} phrases")

if avg_time < 200:
    print(f"   🎉 Excellent! Latency is under 200ms")
elif avg_time < 500:
    print(f"   ✅ Good! Latency is acceptable")
else:
    print(f"   ⚠️  Latency is higher than expected")
    print(f"   💡 Try faster models: glow-tts or speedy-speech")

print("\n5. Testing MongoDB connection...")
try:
    from src.inhouse_ml.mongodb_manager import MongoDBManager
    db = MongoDBManager()
    stats = db.get_statistics()
    print(f"✅ MongoDB connected")
    print(f"   Leads: {stats['leads']}")
    print(f"   Bookings: {stats['bookings']}")
    print(f"   Call logs: {stats['call_logs']}")
    db.close()
except Exception as e:
    print(f"⚠️  MongoDB connection failed: {e}")
    print("   Voice demo will work but won't save data")

print("\n" + "="*70)
print("  Test Complete!")
print("="*70)
print("\n✅ Coqui TTS is ready to use!")
print("💡 Run: python voice_demo_aws.py")
print("\n")
