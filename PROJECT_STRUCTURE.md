# TyrePlex AI Call Center - Project Structure

## 📁 Directory Structure

```
tyreplex-call-center/
│
├── src/
│   └── customer_service_agent/
│       ├── __init__.py                    # Package initialization
│       ├── tyreplex_voice_agent.py        # Main voice agent
│       └── tyreplex_tools.py              # TyrePlex-specific tools
│
├── examples/
│   ├── tyreplex_call_center_demo.py       # Demo with 5 scenarios
│   └── tyreplex_real_phone.py             # Real phone integration
│
├── data/
│   └── tyreplex_knowledge.json            # Company knowledge base
│
├── docs/
│   ├── TYREPLEX_QUICKSTART.md             # Setup guide
│   └── TYREPLEX_ARCHITECTURE.md           # System architecture
│
├── call_logs/                             # Generated call logs (gitignored)
│
├── .env.example                           # Environment template
├── .gitignore                             # Git ignore rules
├── requirements.txt                       # Python dependencies
├── test_tyreplex_setup.py                 # Setup verification
├── README.md                              # Main documentation
├── README_TYREPLEX.md                     # Detailed guide
└── TYREPLEX_IMPLEMENTATION_SUMMARY.md     # Implementation details
```

## 📄 File Descriptions

### Core Files

**`src/customer_service_agent/tyreplex_voice_agent.py`**
- Main TyrePlex voice agent class
- Handles call flow and conversation management
- Integrates with OpenAI API
- Manages call metadata and analytics
- ~400 lines

**`src/customer_service_agent/tyreplex_tools.py`**
- 6 specialized tools for tyre business:
  1. get_tyre_size_for_vehicle
  2. recommend_tyres
  3. check_availability_location
  4. create_lead
  5. compare_tyres
  6. get_installation_info
- Vehicle database (make/model/variant → tyre size)
- Tyre database (brands, models, prices)
- Location database (cities, stores)
- ~600 lines

**`data/tyreplex_knowledge.json`**
- Complete TyrePlex knowledge base
- Company information
- Vehicle categories and models
- Tyre brands and specifications
- Services and locations
- FAQs and common queries
- Call handling guidelines
- ~500 lines

### Demo & Integration

**`examples/tyreplex_call_center_demo.py`**
- 5 complete customer scenarios
- Text-based simulation (no phone required)
- Shows lead capture and analytics
- ~300 lines

**`examples/tyreplex_real_phone.py`**
- Real phone integration with Twilio
- Speech-to-text and text-to-speech
- Indian English voice (Polly.Aditi)
- Live dashboard
- Webhook handlers
- ~400 lines

### Documentation

**`README.md`**
- Quick start guide
- Key features overview
- Basic usage examples

**`README_TYREPLEX.md`**
- Comprehensive project documentation
- Detailed features and benefits
- Use cases and examples
- Cost breakdown

**`docs/TYREPLEX_QUICKSTART.md`**
- Step-by-step setup instructions
- Configuration guide
- Troubleshooting tips
- Best practices

**`docs/TYREPLEX_ARCHITECTURE.md`**
- System architecture diagrams
- Data flow visualization
- Component interaction
- Deployment architecture

**`TYREPLEX_IMPLEMENTATION_SUMMARY.md`**
- Complete implementation details
- Files created
- Features implemented
- Customization guide

### Configuration

**`.env.example`**
- Environment variable template
- OpenAI API key
- Twilio credentials
- Configuration options

**`requirements.txt`**
- Python dependencies
- Core: openai, python-dotenv, loguru, tenacity
- Voice: twilio, flask
- Dev: pytest, black

**`.gitignore`**
- Python cache files
- Virtual environments
- Environment variables
- Logs and call recordings
- IDE files

### Testing

**`test_tyreplex_setup.py`**
- Verifies Python version
- Checks dependencies
- Validates environment variables
- Tests imports
- Confirms knowledge base
- ~200 lines

## 🔧 Key Components

### 1. Voice Agent (`tyreplex_voice_agent.py`)

**Classes:**
- `CallMetadata` - Stores call information
- `CompanyKnowledgeBase` - Manages company knowledge
- `TyrePlexVoiceAgent` - Main agent class

**Key Methods:**
- `start_call()` - Initialize call session
- `process_voice_input()` - Handle customer input
- `chat()` - Process messages
- `end_call()` - Close call and save logs
- `get_call_analytics()` - Get call metrics

### 2. Tools (`tyreplex_tools.py`)

**Classes:**
- `TyrePlexToolRegistry` - Tool management
- `TyrePlexTools` - Tool implementations

**Databases:**
- Vehicle DB - Make/model/variant → tyre size
- Tyre DB - Brands, models, prices, features
- Location DB - Cities, stores, delivery options

**Functions:**
- `create_tyreplex_tool_registry()` - Initialize tools

### 3. Knowledge Base (`tyreplex_knowledge.json`)

**Sections:**
- company_info
- services
- vehicle_categories
- tyre_brands
- tyre_types
- tyre_specifications
- recommendations_by_usage
- common_queries
- pricing_info
- delivery_options
- locations
- lead_qualification
- faqs
- call_handling_guidelines

## 📊 Data Flow

```
Customer Call
    ↓
Twilio (Speech-to-Text)
    ↓
Flask Webhook
    ↓
TyrePlex Voice Agent
    ↓
OpenAI API (GPT-4o)
    ↓
Tool Execution
    ↓
Knowledge Base Lookup
    ↓
Response Generation
    ↓
Twilio (Text-to-Speech)
    ↓
Customer Hears Response
```

## 🚀 Getting Started

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Add OPENAI_API_KEY
   ```

3. **Run demo:**
   ```bash
   python examples/tyreplex_call_center_demo.py
   ```

4. **For real calls:**
   ```bash
   python examples/tyreplex_real_phone.py
   ```

## 📝 Customization Points

1. **Add vehicles:** Edit `tyreplex_tools.py` → `_initialize_vehicle_db()`
2. **Add tyres:** Edit `tyreplex_tools.py` → `_initialize_tyre_db()`
3. **Update company info:** Edit `data/tyreplex_knowledge.json`
4. **Modify agent behavior:** Edit `tyreplex_voice_agent.py` → `_create_tyreplex_system_prompt()`
5. **Add new tools:** Create function in `TyrePlexTools` class and register it

## 🔐 Security

- API keys stored in `.env` (gitignored)
- Input sanitization in tools
- HTTPS for webhooks
- Call logs stored locally
- No sensitive data in code

## 📈 Scalability

- Stateless design (easy to scale horizontally)
- Redis for session management (production)
- PostgreSQL for lead storage (production)
- Load balancer for multiple instances
- Queue system for async tasks

## 🎯 Next Steps

1. Run `test_tyreplex_setup.py` to verify setup
2. Execute demo to see it in action
3. Customize knowledge base with your data
4. Add your vehicles and tyres
5. Set up Twilio for real calls
6. Deploy to production

---

**Total Lines of Code:** ~2,000 lines
**Total Files:** 15 files
**Languages:** Python, JSON, Markdown
**Dependencies:** 8 packages
