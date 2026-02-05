# TyrePlex Call Center - Quick Start Guide

## 🎯 Overview

Your TyrePlex AI Call Center Agent is ready! This system handles incoming calls, understands customer needs, recommends tyres, and captures leads automatically.

## ✨ Features

✅ **Voice Conversations** - Natural, human-like phone conversations  
✅ **Vehicle Recognition** - Identifies tyre size from make/model/variant  
✅ **Smart Recommendations** - Suggests tyres based on budget and usage  
✅ **Lead Capture** - Automatically captures customer information  
✅ **Location Services** - Checks availability and delivery options  
✅ **Brand Comparison** - Compares different tyre brands  
✅ **Real-time Processing** - Fast response times  
✅ **Call Analytics** - Tracks performance and metrics  

## 🚀 Quick Start (Text Simulation)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Run Demo

```bash
python examples/tyreplex_call_center_demo.py
```

This will simulate 5 different customer scenarios:
- Complete inquiry with lead capture
- Brand comparison
- Budget-conscious customer
- Premium customer
- Just exploring

## 📞 Real Phone Integration

### Prerequisites

1. **Twilio Account** - Sign up at [twilio.com](https://www.twilio.com)
2. **OpenAI API Key** - Get from [platform.openai.com](https://platform.openai.com)
3. **Phone Number** - Purchase a Twilio phone number

### Setup Steps

#### 1. Configure Environment Variables

Add to your `.env` file:

```bash
# OpenAI
OPENAI_API_KEY=sk-your-key-here

# Twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# Flask
FLASK_SECRET_KEY=your-secret-key-here
```

#### 2. Start the Server

```bash
python examples/tyreplex_real_phone.py
```

#### 3. Expose Local Server (for testing)

```bash
# Install ngrok
# Download from https://ngrok.com

# Run ngrok
ngrok http 5000
```

Copy the ngrok URL (e.g., `https://abc123.ngrok.io`)

#### 4. Configure Twilio Webhooks

1. Go to [Twilio Console](https://console.twilio.com)
2. Select your phone number
3. Configure Voice & Fax:
   - **A CALL COMES IN**: `https://your-ngrok-url.ngrok.io/tyreplex/voice/incoming`
   - **METHOD**: POST
   - **STATUS CALLBACK**: `https://your-ngrok-url.ngrok.io/tyreplex/voice/status`
   - **FALLBACK URL**: `https://your-ngrok-url.ngrok.io/tyreplex/voice/fallback`

#### 5. Test Your Call Center!

Call your Twilio number and talk to the AI agent!

## 🎤 Voice Features

### Speech-to-Text
- Uses Twilio's built-in speech recognition
- Optimized for Indian English (en-IN)
- Handles vehicle names, brands, and tyre terminology

### Text-to-Speech
- Indian English voice (Polly.Aditi)
- Natural, conversational tone
- Clear pronunciation of technical terms

### Conversation Hints
The system is trained to recognize:
- Vehicle brands: Maruti, Hyundai, Honda, Toyota, etc.
- Models: Swift, Creta, City, Fortuner, etc.
- Tyre brands: MRF, CEAT, Apollo, Bridgestone, Michelin
- Common terms: tyres, size, budget, delivery, installation

## 📊 Dashboard

Access the live dashboard at:
```
http://localhost:5000/tyreplex/dashboard
```

View:
- Active calls
- Call statistics
- Lead capture rate
- Average call duration

## 🛠️ Customization

### Update Company Knowledge

Edit `data/tyreplex_knowledge.json` to customize:
- Company information
- Services offered
- Vehicle database
- Tyre brands and pricing
- Locations and stores
- FAQs
- Current offers

### Add More Vehicles

In `src/customer_service_agent/tyreplex_tools.py`, update `_initialize_vehicle_db()`:

```python
"Your Make": {
    "Your Model": {
        "Variant": {"tyre_size": "195/65 R15", "year": "2024"}
    }
}
```

### Add More Tyres

Update `_initialize_tyre_db()`:

```python
"195/65 R15": [
    {
        "brand": "Brand Name",
        "model": "Model Name",
        "price": 5000,
        "type": "Tubeless",
        "features": ["Feature 1", "Feature 2"]
    }
]
```

### Modify Agent Behavior

Edit the system prompt in `src/customer_service_agent/tyreplex_voice_agent.py`:
- Change greeting style
- Adjust conversation flow
- Add new scenarios
- Modify closing messages

## 📈 Call Flow

```
1. GREETING
   ↓
2. VEHICLE IDENTIFICATION
   - Ask for make, model, variant
   - Look up tyre size
   ↓
3. NEEDS ASSESSMENT
   - Usage pattern (city/highway)
   - Budget range
   - Brand preferences
   ↓
4. RECOMMENDATIONS
   - Show 2-3 options
   - Explain features
   - Compare prices
   ↓
5. LOCATION & DELIVERY
   - Check availability
   - Offer home/store installation
   ↓
6. LEAD CAPTURE
   - Get name and phone
   - Confirm details
   - Provide lead ID
   ↓
7. CLOSING
   - Set follow-up expectations
   - Thank customer
```

## 🔧 Tools Available

The agent can use these tools automatically:

1. **get_tyre_size_for_vehicle** - Find tyre size from vehicle details
2. **recommend_tyres** - Suggest tyres based on size/budget/usage
3. **check_availability_location** - Check delivery in customer's city
4. **create_lead** - Capture customer information
5. **compare_tyres** - Compare two brands
6. **get_installation_info** - Explain installation services

## 📝 Lead Management

Leads are automatically captured with:
- Lead ID (e.g., LEAD-20260205143022)
- Customer name and phone
- Vehicle information
- Tyre size
- Location
- Budget preference
- Urgency level
- Timestamp

Access leads in call logs: `call_logs/`

## 🎯 Best Practices

### For Agents
- Let the AI handle initial qualification
- Review captured leads promptly
- Follow up within promised timeframe
- Use lead ID for reference

### For Customers
- Speak clearly
- Provide complete vehicle details
- Mention budget range
- Specify location for delivery

### For System
- Monitor call quality
- Review conversation logs
- Update knowledge base regularly
- Track conversion rates

## 🚨 Troubleshooting

### Agent Not Responding
- Check OpenAI API key is valid
- Verify internet connection
- Check API rate limits

### Twilio Connection Issues
- Verify webhook URLs are correct
- Check ngrok is running (for local testing)
- Ensure HTTPS is used
- Check Twilio account balance

### Speech Recognition Problems
- Ensure good audio quality
- Speak clearly and at moderate pace
- Check language setting (en-IN)
- Review confidence scores in logs

### Lead Not Captured
- Verify customer provided name and phone
- Check tool execution in logs
- Ensure create_lead tool is working

## 📊 Monitoring

### Key Metrics to Track
- Total calls per day
- Average call duration
- Lead capture rate
- Customer satisfaction scores
- Tools usage frequency
- Response time
- Conversion rate

### Log Files
- Call logs: `call_logs/`
- Agent logs: `customer_agent.log`
- Server logs: Console output

## 🔐 Security

### Production Checklist
- [ ] Change FLASK_SECRET_KEY
- [ ] Use HTTPS for all webhooks
- [ ] Secure Twilio credentials
- [ ] Implement rate limiting
- [ ] Add authentication for dashboard
- [ ] Encrypt call recordings
- [ ] Sanitize customer data
- [ ] Regular security audits

## 💰 Cost Optimization

### OpenAI API
- Use GPT-3.5-turbo for simple queries
- Cache common responses
- Set max_tokens limits
- Monitor token usage

### Twilio
- Optimize call duration
- Use efficient speech recognition
- Implement call queuing
- Monitor usage patterns

## 🚀 Scaling

### For High Volume
1. **Load Balancing** - Multiple server instances
2. **Redis** - Session management
3. **Database** - Store leads in PostgreSQL/MongoDB
4. **Queue System** - RabbitMQ or Celery for async tasks
5. **CDN** - Serve static assets
6. **Monitoring** - Datadog, New Relic, or Prometheus

### Deployment Options
- **AWS**: EC2, ECS, or Lambda
- **Google Cloud**: Compute Engine or Cloud Run
- **Azure**: App Service or Functions
- **Heroku**: Easy deployment
- **DigitalOcean**: Droplets or App Platform

## 📞 Support

For issues or questions:
- Check logs in `call_logs/` and `customer_agent.log`
- Review Twilio console for call details
- Test with demo first: `python examples/tyreplex_call_center_demo.py`
- Verify all environment variables are set

## 🎓 Training

### For Call Center Staff
1. Run demo scenarios
2. Review conversation logs
3. Understand tool capabilities
4. Learn escalation procedures
5. Practice lead follow-up

### For Developers
1. Review code in `src/customer_service_agent/`
2. Understand tool registry system
3. Learn prompt engineering
4. Study conversation flow
5. Explore customization options

## 🎉 You're Ready!

Your TyrePlex AI Call Center is now operational. Start with the demo, then move to real phone integration when ready.

**Next Steps:**
1. Run the demo
2. Customize knowledge base
3. Set up Twilio
4. Test with real calls
5. Monitor and optimize
6. Scale as needed

Happy calling! 🚀📞
