# In-House TyrePlex System Architecture (No Cloud Dependencies)

## 🎯 Overview

Complete self-hosted solution without OpenAI, AWS, or any cloud services. Everything runs on your own servers.

---

## 🏗️ System Components

### 1. Speech-to-Text (STT) - Local
**Technology:** Whisper (OpenAI's open-source model)
- Runs locally on your server
- No API calls
- Supports multiple languages including Indian English
- Accuracy: 95%+

**Alternatives:**
- Vosk (lighter, faster)
- DeepSpeech (Mozilla)
- Kaldi (research-grade)

### 2. Text-to-Speech (TTS) - Local
**Technology:** Coqui TTS or Piper TTS
- Runs locally
- Natural-sounding voices
- Indian English voices available
- Low latency

**Alternatives:**
- Festival TTS
- eSpeak-ng
- MaryTTS

### 3. Intent Classification - Your ML Model
**Technology:** Scikit-learn / XGBoost
- Trained on your CSV data
- Fast inference (<10ms)
- No external dependencies
- Easy to update

**Model Types:**
- Random Forest (for classification)
- XGBoost (for recommendations)
- Logistic Regression (for simple intents)

### 4. Vehicle/Tyre Matching - Elasticsearch
**Technology:** Elasticsearch (self-hosted)
- Fuzzy search for typos
- Phonetic matching
- Vector search for semantic matching
- Sub-second response times

### 5. Voice Activity Detection (VAD)
**Technology:** WebRTC VAD or Silero VAD
- Detects when customer stops speaking
- Prevents overlapping
- Low latency (<50ms)

### 6. Call Management
**Technology:** FreeSWITCH or Asterisk
- Open-source PBX
- SIP protocol
- Call routing
- Recording

---

## 📊 Data Flow (No Overlapping)

```
1. Customer starts speaking
   ↓
2. VAD detects voice activity
   ↓
3. Audio buffered (no AI response yet)
   ↓
4. VAD detects silence (customer stopped)
   ↓
5. Audio sent to Whisper STT
   ↓
6. Text processed by ML model
   ↓
7. Response generated
   ↓
8. TTS converts to speech
   ↓
9. Audio played to customer
   ↓
10. System waits for customer (back to step 1)
```

**Key:** AI only speaks AFTER customer finishes (VAD confirms silence)

---

## 🔧 Technology Stack

### Core Components
```
┌─────────────────────────────────────────┐
│         Your Server (Linux)              │
├─────────────────────────────────────────┤
│ 1. FreeSWITCH/Asterisk (Call handling)  │
│ 2. Whisper (STT) - GPU recommended      │
│ 3. Coqui TTS (TTS) - CPU/GPU            │
│ 4. Elasticsearch (Search)                │
│ 5. Python ML Model (Your trained model) │
│ 6. WebRTC VAD (Turn detection)          │
│ 7. Flask/FastAPI (Orchestration)        │
└─────────────────────────────────────────┘
```

### Hardware Requirements

**Minimum:**
- CPU: 8 cores
- RAM: 16GB
- Storage: 100GB SSD
- Network: 100Mbps

**Recommended:**
- CPU: 16 cores
- RAM: 32GB
- GPU: NVIDIA (for faster Whisper)
- Storage: 500GB SSD
- Network: 1Gbps

---

## 🎓 Training Your Own Model

### Step 1: Prepare CSV Data

Your CSV should have columns like:
```csv
vehicle_make,vehicle_model,variant,tyre_size,tyre_brand,tyre_model,price,usage_type,customer_budget
Maruti Suzuki,Swift,VXI,185/65 R15,MRF,ZVTV,4200,city,mid
Hyundai,Creta,SX,215/65 R16,CEAT,CrossDrive,5800,mixed,mid
...
```

### Step 2: Train Classification Model

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import pandas as pd

# Load your CSV
df = pd.read_csv('tyreplex_data.csv')

# Encode categorical variables
le_make = LabelEncoder()
le_model = LabelEncoder()
df['make_encoded'] = le_make.fit_transform(df['vehicle_make'])
df['model_encoded'] = le_model.fit_transform(df['vehicle_model'])

# Features and target
X = df[['make_encoded', 'model_encoded', 'customer_budget']]
y = df['tyre_brand']

# Train model
model = RandomForestClassifier(n_estimators=100)
model.fit(X, y)

# Save model
import joblib
joblib.dump(model, 'tyre_recommendation_model.pkl')
```

### Step 3: Use Model for Predictions

```python
# Load model
model = joblib.load('tyre_recommendation_model.pkl')

# Predict
prediction = model.predict([[make_encoded, model_encoded, budget]])
```

---

## 🔍 Elasticsearch Integration

### Setup

```bash
# Install Elasticsearch
docker run -d -p 9200:9200 -e "discovery.type=single-node" elasticsearch:8.11.0
```

### Index Your Data

```python
from elasticsearch import Elasticsearch

es = Elasticsearch(['http://localhost:9200'])

# Index vehicles
for _, row in df.iterrows():
    doc = {
        'vehicle_make': row['vehicle_make'],
        'vehicle_model': row['vehicle_model'],
        'variant': row['variant'],
        'tyre_size': row['tyre_size'],
        'tyre_brand': row['tyre_brand'],
        'price': row['price']
    }
    es.index(index='tyreplex', document=doc)
```

### Fuzzy Search

```python
# Search with typos
query = {
    "query": {
        "multi_match": {
            "query": "Maruti Swft",  # Typo: "Swft" instead of "Swift"
            "fields": ["vehicle_make", "vehicle_model"],
            "fuzziness": "AUTO"
        }
    }
}

results = es.search(index='tyreplex', body=query)
# Returns: Maruti Swift (corrected)
```

---

## 🎤 Voice Activity Detection (No Overlapping)

### Using Silero VAD

```python
import torch
import torchaudio

# Load VAD model
model, utils = torch.hub.load(
    repo_or_dir='snakers4/silero-vad',
    model='silero_vad'
)

(get_speech_timestamps, _, read_audio, *_) = utils

# Detect speech in audio
wav = read_audio('audio.wav')
speech_timestamps = get_speech_timestamps(wav, model)

# Check if customer is speaking
is_speaking = len(speech_timestamps) > 0

# Only respond when customer stops (silence detected)
if not is_speaking:
    # Generate AI response
    pass
```

### Turn-Taking Logic

```python
class TurnManager:
    def __init__(self):
        self.customer_speaking = False
        self.silence_duration = 0
        self.silence_threshold = 1.0  # 1 second of silence
    
    def process_audio_chunk(self, audio_chunk):
        # Check if speech detected
        has_speech = self.vad.detect_speech(audio_chunk)
        
        if has_speech:
            self.customer_speaking = True
            self.silence_duration = 0
        else:
            self.silence_duration += 0.1  # 100ms chunks
        
        # Customer finished speaking?
        if self.customer_speaking and self.silence_duration >= self.silence_threshold:
            self.customer_speaking = False
            return "CUSTOMER_FINISHED"
        
        return "CUSTOMER_SPEAKING" if self.customer_speaking else "WAITING"
```

---

## 🚀 Complete Implementation

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Customer Phone                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              FreeSWITCH / Asterisk (PBX)                 │
│  • Handles SIP calls                                     │
│  • Routes to Python application                          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                 WebRTC Audio Stream                      │
│  • Real-time audio streaming                             │
│  • Bidirectional communication                           │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Voice Activity Detection (VAD)              │
│  • Silero VAD (local)                                    │
│  • Detects when customer stops speaking                  │
│  • Prevents AI from interrupting                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼ (Only when customer stops)
┌─────────────────────────────────────────────────────────┐
│              Whisper STT (Local GPU/CPU)                 │
│  • Converts speech to text                               │
│  • Runs on your server                                   │
│  • No API calls                                          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Intent Classifier (Your Model)              │
│  • Trained on your CSV                                   │
│  • Classifies: vehicle_inquiry, tyre_recommendation,     │
│    price_check, availability, lead_capture               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   Elasticsearch                          │
│  • Fuzzy search for vehicles                             │
│  • Phonetic matching                                     │
│  • Fast retrieval (<50ms)                                │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              ML Model + Rule Engine                      │
│  • Your trained model (scikit-learn/XGBoost)             │
│  • Business rules                                        │
│  • Recommendation logic                                  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Response Generator                          │
│  • Template-based responses                              │
│  • Dynamic content insertion                             │
│  • Natural language generation                           │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Coqui TTS (Local)                           │
│  • Text to speech                                        │
│  • Indian English voice                                  │
│  • Runs on your server                                   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Audio Playback                              │
│  • Streams to customer                                   │
│  • Waits for customer response                           │
└─────────────────────────────────────────────────────────┘
```

---

## 💰 Cost Comparison

### Cloud-Based (Current)
- OpenAI API: ₹5-10 per call
- Twilio: ₹2-3 per call
- **Total: ₹7-13 per call**
- **1000 calls/month: ₹7,000-13,000**

### In-House (Proposed)
- Server cost: ₹10,000-20,000/month (one-time setup + hosting)
- Electricity: ₹2,000/month
- **Total: ₹12,000-22,000/month**
- **Cost per call: ₹12-22 (for 1000 calls)**
- **Break-even: ~2 months**
- **After 6 months: 70% cost savings**

---

## 🔐 Benefits of In-House

1. **Data Privacy** - All data stays on your servers
2. **No API Limits** - Unlimited calls
3. **Customization** - Full control over models
4. **Cost Savings** - After initial setup
5. **No Vendor Lock-in** - Own your infrastructure
6. **Faster Response** - No network latency
7. **Offline Capable** - Works without internet

---

## 📋 Implementation Checklist

- [ ] Set up Linux server (Ubuntu 22.04 recommended)
- [ ] Install Elasticsearch
- [ ] Install Whisper (local STT)
- [ ] Install Coqui TTS (local TTS)
- [ ] Set up FreeSWITCH/Asterisk
- [ ] Implement VAD (Silero)
- [ ] Train ML model on your CSV
- [ ] Index data in Elasticsearch
- [ ] Build orchestration layer (Python)
- [ ] Test turn-taking logic
- [ ] Deploy and monitor

---

## 🎯 Next Steps

1. **Share your CSV structure** - I'll create the exact ML model
2. **Confirm server specs** - I'll optimize for your hardware
3. **Choose components** - Whisper vs Vosk, Coqui vs Piper, etc.
4. **Build proof of concept** - Test with sample data
5. **Deploy to production** - Full system setup

---

**Ready to build a 100% in-house solution?** 🚀

No OpenAI. No cloud. Complete control.
