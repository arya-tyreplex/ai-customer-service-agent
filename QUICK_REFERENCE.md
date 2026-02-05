# TyrePlex Call Center - Quick Reference Card

## 🚀 Quick Start Commands

```bash
# 1. Setup
pip install -r requirements.txt
cp .env.example .env
# Add OPENAI_API_KEY to .env

# 2. Verify Setup
python test_tyreplex_setup.py

# 3. Run Demo
python examples/tyreplex_call_center_demo.py

# 4. Real Phone (with Twilio)
python examples/tyreplex_real_phone.py
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `src/customer_service_agent/tyreplex_voice_agent.py` | Main voice agent |
| `src/customer_service_agent/tyreplex_tools.py` | 6 specialized tools |
| `data/tyreplex_knowledge.json` | Knowledge base |
| `examples/tyreplex_call_center_demo.py` | Demo scenarios |
| `examples/tyreplex_real_phone.py` | Phone integration |

---

## 🔧 6 Tools Available

1. **get_tyre_size_for_vehicle** - Find tyre size from vehicle
2. **recommend_tyres** - Suggest tyres by budget/usage
3. **check_availability_location** - Check delivery options
4. **create_lead** - Capture customer information
5. **compare_tyres** - Compare two brands
6. **get_installation_info** - Installation details

---

## 💬 Sample Conversation Flow

```
Agent: "Thank you for calling TyrePlex..."
Customer: "I have a Maruti Swift VXI"
Agent: [Uses get_tyre_size_for_vehicle]
Agent: "The Swift VXI uses 185/65 R15 tyres..."
Customer: "What's available in my budget?"
Agent: [Uses recommend_tyres]
Agent: "Here are 3 options: MRF, CEAT, Michelin..."
Customer: "I'm in Bangalore"
Agent: [Uses check_availability_location]
Agent: "We have 38 stores in Bangalore..."
Customer: "Rahul Sharma, 9876543210"
Agent: [Uses create_lead]
Agent: "Lead ID: LEAD-xxx. We'll call you soon!"
```

---

## 🎯 Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-your-key-here

# For Real Phone Calls
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=your-token
TWILIO_PHONE_NUMBER=+1234567890
```

---

## 📊 Customization Points

### Add Vehicle
```python
# In tyreplex_tools.py → _initialize_vehicle_db()
"Your Make": {
    "Your Model": {
        "Variant": {"tyre_size": "195/65 R15", "year": "2024"}
    }
}
```

### Add Tyre
```python
# In tyreplex_tools.py → _initialize_tyre_db()
"195/65 R15": [
    {
        "brand": "Brand Name",
        "model": "Model Name",
        "price": 5000,
        "type": "Tubeless",
        "features": ["Feature 1", "Feature 2"],
        "best_for": "City driving"
    }
]
```

### Update Company Info
```json
// In data/tyreplex_knowledge.json
{
  "company_info": {
    "name": "Your Company",
    "support_phone": "Your Number"
  }
}
```

---

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| Import error | `pip install -r requirements.txt` |
| API error | Check `OPENAI_API_KEY` in `.env` |
| Twilio error | Verify webhook URLs and credentials |
| No response | Check OpenAI API key is valid |

---

## 📈 Call Analytics

```python
# Get call analytics
analytics = agent.get_call_analytics()

# Returns:
{
    "call_id": "TYREPLEX-20260205143022",
    "duration_seconds": 180.5,
    "total_turns": 8,
    "tools_used": 4,
    "lead_captured": True,
    "lead_id": "LEAD-20260205143022"
}
```

---

## 💰 Cost Per Call

| Component | Cost |
|-----------|------|
| OpenAI GPT-4o | ₹2-5 |
| OpenAI GPT-3.5 | ₹0.50-1 |
| Twilio Call | ₹0.85/min |
| Speech-to-Text | ₹0.04/15s |
| Text-to-Speech | ₹0.04/100 chars |
| **Total** | **₹5-10** |

---

## 🎓 Demo Scenarios

1. **Complete Inquiry** - Full vehicle details, lead capture
2. **Brand Comparison** - MRF vs CEAT comparison
3. **Budget Conscious** - Affordable options
4. **Premium Customer** - Best quality tyres
5. **Just Exploring** - Price checking

---

## 📞 Twilio Setup

```bash
# 1. Sign up at twilio.com
# 2. Get phone number
# 3. Configure webhooks:
#    - Incoming: https://your-domain/tyreplex/voice/incoming
#    - Status: https://your-domain/tyreplex/voice/status
# 4. For local testing:
ngrok http 5000
# Use ngrok URL in Twilio webhooks
```

---

## 🔐 Security Checklist

- [ ] `.env` file in `.gitignore`
- [ ] HTTPS for webhooks
- [ ] API keys not in code
- [ ] Input sanitization enabled
- [ ] Call logs secured
- [ ] Rate limiting configured

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| `README.md` | Quick overview |
| `README_TYREPLEX.md` | Detailed guide |
| `docs/TYREPLEX_QUICKSTART.md` | Setup instructions |
| `docs/TYREPLEX_ARCHITECTURE.md` | System architecture |
| `PROJECT_STRUCTURE.md` | File structure |
| `CLEANUP_SUMMARY.md` | What was removed |

---

## 🎯 Common Tasks

### Test Setup
```bash
python test_tyreplex_setup.py
```

### Run Demo
```bash
python examples/tyreplex_call_center_demo.py
```

### Start Phone Server
```bash
python examples/tyreplex_real_phone.py
```

### View Dashboard
```
http://localhost:5000/tyreplex/dashboard
```

### Check Logs
```bash
ls -la call_logs/
cat call_logs/TYREPLEX-*.json
```

---

## 💡 Pro Tips

1. **Start with demo** - Test without phone first
2. **Customize knowledge** - Add your vehicles and tyres
3. **Use GPT-3.5** - Cheaper for simple queries
4. **Monitor costs** - Track API usage
5. **Test thoroughly** - Try all scenarios
6. **Scale gradually** - Start small, grow as needed

---

## 🆘 Support

- **Setup Issues:** Run `python test_tyreplex_setup.py`
- **Import Errors:** Check `requirements.txt`
- **API Errors:** Verify `.env` configuration
- **Phone Issues:** Check Twilio webhooks
- **Documentation:** See `docs/` folder

---

## ✅ Success Checklist

- [ ] Dependencies installed
- [ ] OpenAI API key configured
- [ ] Demo runs successfully
- [ ] Knowledge base customized
- [ ] Vehicles added
- [ ] Tyres added
- [ ] Twilio configured (optional)
- [ ] Real calls tested (optional)
- [ ] Production deployed (optional)

---

**Quick Help:** `python test_tyreplex_setup.py`  
**Run Demo:** `python examples/tyreplex_call_center_demo.py`  
**Full Docs:** See `README_TYREPLEX.md`

---

**TyrePlex AI Call Center** - India's No. 1 Tyre Destination 🎯📞
