"""
TyrePlex Real Phone Integration with Twilio
Handles actual phone calls with speech-to-text and text-to-speech.
"""

import os
import sys
from dotenv import load_dotenv
from flask import Flask, request, session
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from customer_service_agent.tyreplex_voice_agent import TyrePlexVoiceAgent


# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "tyreplex-secret-key-change-in-production")

# Load environment
load_dotenv()

# Initialize Twilio client
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
else:
    twilio_client = None
    print("⚠️  Twilio credentials not found. Running in demo mode.")

# Store active call sessions
active_calls = {}


@app.route("/tyreplex/voice/incoming", methods=['POST'])
def handle_incoming_call():
    """Handle incoming phone call to TyrePlex."""
    response = VoiceResponse()
    
    # Get caller information
    caller_number = request.form.get('From')
    call_sid = request.form.get('CallSid')
    
    print(f"📞 Incoming call from {caller_number} (SID: {call_sid})")
    
    # Initialize TyrePlex voice agent for this call
    agent = TyrePlexVoiceAgent(
        knowledge_file="data/tyreplex_knowledge.json"
    )
    
    # Start call session
    greeting = agent.start_call(
        phone_number=caller_number,
        call_source="inbound"
    )
    
    # Store agent in session
    active_calls[call_sid] = agent
    
    # Speak greeting and gather input
    gather = Gather(
        input='speech',
        action='/tyreplex/voice/process',
        method='POST',
        speech_timeout='auto',
        language='en-IN',  # Indian English
        hints='Maruti, Hyundai, Honda, Toyota, Swift, Creta, City, tyres, tyre size',
        profanity_filter=False
    )
    
    # Use Indian English voice
    gather.say(
        greeting,
        voice='Polly.Aditi',  # Indian English female voice
        language='en-IN'
    )
    
    response.append(gather)
    
    # If no input, redirect
    response.redirect('/tyreplex/voice/incoming')
    
    return str(response)


@app.route("/tyreplex/voice/process", methods=['POST'])
def process_speech():
    """Process customer speech input."""
    response = VoiceResponse()
    
    call_sid = request.form.get('CallSid')
    speech_result = request.form.get('SpeechResult', '')
    confidence = request.form.get('Confidence', '0')
    
    print(f"🎤 Speech: '{speech_result}' (confidence: {confidence})")
    
    # Get agent for this call
    agent = active_calls.get(call_sid)
    
    if not agent:
        response.say(
            "I'm sorry, there was an error. Please call back.",
            voice='Polly.Aditi',
            language='en-IN'
        )
        response.hangup()
        return str(response)
    
    # Handle low confidence
    if float(confidence) < 0.5:
        gather = Gather(
            input='speech',
            action='/tyreplex/voice/process',
            method='POST',
            speech_timeout='auto',
            language='en-IN'
        )
        gather.say(
            "I'm sorry, I didn't catch that. Could you please repeat?",
            voice='Polly.Aditi',
            language='en-IN'
        )
        response.append(gather)
        return str(response)
    
    # Process the speech input
    try:
        result = agent.process_voice_input(text_input=speech_result)
        agent_response = result['response_text']
        should_end = result['should_end_call']
        lead_captured = result.get('lead_captured', False)
        
        print(f"🤖 Response: {agent_response[:100]}...")
        
        if should_end or lead_captured:
            # End the call
            response.say(
                agent_response,
                voice='Polly.Aditi',
                language='en-IN'
            )
            
            # Final closing
            closing = "Thank you for calling TyrePlex. Have a great day!"
            response.say(
                closing,
                voice='Polly.Aditi',
                language='en-IN'
            )
            response.hangup()
            
            # Clean up
            resolution = "lead_captured" if lead_captured else "just_inquiry"
            agent.end_call(resolution_status=resolution)
            del active_calls[call_sid]
            
            print(f"✅ Call ended - {resolution}")
        else:
            # Continue conversation
            gather = Gather(
                input='speech',
                action='/tyreplex/voice/process',
                method='POST',
                speech_timeout='auto',
                language='en-IN',
                hints='Maruti, Hyundai, Honda, Toyota, Swift, Creta, City, tyres, MRF, CEAT, Apollo'
            )
            gather.say(
                agent_response,
                voice='Polly.Aditi',
                language='en-IN'
            )
            response.append(gather)
            
            # Fallback
            response.redirect('/tyreplex/voice/process')
    
    except Exception as e:
        print(f"❌ Error processing speech: {e}")
        response.say(
            "I'm sorry, I encountered an error. Let me transfer you to our support team.",
            voice='Polly.Aditi',
            language='en-IN'
        )
        response.hangup()
        
        if call_sid in active_calls:
            del active_calls[call_sid]
    
    return str(response)


@app.route("/tyreplex/voice/status", methods=['POST'])
def call_status():
    """Handle call status updates."""
    call_sid = request.form.get('CallSid')
    call_status = request.form.get('CallStatus')
    call_duration = request.form.get('CallDuration', '0')
    
    print(f"📊 Call {call_sid} status: {call_status} (duration: {call_duration}s)")
    
    # Clean up if call ended
    if call_status in ['completed', 'failed', 'busy', 'no-answer', 'canceled']:
        if call_sid in active_calls:
            agent = active_calls[call_sid]
            try:
                agent.end_call()
            except:
                pass
            del active_calls[call_sid]
            print(f"🧹 Cleaned up call session: {call_sid}")
    
    return '', 200


@app.route("/tyreplex/voice/fallback", methods=['POST'])
def fallback():
    """Fallback handler for errors."""
    response = VoiceResponse()
    response.say(
        "We're experiencing technical difficulties. Please call back in a few minutes.",
        voice='Polly.Aditi',
        language='en-IN'
    )
    response.hangup()
    return str(response)


def make_outbound_call(to_number: str, lead_id: str, customer_name: str):
    """
    Make an outbound call to follow up on a lead.
    
    Args:
        to_number: Customer phone number
        lead_id: Lead identifier
        customer_name: Customer's name
    """
    if not twilio_client:
        print("❌ Twilio client not initialized")
        return None
    
    message = f"Hello {customer_name}, this is calling from TyrePlex regarding your tyre inquiry {lead_id}. " \
              f"Our tyre expert will provide you with personalized recommendations and best prices. " \
              f"Please call us back at your convenience. Thank you!"
    
    try:
        call = twilio_client.calls.create(
            to=to_number,
            from_=TWILIO_PHONE_NUMBER,
            twiml=f'<Response><Say voice="Polly.Aditi" language="en-IN">{message}</Say></Response>'
        )
        
        print(f"📞 Outbound call initiated: {call.sid}")
        return call.sid
    except Exception as e:
        print(f"❌ Error making outbound call: {e}")
        return None


@app.route("/tyreplex/dashboard")
def dashboard():
    """Simple dashboard to monitor active calls."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>TyrePlex Call Center Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
            h1 { color: #e74c3c; }
            .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 20px 0; }
            .stat-card { background: #ecf0f1; padding: 20px; border-radius: 8px; text-align: center; }
            .stat-value { font-size: 32px; font-weight: bold; color: #e74c3c; }
            .stat-label { color: #7f8c8d; margin-top: 10px; }
            .active-calls { margin-top: 30px; }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background: #e74c3c; color: white; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 TyrePlex Call Center Dashboard</h1>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value">""" + str(len(active_calls)) + """</div>
                    <div class="stat-label">Active Calls</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">0</div>
                    <div class="stat-label">Waiting</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">0</div>
                    <div class="stat-label">Leads Today</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">0</div>
                    <div class="stat-label">Avg Duration</div>
                </div>
            </div>
            
            <div class="active-calls">
                <h2>Active Calls</h2>
                <table>
                    <tr>
                        <th>Call ID</th>
                        <th>Phone Number</th>
                        <th>Duration</th>
                        <th>Status</th>
                    </tr>
    """
    
    for call_sid, agent in active_calls.items():
        if agent.call_metadata:
            html += f"""
                    <tr>
                        <td>{call_sid[:20]}...</td>
                        <td>{agent.call_metadata.phone_number or 'Unknown'}</td>
                        <td>{agent.call_metadata.total_turns} turns</td>
                        <td>In Progress</td>
                    </tr>
            """
    
    if not active_calls:
        html += """
                    <tr>
                        <td colspan="4" style="text-align: center; color: #7f8c8d;">No active calls</td>
                    </tr>
        """
    
    html += """
                </table>
            </div>
            
            <div style="margin-top: 30px; padding: 20px; background: #e8f8f5; border-radius: 8px;">
                <h3>📞 Webhook URLs</h3>
                <p><strong>Incoming Call:</strong> https://your-domain.com/tyreplex/voice/incoming</p>
                <p><strong>Status Callback:</strong> https://your-domain.com/tyreplex/voice/status</p>
                <p><strong>Fallback:</strong> https://your-domain.com/tyreplex/voice/fallback</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html


if __name__ == "__main__":
    print("\n🚀 TyrePlex Call Center - Real Phone Integration")
    print("=" * 80)
    print("📞 Starting server for real phone calls with Twilio...")
    print()
    
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        print("⚠️  WARNING: Twilio credentials not configured!")
        print("   Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in .env file")
        print()
    
    print("🔧 Configuration:")
    print(f"   Twilio Phone: {TWILIO_PHONE_NUMBER or 'Not configured'}")
    print(f"   Voice: Indian English (Polly.Aditi)")
    print(f"   Language: en-IN")
    print()
    
    print("📋 Webhook URLs (configure in Twilio console):")
    print("   Incoming: https://your-domain.com/tyreplex/voice/incoming")
    print("   Status: https://your-domain.com/tyreplex/voice/status")
    print("   Fallback: https://your-domain.com/tyreplex/voice/fallback")
    print()
    
    print("💡 For local testing, use ngrok:")
    print("   ngrok http 5000")
    print("   Then use the ngrok URL in Twilio webhooks")
    print()
    
    print("🌐 Dashboard: http://localhost:5000/tyreplex/dashboard")
    print()
    print("=" * 80)
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
