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

## 📞 How It Works

```
Customer calls → AI Agent answers → Understands needs → 
Recommends tyres → Captures lead → Sales team follows up
```

**Example Conversation:**

```
🤖 Agent: "Thank you for calling TyrePlex, India's number one tyre 
           destination. Which vehicle do you have?"

👤 Customer: "I have a Maruti Swift VXI"

🤖 Agent: "Great! The Maruti Swift VXI uses 185/65 R15 tyres. 
           What kind of driving do you mostly do?"

👤 Customer: "Mostly city, some highway"

🤖 Agent: "Perfect! I have 3 excellent options for you:
           1. CEAT Milaze at ₹3,800 - Best for mileage
           2. MRF ZVTV at ₹4,200 - Great all-rounder  
           3. Michelin Energy at ₹6,200 - Premium quality
           
           Which interests you?"

👤 Customer: "The MRF sounds good. I'm in Bangalore"

🤖 Agent: "Excellent choice! We have 38 stores in Bangalore with 
           same-day delivery. May I have your name and number 
           for our expert to call you with the best price?"

👤 Customer: "Rahul Sharma, 9876543210"

🤖 Agent: "Thank you Rahul! Your inquiry is registered as 
           LEAD-20260205143022. Our expert will call you within 
           2 hours. Have a great day!"
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

## 🏃 Quick Start

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

This simulates 5 customer scenarios and shows how the agent handles each.

### Option 2: Real Phone Calls (with Twilio)

```bash
# 1. Get Twilio account and phone number
# Sign up at twilio.com

# 2. Configure .env
OPENAI_API_KEY=sk-your-key
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=your-token
TWILIO_PHONE_NUMBER=+1234567890

# 3. Start server
python examples/tyreplex_real_phone.py

# 4. Expose with ngrok (for testing)
ngrok http 5000

# 5. Configure Twilio webhook
# Point to: https://your-ngrok-url/tyreplex/voice/incoming

# 6. Call your Twilio number!
```

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
- Sentiment analysis
- Resolution status

---

## 🎨 Customization

### Update Your Data

**1. Company Information** (`data/tyreplex_knowledge.json`)
```json
{
  "company_info": {
    "name": "Your Company",
    "support_phone": "Your Number",
    "business_hours": "Your Hours"
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
        "price": 5000,
        "features": ["Feature 1", "Feature 2"]
    }
]
```

**4. Modify Agent Behavior**
Edit system prompt in `tyreplex_voice_agent.py` to change:
- Greeting style
- Conversation flow
- Recommendation approach
- Closing messages

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

**Total:** ₹5-10 per call (can be optimized)

### Cost Optimization
- Use GPT-3.5-turbo for simple queries
- Cache common responses
- Optimize conversation length
- Batch processing

---

## 🔧 Technical Stack

- **AI Model:** OpenAI GPT-4o / GPT-3.5-turbo
- **Voice:** Twilio Voice API
- **Speech-to-Text:** Twilio Speech Recognition
- **Text-to-Speech:** Amazon Polly (Aditi - Indian English)
- **Backend:** Python + Flask
- **Tools:** Custom function calling
- **Logging:** Loguru
- **Session Management:** In-memory (Redis for production)

---

## 📈 Scaling

### For Production

**Infrastructure:**
- Load balancer (Nginx/HAProxy)
- Multiple server instances
- Redis for session management
- PostgreSQL/MongoDB for leads
- Queue system (Celery/RabbitMQ)

**Monitoring:**
- Call quality metrics
- API usage tracking
- Error rate monitoring
- Lead conversion tracking
- Customer satisfaction scores

**Security:**
- HTTPS for all webhooks
- Encrypted call recordings
- PCI compliance for payments
- Data sanitization
- Rate limiting

---

## 🎯 Use Cases

### 1. **Inbound Call Center**
- Handle customer inquiries
- Provide tyre recommendations
- Capture leads for sales team
- Answer FAQs
- Book appointments

### 2. **Lead Generation**
- Qualify leads automatically
- Capture complete information
- Prioritize by urgency
- Route to appropriate team
- Follow-up scheduling

### 3. **Customer Support**
- Answer product questions
- Explain services
- Provide pricing
- Check availability
- Handle comparisons

### 4. **24/7 Availability**
- No missed calls
- Instant responses
- Consistent quality
- Multilingual support (expandable)
- Holiday coverage

---

## 📚 Documentation

- **Quick Start:** `docs/TYREPLEX_QUICKSTART.md`
- **Voice Setup:** `docs/voice-agent-setup.md`
- **API Reference:** `docs/api-reference.md`
- **Deployment:** `docs/deployment.md`

---

## 🎓 Training

### For Call Center Staff
1. Review demo scenarios
2. Understand lead follow-up process
3. Learn escalation procedures
4. Practice with test calls

### For Developers
1. Study code structure
2. Understand tool system
3. Learn prompt engineering
4. Explore customization options

---

## 🚨 Support & Troubleshooting

### Common Issues

**Agent not responding?**
- Check OpenAI API key
- Verify internet connection
- Review API rate limits

**Twilio connection issues?**
- Verify webhook URLs
- Check ngrok is running
- Ensure HTTPS
- Check account balance

**Speech recognition problems?**
- Ensure good audio quality
- Check language setting (en-IN)
- Review confidence scores

---

## 🎉 Success Metrics

Track these KPIs:
- **Call Volume:** Calls handled per day
- **Lead Capture Rate:** % of calls converted to leads
- **Average Handle Time:** Duration per call
- **Customer Satisfaction:** CSAT scores
- **Conversion Rate:** Leads to sales
- **Cost Per Lead:** Total cost / leads captured
- **Response Time:** Agent response speed

---

## 🌟 Benefits

### For Business
- ✅ 24/7 availability
- ✅ Consistent quality
- ✅ Scalable operations
- ✅ Reduced costs
- ✅ Better lead capture
- ✅ Data-driven insights

### For Customers
- ✅ Instant responses
- ✅ No wait times
- ✅ Accurate information
- ✅ Personalized recommendations
- ✅ Convenient service
- ✅ Professional experience

### For Sales Team
- ✅ Qualified leads
- ✅ Complete information
- ✅ Prioritized follow-ups
- ✅ Better conversion
- ✅ Time savings
- ✅ Performance tracking

---

## 🚀 Get Started Now!

```bash
# Clone and setup
git clone <your-repo>
cd ai-customer-service-agent

# Install
pip install -r requirements.txt

# Configure
cp .env.example .env
# Add your OPENAI_API_KEY

# Run demo
python examples/tyreplex_call_center_demo.py

# For real calls
python examples/tyreplex_real_phone.py
```

---

## 📞 Contact

For questions, support, or customization:
- Email: help@tyreplex.com
- Phone: 1800-XXX-XXXX
- Website: www.tyreplex.com

---

## 📄 License

MIT License - See LICENSE file for details

---

**Built with ❤️ for TyrePlex - India's No. 1 Tyre Destination**

*Revolutionizing tyre retail with AI-powered customer service*
