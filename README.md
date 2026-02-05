# TyrePlex AI Call Center 🎯📞

**India's First AI-Powered Tyre Call Center Agent**

Transform your tyre business with an intelligent voice agent that handles customer calls 24/7, understands vehicle requirements, recommends the perfect tyres, and captures leads automatically.

---

## 🚀 What This Does

Your TyrePlex AI Call Center Agent can:

✅ **Answer incoming calls** with natural, human-like conversations  
✅ **Identify tyre requirements** from vehicle make, model, and variant  
✅ **Recommend tyres** based on budget, usage, and preferences  
✅ **Compare brands** (MRF, CEAT, Apollo, Bridgestone, Michelin, etc.)  
✅ **Check availability** in customer's location  
✅ **Explain services** (home installation, store fitment, delivery)  
✅ **Capture leads** automatically with all details  
✅ **Handle multiple scenarios** (budget, premium, comparison, exploration)  
✅ **Speak Indian English** with natural pronunciation  
✅ **Generate analytics** on calls, leads, and performance  

---

## 📞 Quick Start

### Option 1: Text Simulation (No Phone Required)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env
# Add your OPENAI_API_KEY to .env

# 3. Run demo
python examples/tyreplex_call_center_demo.py
```

### Option 2: Real Phone Calls (with Twilio)

```bash
# 1. Configure Twilio in .env
OPENAI_API_KEY=sk-your-key
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=your-token
TWILIO_PHONE_NUMBER=+1234567890

# 2. Start server
python examples/tyreplex_real_phone.py

# 3. Expose with ngrok (for testing)
ngrok http 5000

# 4. Configure Twilio webhook
# Point to: https://your-ngrok-url/tyreplex/voice/incoming

# 5. Call your Twilio number!
```

---

## 🎯 Key Features

### 1. **Vehicle Intelligence**
- Knows 100+ vehicle makes and models
- Identifies correct tyre size automatically
- Handles variants (LXI, VXI, ZXI, etc.)
- Covers cars, bikes, scooters, and commercial vehicles

### 2. **Smart Recommendations**
- Budget-based suggestions (₹2,000 - ₹30,000)
- Usage-based (city, highway, mixed, performance)
- Brand comparisons
- Feature explanations

### 3. **Location Services**
- 1000+ partner stores across India
- Same-day delivery in major cities
- Home installation within 24 hours
- Store fitment options

### 4. **Lead Management**
- Automatic lead capture
- Complete customer information
- Urgency classification
- Follow-up scheduling
- Lead ID generation

### 5. **Natural Conversations**
- Indian English voice (Polly.Aditi)
- Understands vehicle names and brands
- Handles interruptions gracefully
- Asks clarifying questions
- Professional yet friendly tone

---

## 📊 What You Get

### Call Analytics
- Total calls handled
- Average call duration
- Lead capture rate
- Customer satisfaction scores
- Tools usage frequency
- Response times

### Lead Information
- Customer name and phone
- Vehicle details (make/model/variant)
- Tyre size
- Budget range
- Location
- Urgency level
- Timestamp
- Unique lead ID

### Conversation Logs
- Complete call transcripts
- Tool executions
- Response times
- Resolution status

---

## 🎨 Customization

### Update Your Data

**1. Company Information** (`data/tyreplex_knowledge.json`)
```json
{
  "company_info": {
    "name": "Your Company",
    "support_phone": "Your Number"
  }
}
```

**2. Add Vehicles** (`src/customer_service_agent/tyreplex_tools.py`)
```python
"Your Make": {
    "Your Model": {
        "Variant": {"tyre_size": "195/65 R15"}
    }
}
```

**3. Add Tyres**
```python
"195/65 R15": [
    {
        "brand": "Brand",
        "model": "Model",
        "price": 5000
    }
]
```

---

## 📚 Documentation

- **Quick Start:** `docs/TYREPLEX_QUICKSTART.md`
- **Architecture:** `docs/TYREPLEX_ARCHITECTURE.md`
- **Implementation:** `TYREPLEX_IMPLEMENTATION_SUMMARY.md`
- **Full Guide:** `README_TYREPLEX.md`

---

## 💰 Pricing

### Costs Per Call (Approximate)

**OpenAI API:**
- GPT-4o: ~₹2-5 per call
- GPT-3.5-turbo: ~₹0.50-1 per call

**Twilio:**
- Incoming call: ~₹0.85/minute
- Speech recognition: ~₹0.04/15 seconds
- Text-to-speech: ~₹0.04/100 characters

**Total:** ₹5-10 per call

---

## 🔧 Technical Stack

- **AI Model:** OpenAI GPT-4o / GPT-3.5-turbo
- **Voice:** Twilio Voice API
- **Speech-to-Text:** Twilio Speech Recognition
- **Text-to-Speech:** Amazon Polly (Aditi - Indian English)
- **Backend:** Python + Flask
- **Tools:** Custom function calling
- **Logging:** Loguru

---

## 🎓 Testing

Run the setup verification:
```bash
python test_tyreplex_setup.py
```

Run the demo:
```bash
python examples/tyreplex_call_center_demo.py
```

---

## 📞 Support

For questions or support:
- Email: help@tyreplex.com
- Documentation: `docs/` folder
- Issues: GitHub Issues

---

## 📄 License

MIT License - See LICENSE file for details

---

**Built with ❤️ for TyrePlex - India's No. 1 Tyre Destination**

*Revolutionizing tyre retail with AI-powered customer service*
