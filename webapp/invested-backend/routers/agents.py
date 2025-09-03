from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Dict, Any, Optional
import sys
import os
import asyncio
import json

# Add the agents directory to the path
agents_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'agents')
sys.path.append(agents_path)

# Import agent functions
try:
    from oracle import process_oracle_query
    from guardian import run_guardian_analysis
    from catalyst import run_catalyst_analysis
    from strategist import run_strategist_analysis
except ImportError as e:
    print(f"Warning: Could not import agent modules: {e}")
    print(f"Agents path: {agents_path}")
    # Create dummy functions for testing
    async def process_oracle_query(uid: str, question: str):
        return {"response": "Oracle agent not available"}
    async def run_guardian_analysis(uid: str):
        return {"alerts": "Guardian agent not available"}
    async def run_catalyst_analysis(uid: str):
        return {"tips": "Catalyst agent not available"}
    async def run_strategist_analysis(uid: str):
        return {"portfolio_analysis": "Strategist agent not available"}

# Import authentication - use absolute import to avoid relative import issues
import sys
import os
sys.path.append(os.path.dirname(__file__))

# We'll define a simple authentication function here to avoid circular imports
async def get_current_phone_number(token: str = None):
    # For now, return a default phone number for testing
    # In production, this should validate the JWT token
    return "2222222222"

# Add error handling for agent calls
def handle_agent_error(agent_name: str, error: Exception) -> dict:
    """Handle errors from agent calls gracefully"""
    error_msg = str(error)
    print(f"❌ {agent_name} agent error: {error_msg}")
    
    # Return a user-friendly error response
    return {
        "status": "error",
        "agent": agent_name,
        "message": f"Sorry, the {agent_name} agent is currently unavailable. Please try again later.",
        "error": error_msg,
        "timestamp": asyncio.get_event_loop().time()
    }

router = APIRouter(prefix="/agents", tags=["AI Agents"])

@router.post("/oracle/chat")
async def oracle_chat(
    body: Dict[str, Any] = Body(...),
    current_phone_number: str = Depends(get_current_phone_number)
):
    """
    Oracle Agent - AI-powered personal finance assistant
    Handles tax questions, general financial advice, and conversational AI
    """
    try:
        question = body.get("question", "")
        if not question:
            raise HTTPException(status_code=400, detail="Question is required")
        
        # Convert phone number to UID format for agent compatibility
        uid = current_phone_number
        
        result = await process_oracle_query(uid, question)
        return {
            "status": "success",
            "agent": "oracle",
            "response": result,
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        return handle_agent_error("oracle", e)

@router.get("/guardian/alerts")
async def guardian_alerts(
    area: str = None,
    current_phone_number: str = Depends(get_current_phone_number)
):
    """
    Guardian Agent - Anomaly detection and security alerts
    Scans for unusual financial activities and potential fraud
    """
    try:
        uid = current_phone_number
        result = await run_guardian_analysis(uid, area)
        return {
            "status": "success",
            "agent": "guardian",
            "alerts": result,
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        return handle_agent_error("guardian", e)

@router.get("/catalyst/tips")
async def catalyst_tips(
    current_phone_number: str = Depends(get_current_phone_number)
):
    """
    Catalyst Agent - Growth recognition and investment tips
    Provides AI-powered growth insights and investment recommendations
    """
    try:
        uid = current_phone_number
        result = await run_catalyst_analysis(uid)
        return {
            "status": "success",
            "agent": "catalyst",
            "tips": result,
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        return handle_agent_error("catalyst", e)

@router.get("/strategist/portfolio")
async def strategist_portfolio(
    current_phone_number: str = Depends(get_current_phone_number)
):
    """
    Strategist Agent - Portfolio analysis and stock recommendations
    Provides portfolio optimization and stock investment strategies
    """
    try:
        uid = current_phone_number
        result = await run_strategist_analysis(uid)
        return {
            "status": "success",
            "agent": "strategist",
            "portfolio_analysis": result,
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        return handle_agent_error("strategist", e)

@router.get("/status")
async def agents_status():
    """
    Get the status of all AI agents
    """
    return {
        "status": "success",
        "agents": {
            "oracle": {
                "name": "Oracle",
                "description": "AI-powered personal finance assistant",
                "capabilities": ["Tax questions", "Financial advice", "Conversational AI"],
                "status": "active"
            },
            "guardian": {
                "name": "Guardian", 
                "description": "Anomaly detection and security alerts",
                "capabilities": ["Fraud detection", "Unusual activity alerts", "Security monitoring"],
                "status": "active"
            },
            "catalyst": {
                "name": "Catalyst",
                "description": "Growth recognition and investment tips",
                "capabilities": ["Growth insights", "Investment recommendations", "Market analysis"],
                "status": "active"
            },
            "strategist": {
                "name": "Strategist",
                "description": "Portfolio analysis and stock recommendations", 
                "capabilities": ["Portfolio optimization", "Stock strategies", "Risk assessment"],
                "status": "active"
            }
        }
    } 