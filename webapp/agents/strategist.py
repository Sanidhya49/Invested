# Strategist Agent - Investment strategy expert

import asyncio
import json
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
        market_data_tool
    )
except ImportError as e:
    print(f"Warning: Could not import shared_utils: {e}")
    # Fallback implementations
    async def get_user_financial_data(uid: str, tool_name: str):
        return {"error": f"Mock data for {tool_name}"}
    
    async def get_cached_mcp_data(uid: str):
        return {"error": "No cache available"}
    
    def call_gemini_text(prompt: str, model_name="gemini-2.5-flash", tools=None, timeout=45):
        return f"Mock response to: {prompt[:100]}..."
    
    def force_json_safe(data):
        return {"mock_data": True, "timestamp": "2024-01-01T00:00:00"}
    
    # Mock market data tool
    market_data_tool = None

async def run_strategist_analysis(uid: str):
    """Run Strategist analysis for investment recommendations"""
    try:
        db = firestore.client()
    except Exception as e:
        print(f"Warning: Could not initialize Firestore: {e}")
        # Return a mock response if Firebase is not available
        fallback = {
            "summary": "Financial data access is temporarily unavailable.",
            "recommendations": [
                {"symbol": "SYSTEM", "advice": "Wait", "reasoning": "Please try again when the system is fully operational."},
                {"symbol": "GENERAL", "advice": "Diversify", "reasoning": "Consider diversifying your portfolio when data access is restored."}
            ]
        }
        return {"strategy": json.dumps(fallback)}
    
    # Initialize variables
    stock_tx = mf_tx = None
    
    # Try cache first
    try:
        mcp_cache = await get_cached_mcp_data(uid)
        if mcp_cache and isinstance(mcp_cache, dict):
            stock_tx = mcp_cache.get("stock_transactions")
            mf_tx = mcp_cache.get("mf_transactions")
        else:
            try:
                stock_tx, mf_tx = await asyncio.gather(
                    get_user_financial_data(uid, tool_name="fetch_stock_transactions"),
                    get_user_financial_data(uid, tool_name="fetch_mf_transactions")
                )
                # Ensure all results are dictionaries
                if stock_tx is None:
                    stock_tx = {"error": "Stock transactions fetch failed"}
                if mf_tx is None:
                    mf_tx = {"error": "Mutual fund transactions fetch failed"}
            except Exception as e:
                print(f"❌ Error in asyncio.gather: {e}")
                stock_tx = {"error": "Stock transactions fetch failed"}
                mf_tx = {"error": "Mutual fund transactions fetch failed"}
            # Update cache
            try:
                mcp_data = mcp_cache if isinstance(mcp_cache, dict) else {}
                mcp_data.update({
                    "stock_transactions": stock_tx,
                    "mf_transactions": mf_tx,
                    "mcp_cache_timestamp": datetime.utcnow().isoformat()
                })
                safe_mcp_data = force_json_safe(mcp_data)
                
                # Try to save to Firestore with error handling
                await asyncio.to_thread(db.collection("users").document(uid).set, {"mcp_data_cache": safe_mcp_data}, merge=True)
                print("✅ SUCCESS: Strategist MCP data cached in Firestore")
            except Exception as e:
                print(f"❌ WARNING: Failed to cache Strategist MCP data in Firestore: {e}")
                # Continue without caching - the app will still work
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        stock_tx = mf_tx = {"error": "Data fetch failed"}
    
    # Ensure variables are not None
    if stock_tx is None:
        stock_tx = {"error": "Data fetch failed"}
    if mf_tx is None:
        mf_tx = {"error": "Data fetch failed"}
    
    # If data fetch failed, use mock data for testing
    if (stock_tx and stock_tx.get('error')) or (mf_tx and mf_tx.get('error')):
        print("🔄 Using mock data for Strategist analysis")
        # Load mock data for user 2222222222
        import os
        mock_data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fi-mcp-dev', 'test_data_dir', uid)
        
        try:
            # Load stock transactions
            stock_file = os.path.join(mock_data_path, 'fetch_stock_transactions.json')
            if os.path.exists(stock_file):
                with open(stock_file, 'r') as f:
                    stock_tx = json.load(f)
                print("✅ Loaded mock stock transactions")
            
            # Load mutual fund transactions
            mf_file = os.path.join(mock_data_path, 'fetch_mf_transactions.json')
            if os.path.exists(mf_file):
                with open(mf_file, 'r') as f:
                    mf_tx = json.load(f)
                print("✅ Loaded mock mutual fund transactions")
                
        except Exception as e:
            print(f"❌ Error loading mock data: {e}")
            # Fallback to error state
            stock_tx = mf_tx = {"error": "Mock data load failed"}
    
    stock_data = stock_tx if stock_tx and not stock_tx.get('error') else "unavailable"
    mf_data = mf_tx if mf_tx and not mf_tx.get('error') else "unavailable"
    data = {"stock_transactions": stock_data, "mf_transactions": mf_data}
    
    prompt = (
        "You are an expert Investment Strategist for the Indian market. "
        "You receive the user's stock and mutual fund transactions as JSON. "
        "Analyze the portfolio and provide specific buy/sell/hold recommendations with price targets and risk assessment. "
        "If any data is 'unavailable', still provide at least two actionable, proactive recommendations for the user. "
        "If the user's portfolio is perfect, still suggest at least two ways to improve diversification, reduce risk, or optimize returns. "
        "Respond ONLY in a valid JSON object: "
        '{"summary":"...", "recommendations":[{"symbol":"...", "advice":"buy/sell/hold", "reasoning":"...", "current_price":1500, "price_analysis":{"target":1800, "stop_loss":1400, "potential_return":20}, "risk_assessment":{"level":"medium", "level_percentage":60, "description":"..."}, "action_items":["...", "..."]}]}'"\n"
        f"User's Portfolio Data:\n{json.dumps(data)}"
    )
    
    try:
        answer = await asyncio.to_thread(call_gemini_text, prompt, tools=[market_data_tool])
    except Exception as e:
        print(f"❌ Error calling Gemini: {e}")
        # Return fallback strategy if Gemini fails
        fallback = {
            "summary": "Could not analyze portfolio, but here are some general recommendations.",
            "recommendations": [
                {"symbol": "NIFTY 50", "advice": "Diversify", "reasoning": "Consider adding more sectors or asset classes to your portfolio for better risk management."},
                {"symbol": "CASH", "advice": "Increase Equity Allocation", "reasoning": "If you have excess cash, consider allocating more to equities for long-term growth."}
            ]
        }
        return {"strategy": json.dumps(fallback)}
    
    try:
        parsed = json.loads(answer.replace("```json", '').replace("```", ''))
        recs = parsed.get('recommendations', [])
        if not recs:
            recs = [
                {"symbol": "NIFTY 50", "advice": "Diversify", "reasoning": "Consider adding more sectors or asset classes to your portfolio for better risk management."},
                {"symbol": "CASH", "advice": "Increase Equity Allocation", "reasoning": "If you have excess cash, consider allocating more to equities for long-term growth."}
            ]
        parsed['recommendations'] = recs
        return {"strategy": json.dumps(parsed)}
    except Exception:
        fallback = {
            "summary": "Could not analyze portfolio, but here are some general recommendations.",
            "recommendations": [
                {"symbol": "NIFTY 50", "advice": "Diversify", "reasoning": "Consider adding more sectors or asset classes to your portfolio for better risk management."},
                {"symbol": "CASH", "advice": "Increase Equity Allocation", "reasoning": "If you have excess cash, consider allocating more to equities for long-term growth."}
            ]
        }
        return {"strategy": json.dumps(fallback)} 