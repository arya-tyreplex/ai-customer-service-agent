"""
FastAPI web service for the customer service agent.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging

from agent import CustomerServiceAgent
from config import AgentConfig

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Customer Service Agent API",
    description="REST API for AI-powered customer service agent",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
agent = None


class ChatRequest(BaseModel):
    message: str
    customer_id: Optional[str] = None
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    metadata: Dict[str, Any]


class WorkflowRequest(BaseModel):
    steps: List[Dict[str, str]]
    customer_id: Optional[str] = None


class WorkflowResponse(BaseModel):
    results: List[Dict[str, Any]]
    customer_id: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """Initialize the agent on startup."""
    global agent
    try:
        agent = CustomerServiceAgent()
        logger.info("Customer service agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize agent: {str(e)}")
        raise


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AI Customer Service Agent API",
        "version": "1.0.0",
        "status": "operational",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    return {"status": "healthy", "agent_info": agent.get_agent_info()}


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Chat with the customer service agent."""
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not available")

    try:
        response = agent.chat(
            user_message=request.message, customer_id=request.customer_id
        )

        return ChatResponse(
            response=response,
            conversation_id=request.conversation_id or "default",
            metadata=agent.get_agent_info(),
        )

    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/workflow", response_model=WorkflowResponse)
async def execute_workflow(request: WorkflowRequest):
    """Execute a multi-step workflow."""
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not available")

    try:
        from .models import WorkflowStep

        workflow_steps = [WorkflowStep(**step) for step in request.steps] # type: ignore

        results = agent.execute_workflow(workflow_steps)

        return WorkflowResponse(
            results=[result.to_dict() for result in results],
            customer_id=request.customer_id,
        )

    except Exception as e:
        logger.error(f"Workflow error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation history."""
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not available")

    try:
        history = agent.get_conversation_history()
        return {
            "conversation_id": conversation_id,
            "history": history,
            "total_messages": len(history),
        }

    except Exception as e:
        logger.error(f"Conversation retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/conversation/{conversation_id}")
async def reset_conversation(conversation_id: str):
    """Reset conversation history."""
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not available")

    try:
        agent.reset_conversation()
        return {"message": f"Conversation {conversation_id} reset successfully"}

    except Exception as e:
        logger.error(f"Conversation reset error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/performance")
async def get_performance_report(last_n: Optional[int] = 50):
    """Get performance report."""
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not available")

    try:
        report = agent.get_performance_report(last_n)
        return {"report": report}

    except Exception as e:
        logger.error(f"Performance report error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
