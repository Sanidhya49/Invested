# Catalyst Agent - AI financial growth agent

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
        force_json_safe
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

async def run_catalyst_analysis(uid: str):
    """Run Catalyst analysis for financial growth opportunities"""
    try:
        db = firestore.client()
    except Exception as e:
        print(f"Warning: Could not initialize Firestore: {e}")
        # Return a mock response if Firebase is not available
        fallback = {
            "opportunities": [
                {"title": "System Maintenance", "description": "Financial data access is temporarily unavailable.", "category": "System"},
                {"title": "General Investment Tip", "description": "Consider diversifying your portfolio across different asset classes.", "category": "Growth"}
            ]
        }
        return {"opportunities": json.dumps(fallback)}
    
    # Initialize variables
    net_worth = epf = mf_tx = None
    
    # Try cache first
    try:
        mcp_cache = await get_cached_mcp_data(uid)
        if mcp_cache and isinstance(mcp_cache, dict):
            net_worth = mcp_cache.get("net_worth")
            epf = mcp_cache.get("epf_details")
            mf_tx = mcp_cache.get("mf_transactions")
        else:
            try:
                net_worth, epf, mf_tx = await asyncio.gather(
                    get_user_financial_data(uid, tool_name="fetch_net_worth"),
                    get_user_financial_data(uid, tool_name="fetch_epf_details"),
                    get_user_financial_data(uid, tool_name="fetch_mf_transactions")
                )
                # Ensure all results are dictionaries
                if net_worth is None:
                    net_worth = {"error": "Net worth fetch failed"}
                if epf is None:
                    epf = {"error": "EPF details fetch failed"}
                if mf_tx is None:
                    mf_tx = {"error": "Mutual fund transactions fetch failed"}
            except Exception as e:
                print(f"❌ Error in asyncio.gather: {e}")
                net_worth = {"error": "Net worth fetch failed"}
                epf = {"error": "EPF details fetch failed"}
                mf_tx = {"error": "Mutual fund transactions fetch failed"}
            # Update cache
            try:
                mcp_data = mcp_cache if isinstance(mcp_cache, dict) else {}
                mcp_data.update({
                    "net_worth": net_worth,
                    "epf_details": epf,
                    "mf_transactions": mf_tx,
                    "mcp_cache_timestamp": datetime.utcnow().isoformat()
                })
                safe_mcp_data = force_json_safe(mcp_data)
                
                # Try to save to Firestore with error handling
                await asyncio.to_thread(db.collection("users").document(uid).set, {"mcp_data_cache": safe_mcp_data}, merge=True)
                print("✅ SUCCESS: Catalyst MCP data cached in Firestore")
            except Exception as e:
                print(f"❌ WARNING: Failed to cache Catalyst MCP data in Firestore: {e}")
                # Continue without caching - the app will still work
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        net_worth = epf = mf_tx = {"error": "Data fetch failed"}
    
    # Ensure variables are not None
    if net_worth is None:
        net_worth = {"error": "Data fetch failed"}
    if epf is None:
        epf = {"error": "Data fetch failed"}
    if mf_tx is None:
        mf_tx = {"error": "Data fetch failed"}
    
    # If data fetch failed, use mock data for testing
    if (net_worth and net_worth.get('error')) or (epf and epf.get('error')) or (mf_tx and mf_tx.get('error')):
        print("🔄 Using mock data for Catalyst analysis")
        # Load mock data for user 2222222222
        import os
        mock_data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fi-mcp-dev', 'test_data_dir', uid)
        
        try:
            # Load net worth
            net_worth_file = os.path.join(mock_data_path, 'fetch_net_worth.json')
            if os.path.exists(net_worth_file):
                with open(net_worth_file, 'r') as f:
                    net_worth = json.load(f)
                print("✅ Loaded mock net worth data")
            
            # Load EPF details
            epf_file = os.path.join(mock_data_path, 'fetch_epf_details.json')
            if os.path.exists(epf_file):
                with open(epf_file, 'r') as f:
                    epf = json.load(f)
                print("✅ Loaded mock EPF details")
            
            # Load mutual fund transactions
            mf_file = os.path.join(mock_data_path, 'fetch_mf_transactions.json')
            if os.path.exists(mf_file):
                with open(mf_file, 'r') as f:
                    mf_tx = json.load(f)
                print("✅ Loaded mock mutual fund transactions")
                
        except Exception as e:
            print(f"❌ Error loading mock data: {e}")
            # Fallback to error state
            net_worth = epf = mf_tx = {"error": "Mock data load failed"}
    
    nw_data = net_worth if net_worth and not net_worth.get('error') else "unavailable"
    epf_data = epf if epf and not epf.get('error') else "unavailable"
    mf_data = mf_tx if mf_tx and not mf_tx.get('error') else "unavailable"
    data = {"net_worth_summary": nw_data, "epf_details": epf_data, "mf_transactions": mf_data}
    
    prompt = (
        "You are Catalyst, an AI financial growth agent. "
        "You receive the user's net worth summary, EPF details, and mutual fund transactions as JSON. "
        "Analyze the data and provide specific investment opportunities with ROI comparisons. "
        "If any data is 'unavailable', still provide at least two actionable, proactive opportunities for the user. "
        "If the user's finances are perfect, still suggest at least two ways to improve growth, diversification, or protection. "
        "Respond ONLY in a valid JSON object: "
        '{"opportunities": [{"title":"...", "description":"...", "category":"...", "roi_comparison":{"current":12.5, "suggested":18.2}, "action_items":["...", "..."]}]}'"\n"
        f"Data:\n{json.dumps(data)}"
    )
    
    try:
        answer = await asyncio.to_thread(call_gemini_text, prompt)
    except Exception as e:
        print(f"❌ Error calling Gemini: {e}")
        # Return fallback opportunities if Gemini fails
        fallback = {
            "opportunities": [
                {"title": "Diversify Investments", "description": "Explore new asset classes or sectors to reduce risk and enhance returns.", "category": "Growth"},
                {"title": "Increase Emergency Fund", "description": "Boost your emergency fund to cover at least 6 months of expenses.", "category": "Protection"}
            ]
        }
        return {"opportunities": json.dumps(fallback)}
    
    try:
        parsed = json.loads(answer.replace("```json", '').replace("```", ''))
        opportunities = parsed.get('opportunities', [])
        if not opportunities:
            opportunities = [
                {"title": "Diversify Investments", "description": "Explore new asset classes or sectors to reduce risk and enhance returns.", "category": "Growth"},
                {"title": "Increase Emergency Fund", "description": "Boost your emergency fund to cover at least 6 months of expenses.", "category": "Protection"}
            ]
        parsed['opportunities'] = opportunities
        # Cache opportunities in Firestore
        try:
            await asyncio.to_thread(db.collection("users").document(uid).set, {"catalyst_opportunities_cache": opportunities}, merge=True)
        except Exception as e:
            print(f"❌ WARNING: Failed to cache Catalyst opportunities in Firestore: {e}")
        return {"opportunities": json.dumps(parsed)}
    except Exception:
        try:
            user_doc = await asyncio.to_thread(db.collection("users").document(uid).get)
            cache = user_doc.to_dict().get("catalyst_opportunities_cache") if user_doc.exists else None
            if cache:
                fallback = {"opportunities": cache}
                return {"opportunities": json.dumps(fallback)}
        except Exception as e:
            print(f"❌ WARNING: Failed to read Catalyst opportunities cache: {e}")
        fallback = {
            "opportunities": [
                {"title": "Diversify Investments", "description": "Explore new asset classes or sectors to reduce risk and enhance returns.", "category": "Growth"},
                {"title": "Increase Emergency Fund", "description": "Boost your emergency fund to cover at least 6 months of expenses.", "category": "Protection"}
            ]
        }
        return {"opportunities": json.dumps(fallback)} 