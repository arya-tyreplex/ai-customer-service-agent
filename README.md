# TyrePlex AI Customer Service Agent

Complete AI-powered customer service agent for TyrePlex with voice support, ML recommendations, and booking system.

## 🎯 Features

### Voice Agent (FREE & FAST)
- **Coqui TTS** - Free, open-source text-to-speech (<200ms latency)
- **Google Speech Recognition** - Free speech-to-text
- **Bilingual Support** - English, Hindi, Hinglish
- **Natural Conversation** - Human-like interaction
- **Complete Booking Flow** - 12-step end-to-end process

### ML System
- **Brand Recommender** - Suggests best tyre brands
- **Price Predictor** - Estimates tyre prices
- **Size Predictor** - Determines correct tyre size
- **Intent Classifier** - Understands customer needs

### Database Integration
- **MongoDB** - Stores leads, bookings, call logs
- **Elasticsearch** - Fast search across 140K+ records
- **Real-time Updates** - Instant data synchronization

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Environment
```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Start Services
```bash
# Start MongoDB
docker-compose up -d mongodb

# Or use the run script
./run.sh
```

### 4. Run Voice Agent
```bash
python voice_demo_aws.py
```

## 📦 What's Included

### Voice Demos
- `voice_demo_aws.py` - **MAIN** - Coqui TTS (FREE, <200ms latency)
- `voice_demo_natural.py` - Alternative with Google TTS
- `voice_demo_local.py` - Offline with pyttsx3

### Test Scripts
- `test_coqui_tts.py` - Test TTS and measure latency
- `test_complete_system.py` - Test ML system
- `test_mongodb_insertion.py` - Test database
- `test_microphone.py` - Test audio input

### Setup & Training
- `setup_csv.py` - Process CSV data
- `train_complete_system.py` - Train ML models
- `demo.py` - Interactive demo

### Utilities
- `cleanup.py` - Clean cache files
- `diagnose_voice.py` - Voice diagnostics

## 🎤 Voice Agent Features

### Complete Booking Flow
1. ✅ Greeting & name collection
2. ✅ Services presentation
3. ✅ Need understanding with topic validation
4. ✅ Vehicle details (make → model → variant)
5. ✅ ML-powered tyre recommendations
6. ✅ Interactive selection (first/second/third)
7. ✅ Booking question
8. ✅ Contact collection (phone, city)
9. ✅ Installation scheduling (date, time)
10. ✅ Booking confirmation
11. ✅ Database saving (leads, bookings, call logs)
12. ✅ Professional closing

### Language Support
- **English** - Full support
- **Hindi** - Romanized text (works well)
- **Hinglish** - Code-mixing supported

## 💾 Database Collections

### MongoDB
- **leads** - Customer information and vehicle details
- **call_logs** - Call metadata and recommendations
- **bookings** - Installation bookings with scheduling
- **vehicles** - Vehicle specifications
- **tyres** - Tyre catalog with pricing

## 🔧 Requirements

### Core
- Python 3.10+
- MongoDB
- PyAudio (for microphone input)

### Voice Agent
- TTS (Coqui TTS) - FREE!
- torch & torchaudio
- SpeechRecognition
- pygame

### ML System
- scikit-learn
- pandas
- numpy

## 📊 Performance

| Metric | Value |
|--------|-------|
| **TTS Latency** | <200ms |
| **Cost** | $0 (FREE) |
| **Voice Quality** | Very Good |
| **Recognition Accuracy** | High (Indian English) |
| **ML Models** | 4 trained models |
| **Database** | MongoDB + Elasticsearch |

## 🎯 Use Cases

1. **Inbound Calls** - Handle customer inquiries
2. **Tyre Recommendations** - ML-powered suggestions
3. **Booking Management** - Schedule installations
4. **Lead Tracking** - CRM integration
5. **Call Analytics** - Performance metrics

## 📝 Documentation

See individual files for detailed documentation:
- Voice agent implementation
- ML model training
- Database schema
- API endpoints

## 🛠️ Development

### Run Tests
```bash
# Test TTS
python test_coqui_tts.py

# Test ML system
python test_complete_system.py

# Test MongoDB
python test_mongodb_insertion.py
```

### Clean Cache
```bash
python cleanup.py
```

### Train Models
```bash
python train_complete_system.py
```

## � Security

- ✅ `.env` files in `.gitignore`
- ✅ No credentials in code
- ✅ Use `.env.example` for templates
- ✅ MongoDB authentication supported

## 📄 License

Proprietary - TyrePlex Internal Use

## � Support

For issues or questions, contact the development team.

---

**Built with ❤️ for TyrePlex**
