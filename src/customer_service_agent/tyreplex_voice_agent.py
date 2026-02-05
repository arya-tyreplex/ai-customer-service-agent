"""
TyrePlex Voice Call Center Agent
Specialized for handling tyre inquiries, recommendations, and lead generation.
"""

import json
import time
import os
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, field

from openai import OpenAI
from loguru import logger


@dataclass
class CallMetadata:
    """Metadata for a phone call session."""
    
    call_id: str
    phone_number: Optional[str] = None
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time: Optional[str] = None
    duration_seconds: float = 0.0
    total_turns: int = 0
    customer_satisfaction: Optional[float] = None
    call_reason: Optional[str] = None
    resolution_status: str = "in_progress"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "call_id": self.call_id,
            "phone_number": self.phone_number,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_seconds": self.duration_seconds,
            "total_turns": self.total_turns,
            "customer_satisfaction": self.customer_satisfaction,
            "call_reason": self.call_reason,
            "resolution_status": self.resolution_status,
        }


class CompanyKnowledgeBase:
    """Manages company-specific knowledge and training data."""
    
    def __init__(self, knowledge_file: Optional[str] = None):
        """Initialize knowledge base."""
        self.knowledge = self._load_knowledge(knowledge_file)
        
    def _load_knowledge(self, filepath: Optional[str]) -> Dict[str, Any]:
        """Load company knowledge from file."""
        if not filepath or not os.path.exists(filepath):
            return self._get_default_knowledge()
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load knowledge file: {e}. Using defaults.")
            return self._get_default_knowledge()
    
    def _get_default_knowledge(self) -> Dict[str, Any]:
        """Get default company knowledge."""
        return {
            "company_name": "TyrePlex",
            "business_hours": "Monday-Saturday 9AM-7PM",
            "support_email": "help@tyreplex.com",
            "support_phone": "1800-XXX-XXXX"
        }
    
    def get_company_context(self) -> str:
        """Get formatted company context for the agent."""
        return f"""
COMPANY INFORMATION:
- Company: {self.knowledge.get('company_info', {}).get('name', 'TyrePlex')}
- Business Hours: {self.knowledge.get('company_info', {}).get('business_hours', 'Monday-Saturday 9AM-7PM')}
- Support: {self.knowledge.get('company_info', {}).get('support_email', 'help@tyreplex.com')}
"""


class TyrePlexVoiceAgent:
    """
    Specialized voice agent for TyrePlex call center operations.
    Handles tyre inquiries, vehicle lookups, recommendations, and lead generation.
    """
    
    def __init__(
        self,
        model: str = "gpt-4o",
        knowledge_file: str = "data/tyreplex_knowledge.json"
    ):
        """Initialize TyrePlex voice agent."""
        self.model = model
        self.knowledge_base = CompanyKnowledgeBase(knowledge_file)
        
        # Initialize OpenAI client
        self.client = None
        self.client_available = False
        self._initialize_openai_client()
        
        # Initialize tools
        from .tyreplex_tools import create_tyreplex_tool_registry
        self.tool_registry = create_tyreplex_tool_registry()
        
        # Initialize conversation state
        self.system_prompt = self._create_tyreplex_system_prompt()
        self.conversation_history: List[Dict[str, Any]] = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Call metadata
        self.call_metadata: Optional[CallMetadata] = None
        self.total_interactions = 0
        self.total_tool_calls = 0
        
        logger.info("TyrePlexVoiceAgent initialized for call center operations")
    
    def _initialize_openai_client(self) -> None:
        """Initialize OpenAI client with error handling."""
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not configured")
            
            self.client = OpenAI(api_key=api_key)
            self.client.models.list()
            self.client_available = True
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.warning(f"OpenAI client initialization failed: {str(e)}")
            self.client_available = False
            self.client = None
    
    def _create_tyreplex_system_prompt(self) -> str:
        """Create TyrePlex-specific system prompt."""
        company_context = self.knowledge_base.get_company_context()
        
        return f"""You are a professional telephone customer service representative for TyrePlex, India's No. 1 website for tyres.

{company_context}

YOUR ROLE:
You are a tyre expert helping customers find the perfect tyres for their vehicles. You handle incoming calls, understand customer needs, provide recommendations, and generate leads for the sales team.

CALL CENTER OBJECTIVES:
1. Understand customer's vehicle (make, model, variant)
2. Identify their needs (budget, usage pattern, preferences)
3. Recommend 2-3 suitable tyre options
4. Provide pricing and availability information
5. Capture lead details for follow-up
6. Book appointments or process orders

CONVERSATION FLOW:
1. GREETING: "Thank you for calling TyrePlex, India's number one tyre destination. How may I help you today?"
2. INFORMATION GATHERING: Ask about vehicle, usage, budget
3. RECOMMENDATION: Use tools to find tyre size and recommend options
4. LOCATION & DELIVERY: Check availability in customer's city
5. LEAD CAPTURE: Get customer name and phone number
6. CLOSING: Confirm follow-up and thank them

VOICE CONVERSATION STYLE:
- Speak naturally and conversationally
- Use simple language, avoid technical jargon
- Be enthusiastic about helping
- Show expertise but remain humble
- Ask clarifying questions
- Provide options

TOOLS USAGE:
- Use get_tyre_size_for_vehicle when customer mentions their vehicle
- Use recommend_tyres to suggest options based on size and budget
- Use check_availability_location to confirm delivery options
- Use create_lead to capture customer information
- Use compare_tyres when customer wants to compare brands
- Use get_installation_info when asked about installation

Remember: You're having a PHONE CONVERSATION. Sound human, friendly, and genuinely helpful!"""
    
    def start_call(
        self,
        phone_number: Optional[str] = None,
        customer_id: Optional[str] = None,
        call_source: str = "inbound"
    ) -> str:
        """Start a TyrePlex call session."""
        call_id = f"TYREPLEX-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.call_metadata = CallMetadata(
            call_id=call_id,
            phone_number=phone_number
        )
        
        logger.info(f"TyrePlex call started: {call_id} ({call_source})")
        
        greeting = "Thank you for calling TyrePlex, India's number one tyre destination. I'm here to help you find the perfect tyres for your vehicle. May I know which vehicle you have?"
        
        self.conversation_history.append({
            "role": "assistant",
            "content": greeting
        })
        
        return greeting
    
    def process_voice_input(
        self,
        text_input: str
    ) -> Dict[str, Any]:
        """Process voice input with TyrePlex-specific handling."""
        if not self.call_metadata:
            raise ValueError("No active call. Call start_call() first.")
        
        start_time = time.time()
        
        # Process the input
        response_text = self.chat(text_input)
        
        # Update call metadata
        self.call_metadata.total_turns += 1
        response_time = time.time() - start_time
        
        # Analyze if call should be wrapped up
        should_end = self._should_end_call(text_input, response_text)
        
        # Extract lead information if present
        lead_info = self._extract_lead_info()
        
        return {
            "response_text": response_text,
            "response_time": response_time,
            "should_end_call": should_end,
            "call_metadata": self.call_metadata.to_dict(),
            "lead_captured": lead_info is not None,
            "lead_info": lead_info
        }
    
    def chat(self, user_message: str) -> str:
        """Process user message and return agent response."""
        start_time = time.time()
        
        try:
            logger.info(f"Processing message: {user_message[:100]}...")
            
            # Add user message to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            # Get agent response
            response = self._get_agent_response()
            
            # Update metadata
            self.total_interactions += 1
            
            logger.info(f"Message processed successfully in {time.time() - start_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return "I apologize, but I encountered an error. Please try again or let me transfer you to our support team."
    
    def _get_agent_response(self) -> str:
        """Get response from agent, handling tool calls if needed."""
        if not self.client_available:
            return "I'm currently in demo mode. Please configure your OpenAI API key to enable full functionality."
        
        # Initial API call
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.conversation_history[-20:],  # Keep last 20 messages
            tools=self.tool_registry.get_all_schemas(),
            tool_choice="auto",
            temperature=0.7
        )
        
        response_message = response.choices[0].message
        tool_calls = getattr(response_message, "tool_calls", [])
        
        # If no tool calls, return direct response
        if not tool_calls:
            final_response = getattr(response_message, "content", "I apologize, but I couldn't generate a response.")
            self.conversation_history.append({
                "role": "assistant",
                "content": final_response
            })
            return final_response
        
        # Handle tool calls
        self.conversation_history.append(response_message.model_dump())
        
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            logger.info(f"Executing tool: {function_name}")
            
            try:
                tool_function = self.tool_registry.get_function(function_name)
                function_response = tool_function(**function_args)
                
                self.conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": function_response
                })
                
                self.total_tool_calls += 1
                
            except Exception as e:
                error_message = f"Error executing {function_name}: {str(e)}"
                logger.error(error_message)
                
                self.conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps({"error": error_message})
                })
        
        # Get final response after tool execution
        final_response = self.client.chat.completions.create(
            model=self.model,
            messages=self.conversation_history[-20:],
            temperature=0.7
        )
        
        final_message = final_response.choices[0].message.content
        self.conversation_history.append({
            "role": "assistant",
            "content": final_message
        })
        
        return final_message
    
    def _should_end_call(self, user_input: str, agent_response: str) -> bool:
        """Determine if the call should be ended."""
        end_phrases = [
            "thank you", "that's all", "goodbye", "bye",
            "have a good day", "that helps", "all set"
        ]
        return any(phrase in user_input.lower() for phrase in end_phrases)
    
    def _extract_lead_info(self) -> Optional[Dict[str, Any]]:
        """Extract lead information from conversation history."""
        for msg in reversed(self.conversation_history):
            if msg.get("role") == "tool" and "lead_id" in msg.get("content", ""):
                try:
                    lead_data = json.loads(msg["content"])
                    if lead_data.get("success"):
                        return lead_data
                except:
                    pass
        return None
    
    def end_call(
        self, 
        customer_satisfaction: Optional[float] = None,
        resolution_status: str = "lead_captured"
    ) -> Dict[str, Any]:
        """End TyrePlex call session."""
        if not self.call_metadata:
            raise ValueError("No active call to end")
        
        self.call_metadata.end_time = datetime.now().isoformat()
        self.call_metadata.resolution_status = resolution_status
        
        # Calculate duration
        start = datetime.fromisoformat(self.call_metadata.start_time)
        end = datetime.fromisoformat(self.call_metadata.end_time)
        self.call_metadata.duration_seconds = (end - start).total_seconds()
        
        if customer_satisfaction:
            self.call_metadata.customer_satisfaction = customer_satisfaction
        
        closing = "Thank you for calling TyrePlex! Our tyre expert will call you shortly. Have a great day!"
        
        lead_info = self._extract_lead_info()
        
        logger.info(f"TyrePlex call ended: {self.call_metadata.call_id}, Duration: {self.call_metadata.duration_seconds}s")
        
        summary = {
            "call_metadata": self.call_metadata.to_dict(),
            "closing_message": closing,
            "total_interactions": self.total_interactions,
            "tools_used": self.total_tool_calls,
            "lead_info": lead_info,
            "resolution_status": resolution_status
        }
        
        # Save call log
        self._save_call_log(summary)
        
        return summary
    
    def _save_call_log(self, summary: Dict[str, Any]) -> None:
        """Save call log to file."""
        try:
            os.makedirs("call_logs", exist_ok=True)
            log_file = f"call_logs/{self.call_metadata.call_id}.json"
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2)
            
            logger.info(f"Call log saved: {log_file}")
        except Exception as e:
            logger.error(f"Failed to save call log: {e}")
    
    @property
    def is_demo_mode(self) -> bool:
        """Check if agent is running in demo mode."""
        return not self.client_available
    
    def get_call_analytics(self) -> Dict[str, Any]:
        """Get analytics for the current call."""
        if not self.call_metadata:
            return {"error": "No active call"}
        
        lead_info = self._extract_lead_info()
        
        return {
            "call_id": self.call_metadata.call_id,
            "duration_seconds": self.call_metadata.duration_seconds,
            "total_turns": self.call_metadata.total_turns,
            "tools_used": self.total_tool_calls,
            "lead_captured": lead_info is not None,
            "lead_id": lead_info.get("lead_id") if lead_info else None,
            "resolution_status": self.call_metadata.resolution_status,
            "customer_satisfaction": self.call_metadata.customer_satisfaction
        }
