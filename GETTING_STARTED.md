# Getting Started with TyrePlex AI Call Center

## 🎯 Welcome!

You now have a complete AI-powered call center for your tyre business. This guide will get you up and running in **5 minutes**.

---

## ⚡ 5-Minute Quick Start

### Step 1: Install Dependencies (1 minute)

```bash
pip install -r requirements.txt
```

### Step 2: Configure API Key (1 minute)

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
# Get key from: https://platform.openai.com/api-keys
```

Your `.env` should look like:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

### Step 3: Verify Setup (1 minute)

```bash
python test_tyreplex_setup.py
```

You should see all green checkmarks ✅

### Step 4: Run Demo (2 minutes)

```bash
python examples/tyreplex_call_center_demo.py
```

Watch the AI agent handle 5 different customer scenarios!

---

## 🎉 That's It!

You're now ready to:
- ✅ Handle customer calls
- ✅ Recommend tyres
- ✅ Capture leads
- ✅ Generate analytics

---

## 📞 What Just Happened?

The demo showed you 5 customer scenarios:

1. **Complete Inquiry** - Customer with Maruti Swift
2. **Brand Comparison** - Comparing MRF vs CEAT
3. **Budget Conscious** - Looking for affordable options
4. **Premium Customer** - Wants best quality
5. **Just Exploring** - Checking prices

Each scenario demonstrated:
- Natural conversation
- Vehicle identification
- Tyre recommendations
- Lead capture
- Call analytics

---

## 🚀 Next Steps

### Option A: Customize for Your Business (10 minutes)

1. **Add Your Vehicles**
   - Open `src/customer_service_agent/tyreplex_tools.py`
   - Find `_initialize_vehicle_db()`
   - Add your vehicles:
   ```python
   "Your Make": {
       "Your Model": {
           "Variant": {"tyre_size": "195/65 R15", "year": "2024"}
       }
   }
   ```

2. **Add Your Tyres**
   - Same file, find `_initialize_tyre_db()`
   - Add your inventory:
   ```python
   "195/65 R15": [
       {
           "brand": "Your Brand",
           "model": "Model Name",
           "price": 5000,
           "features": ["Feature 1", "Feature 2"]
       }
   ]
   ```

3. **Update Company Info**
   - Edit `data/tyreplex_knowledge.json`
   - Change company name, phone, hours, etc.

4. **Test Again**
   ```bash
   python examples/tyreplex_call_center_demo.py
   ```

### Option B: Set Up Real Phone Calls (30 minutes)

1. **Sign Up for Twilio**
   - Go to [twilio.com](https://www.twilio.com)
   - Create free account
   - Get a phone number

2. **Configure Twilio**
   - Add to `.env`:
   ```
   TWILIO_ACCOUNT_SID=ACxxxxx
   TWILIO_AUTH_TOKEN=your-token
   TWILIO_PHONE_NUMBER=+1234567890
   ```

3. **Start Server**
   ```bash
   python examples/tyreplex_real_phone.py
   ```

4. **Expose with ngrok** (for testing)
   ```bash
   # Install ngrok from ngrok.com
   ngrok http 5000
   ```

5. **Configure Twilio Webhook**
   - Go to Twilio console
   - Select your phone number
   - Set webhook to: `https://your-ngrok-url/tyreplex/voice/incoming`

6. **Call Your Number!**
   - Call your Twilio number
   - Talk to the AI agent
   - Watch the magic happen ✨

---

## 💡 Understanding the System

### What the Agent Does

```
1. Answers call with greeting
2. Asks about vehicle
3. Looks up tyre size
4. Asks about budget and usage
5. Recommends 2-3 tyres
6. Checks location availability
7. Captures customer details
8. Provides lead ID
9. Thanks and closes call
```

### Tools the Agent Uses

The agent automatically uses these 6 tools:

1. **get_tyre_size_for_vehicle** - "Maruti Swift VXI" → "185/65 R15"
2. **recommend_tyres** - Shows MRF, CEAT, Michelin options
3. **check_availability_location** - "Bangalore" → 38 stores
4. **create_lead** - Saves customer info with Lead ID
5. **compare_tyres** - MRF vs CEAT comparison
6. **get_installation_info** - Home/store installation details

### How It Works

```
Customer speaks
    ↓
Twilio converts speech to text
    ↓
Flask receives text
    ↓
TyrePlex Agent processes
    ↓
OpenAI understands and selects tools
    ↓
Tools execute (lookup vehicle, recommend tyres, etc.)
    ↓
OpenAI generates natural response
    ↓
Twilio converts text to speech
    ↓
Customer hears response
```

---

## 📊 Viewing Results

### Call Logs

After each call, a log is saved:
```bash
ls call_logs/
cat call_logs/TYREPLEX-20260205143022.json
```

Contains:
- Call duration
- Customer details
- Tools used
- Lead information
- Conversation history

### Analytics

```python
from customer_service_agent import TyrePlexVoiceAgent

agent = TyrePlexVoiceAgent()
# ... after call ...
analytics = agent.get_call_analytics()
print(analytics)
```

Shows:
- Call ID
- Duration
- Number of turns
- Tools used
- Lead captured
- Customer satisfaction

---

## 🎓 Learning More

### Documentation

- **Quick Reference:** `QUICK_REFERENCE.md` - Cheat sheet
- **Full Guide:** `README_TYREPLEX.md` - Complete documentation
- **Setup Guide:** `docs/TYREPLEX_QUICKSTART.md` - Detailed setup
- **Architecture:** `docs/TYREPLEX_ARCHITECTURE.md` - How it works
- **Project Structure:** `PROJECT_STRUCTURE.md` - File organization

### Examples

- **Demo:** `examples/tyreplex_call_center_demo.py` - 5 scenarios
- **Real Phone:** `examples/tyreplex_real_phone.py` - Twilio integration

### Code

- **Agent:** `src/customer_service_agent/tyreplex_voice_agent.py`
- **Tools:** `src/customer_service_agent/tyreplex_tools.py`
- **Knowledge:** `data/tyreplex_knowledge.json`

---

## 🆘 Troubleshooting

### "Module not found"
```bash
pip install -r requirements.txt
```

### "OpenAI API key not configured"
```bash
# Check .env file exists
cat .env

# Should show: OPENAI_API_KEY=sk-...
# If not, add it
```

### "Demo not working"
```bash
# Run verification
python test_tyreplex_setup.py

# Check all items are ✅
```

### "Twilio webhook error"
```bash
# Make sure ngrok is running
ngrok http 5000

# Use the HTTPS URL in Twilio
# NOT the HTTP URL
```

---

## 💰 Cost Estimate

### Per Call
- OpenAI: ₹2-5
- Twilio: ₹2-3
- **Total: ₹5-10 per call**

### Monthly (1000 calls)
- **₹5,000 - ₹10,000**

### Ways to Reduce Costs
1. Use GPT-3.5-turbo instead of GPT-4o (50% cheaper)
2. Optimize conversation length
3. Cache common responses
4. Use Twilio's free tier for testing

---

## ✅ Success Checklist

- [ ] Dependencies installed
- [ ] OpenAI API key added to `.env`
- [ ] Setup verification passed
- [ ] Demo runs successfully
- [ ] Understood how it works
- [ ] Customized with your data (optional)
- [ ] Twilio configured (optional)
- [ ] Real calls tested (optional)

---

## 🎯 What's Next?

### Today
1. ✅ Run demo
2. ✅ Understand the flow
3. ✅ Review documentation

### This Week
1. Customize knowledge base
2. Add your vehicles and tyres
3. Test with your team
4. Set up Twilio

### This Month
1. Deploy to production
2. Train your team
3. Monitor performance
4. Optimize costs

---

## 🌟 Tips for Success

1. **Start Simple** - Use demo mode first
2. **Test Thoroughly** - Try all scenarios
3. **Customize Gradually** - Add data incrementally
4. **Monitor Closely** - Watch first calls carefully
5. **Iterate Quickly** - Improve based on feedback
6. **Scale Smartly** - Grow as you learn

---

## 📞 Need Help?

1. **Check Documentation** - See `docs/` folder
2. **Run Verification** - `python test_tyreplex_setup.py`
3. **Review Examples** - See `examples/` folder
4. **Check Logs** - Look in `call_logs/` folder

---

## 🎉 You're Ready!

You now have everything you need to run an AI-powered call center for your tyre business.

**Start with:**
```bash
python examples/tyreplex_call_center_demo.py
```

**Then customize and deploy!**

---

**Welcome to the future of tyre retail! 🚀**

*TyrePlex AI Call Center - India's No. 1 Tyre Destination* 🎯📞
