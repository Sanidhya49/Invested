# Oracle Agent - AI-powered personal finance assistant

import asyncio
import json
import uuid
import httpx
from firebase_admin import firestore
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from shared_utils import (
        get_user_financial_data,
        get_cached_mcp_data,
        call_gemini_text,
        force_json_safe,
        MOCK_SERVER_BASE_URL
    )
except ImportError as e:
    print(f"Warning: Could not import shared_utils: {e}")
    # Fallback implementations
    MOCK_SERVER_BASE_URL = "http://localhost:8080"
    
    async def get_user_financial_data(uid: str, tool_name: str):
        return {"error": f"Mock data for {tool_name}"}
    
    async def get_cached_mcp_data(uid: str):
        return None
    
    def call_gemini_text(prompt: str, model_name="gemini-2.5-flash", tools=None, timeout=45):
        return f"Mock response to: {prompt[:100]}..."
    
    def force_json_safe(data):
        return {"mock_data": True, "timestamp": "2024-01-01T00:00:00"}

async def process_oracle_query(uid: str, question: str):
    """Process a query for the Oracle agent"""
    # QUICK FIX: Skip Firebase and MCP server, use mock data directly
    print(f"🚀 QUICK FIX: Oracle using mock data directly for user {uid}")
    
    # Load mock data directly without any server calls
    import os
    mock_data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fi-mcp-dev', 'test_data_dir', uid)
    
    # Initialize with default values
    net_worth = bank_tx = credit = epf = mf_tx = stock_tx = goals = {"error": "No data"}
    
    try:
        # Load all available mock data files
        data_files = {
            'net_worth': 'fetch_net_worth.json',
            'bank_tx': 'fetch_bank_transactions.json', 
            'credit': 'fetch_credit_report.json',
            'epf': 'fetch_epf_details.json',
            'mf_tx': 'fetch_mf_transactions.json',
            'stock_tx': 'fetch_stock_transactions.json',
            'goals': 'goals.json'
        }
        
        for data_type, filename in data_files.items():
            file_path = os.path.join(mock_data_path, filename)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    if data_type == 'net_worth':
                        net_worth = json.load(f)
                    elif data_type == 'bank_tx':
                        bank_tx = json.load(f)
                    elif data_type == 'credit':
                        credit = json.load(f)
                    elif data_type == 'epf':
                        epf = json.load(f)
                    elif data_type == 'mf_tx':
                        mf_tx = json.load(f)
                    elif data_type == 'stock_tx':
                        stock_tx = json.load(f)
                    elif data_type == 'goals':
                        goals = json.load(f)
                print(f"✅ Loaded mock {data_type}")
            else:
                print(f"⚠️ Mock file not found: {filename}")
                
    except Exception as e:
        print(f"❌ Error loading mock data: {e}")
        # Continue with error data
    
    print(f"🚀 Oracle data loaded successfully!")
    
    data = {
        "net_worth": net_worth if net_worth and not net_worth.get('error') else "unavailable",
        "bank_transactions": bank_tx if bank_tx and not bank_tx.get('error') else "unavailable",
        "credit_report": credit if credit and not credit.get('error') else "unavailable",
        "epf_details": epf if epf and not epf.get('error') else "unavailable",
        "mf_transactions": mf_tx if mf_tx and not mf_tx.get('error') else "unavailable",
        "stock_transactions": stock_tx if stock_tx and not stock_tx.get('error') else "unavailable",
        "goals": goals if goals and not goals.get('error') else "unavailable"
    }
    
    prompt = (
        "You are Oracle, an AI-powered personal finance assistant. "
        "You have access to the user's complete financial data, including net worth, bank transactions, credit report, EPF, mutual fund transactions, stock transactions, and financial goals. "
        "Answer the user's question in a friendly, conversational, and helpful way, just like a smart financial friend. "
        "You can: look into the future, check progress, analyze investments, and help with big decisions. "
        "If any data is 'unavailable', do your best with what you have. "
        "Be specific, use numbers and trends from the data, and explain your reasoning. "
        "IMPORTANT: When analyzing bank transactions, look for recurring payments and subscriptions. "
        "Common subscription patterns include: monthly/quarterly charges for streaming services (Netflix, Spotify, etc.), "
        "gym memberships, software subscriptions, and other recurring services. "
        "If you find subscriptions, list them with amounts and frequencies. "
        "When analyzing goals, provide insights on progress, timelines, and recommendations. "
        "User's question: '" + question + "'\n"
        f"Data:\n{json.dumps(data)}"
    )
    
    try:
        answer = await asyncio.to_thread(call_gemini_text, prompt)
    except Exception as e:
        print(f"❌ Error calling Gemini: {e}")
        answer = f"I'm sorry, but I'm currently unable to process your request due to a technical issue. Please try again later. Your question was: {question}"
    
    return {"question": question, "answer": answer} 