"""
Quick test script to verify TyrePlex Call Center setup.
Run this to ensure everything is configured correctly.
"""

import os
import sys
from dotenv import load_dotenv

print("🔍 TyrePlex Call Center - Setup Verification")
print("=" * 70)

# Load environment
load_dotenv()

# Check 1: Python version
print("\n1️⃣  Checking Python version...")
if sys.version_info >= (3, 8):
    print(f"   ✅ Python {sys.version_info.major}.{sys.version_info.minor} (OK)")
else:
    print(f"   ❌ Python {sys.version_info.major}.{sys.version_info.minor} (Need 3.8+)")
    sys.exit(1)

# Check 2: Dependencies
print("\n2️⃣  Checking dependencies...")
required_packages = [
    'openai',
    'python-dotenv',
    'pydantic',
    'loguru',
    'tenacity',
    'flask',
    'twilio'
]

missing_packages = []
for package in required_packages:
    try:
        __import__(package.replace('-', '_'))
        print(f"   ✅ {package}")
    except ImportError:
        print(f"   ❌ {package} (missing)")
        missing_packages.append(package)

if missing_packages:
    print(f"\n   ⚠️  Install missing packages: pip install {' '.join(missing_packages)}")
    sys.exit(1)

# Check 3: Environment variables
print("\n3️⃣  Checking environment variables...")
openai_key = os.getenv("OPENAI_API_KEY")
if openai_key and openai_key.startswith("sk-"):
    print(f"   ✅ OPENAI_API_KEY (configured)")
else:
    print(f"   ⚠️  OPENAI_API_KEY (not configured - required for AI features)")

twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")

if twilio_sid and twilio_token:
    print(f"   ✅ Twilio credentials (configured)")
    if twilio_phone:
        print(f"   ✅ Twilio phone number (configured)")
    else:
        print(f"   ⚠️  TWILIO_PHONE_NUMBER (not configured)")
else:
    print(f"   ⚠️  Twilio credentials (not configured - required for real phone calls)")

# Check 4: Project structure
print("\n4️⃣  Checking project structure...")
required_files = [
    'src/customer_service_agent/__init__.py',
    'src/customer_service_agent/tyreplex_voice_agent.py',
    'src/customer_service_agent/tyreplex_tools.py',
    'data/tyreplex_knowledge.json',
    'examples/tyreplex_call_center_demo.py',
    'examples/tyreplex_real_phone.py'
]

for file_path in required_files:
    if os.path.exists(file_path):
        print(f"   ✅ {file_path}")
    else:
        print(f"   ❌ {file_path} (missing)")

# Check 5: Import TyrePlex agent
print("\n5️⃣  Testing TyrePlex agent import...")
try:
    sys.path.insert(0, 'src')
    from customer_service_agent.tyreplex_voice_agent import TyrePlexVoiceAgent
    print(f"   ✅ TyrePlexVoiceAgent imported successfully")
    
    # Try to initialize
    agent = TyrePlexVoiceAgent()
    print(f"   ✅ Agent initialized (Demo mode: {agent.is_demo_mode})")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Check 6: Test knowledge base
print("\n6️⃣  Testing knowledge base...")
try:
    import json
    with open('data/tyreplex_knowledge.json', 'r') as f:
        knowledge = json.load(f)
    
    print(f"   ✅ Knowledge base loaded")
    print(f"   ℹ️  Company: {knowledge['company_info']['name']}")
    print(f"   ℹ️  Vehicle makes: {len(knowledge['vehicle_categories']['car']['popular_makes'])}")
    print(f"   ℹ️  Tyre brands: {len(knowledge['tyre_brands'])}")
    
except Exception as e:
    print(f"   ❌ Error loading knowledge base: {e}")

# Check 7: Test tools
print("\n7️⃣  Testing TyrePlex tools...")
try:
    from customer_service_agent.tyreplex_tools import create_tyreplex_tool_registry
    
    registry = create_tyreplex_tool_registry()
    tools = list(registry.tools.keys())
    
    print(f"   ✅ Tool registry created")
    print(f"   ℹ️  Available tools: {len(tools)}")
    for tool in tools:
        print(f"      - {tool}")
    
except Exception as e:
    print(f"   ❌ Error: {e}")

# Summary
print("\n" + "=" * 70)
print("📊 SETUP SUMMARY")
print("=" * 70)

if openai_key and openai_key.startswith("sk-"):
    print("✅ Ready for text simulation (demo mode)")
    print("   Run: python examples/tyreplex_call_center_demo.py")
else:
    print("⚠️  Configure OPENAI_API_KEY in .env for AI features")

if twilio_sid and twilio_token and twilio_phone:
    print("✅ Ready for real phone calls")
    print("   Run: python examples/tyreplex_real_phone.py")
else:
    print("⚠️  Configure Twilio credentials in .env for real phone calls")

print("\n💡 Next Steps:")
if not openai_key:
    print("   1. Add OPENAI_API_KEY to .env file")
    print("   2. Get API key from: https://platform.openai.com")
if not twilio_sid:
    print("   3. Sign up for Twilio: https://www.twilio.com")
    print("   4. Add Twilio credentials to .env")
print("   5. Run demo: python examples/tyreplex_call_center_demo.py")
print("   6. Review docs: docs/TYREPLEX_QUICKSTART.md")

print("\n✨ Setup verification complete!")
