# Guardian Agent - AI financial safety agent

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
        print(f"🔍 force_json_safe called with data: {type(data)}")
        if data is None:
            return {"mock_data": True, "timestamp": "2024-01-01T00:00:00"}
        try:
            return {"mock_data": True, "timestamp": "2024-01-01T00:00:00", "data": data}
        except Exception as e:
            print(f"❌ Error in force_json_safe: {e}")
            return {"mock_data": True, "timestamp": "2024-01-01T00:00:00"}

async def run_guardian_analysis(uid: str, area: str = None):
    """Run Guardian analysis for financial safety alerts"""
    try:
        db = firestore.client()
    except Exception as e:
        print(f"Warning: Could not initialize Firestore: {e}")
        # Return a mock response if Firebase is not available
        fallback = {
            "alerts": [
                {"type": "System Alert", "description": "Financial data access is temporarily unavailable.", "severity": "info"},
                {"type": "Security Reminder", "description": "Please ensure your account security settings are up to date.", "severity": "info"}
            ]
        }
        return {"alerts": json.dumps(fallback)}
    
    # Initialize variables
    bank_tx = credit = mf_tx = None
    
    # Try cache first
    try:
        mcp_cache = await get_cached_mcp_data(uid)
        if mcp_cache and isinstance(mcp_cache, dict):
            bank_tx = mcp_cache.get("bank_transactions")
            credit = mcp_cache.get("credit_report")
            mf_tx = mcp_cache.get("mf_transactions")
        else:
            try:
                bank_tx, credit, mf_tx = await asyncio.gather(
                    get_user_financial_data(uid, tool_name="fetch_bank_transactions"),
                    get_user_financial_data(uid, tool_name="fetch_credit_report"),
                    get_user_financial_data(uid, tool_name="fetch_mf_transactions")
                )
                # Ensure all results are dictionaries
                if bank_tx is None:
                    bank_tx = {"error": "Bank transactions fetch failed"}
                if credit is None:
                    credit = {"error": "Credit report fetch failed"}
                if mf_tx is None:
                    mf_tx = {"error": "Mutual fund transactions fetch failed"}
            except Exception as e:
                print(f"❌ Error in asyncio.gather: {e}")
                bank_tx = {"error": "Bank transactions fetch failed"}
                credit = {"error": "Credit report fetch failed"}
                mf_tx = {"error": "Mutual fund transactions fetch failed"}
            # Update cache
            try:
                mcp_data = mcp_cache if isinstance(mcp_cache, dict) else {}
                mcp_data.update({
                    "bank_transactions": bank_tx,
                    "credit_report": credit,
                    "mf_transactions": mf_tx,
                    "mcp_cache_timestamp": datetime.utcnow().isoformat()
                })
                safe_mcp_data = force_json_safe(mcp_data)
                
                # Try to save to Firestore with error handling
                await asyncio.to_thread(db.collection("users").document(uid).set, {"mcp_data_cache": safe_mcp_data}, merge=True)
                print("✅ SUCCESS: Guardian MCP data cached in Firestore")
            except Exception as e:
                print(f"❌ WARNING: Failed to cache Guardian MCP data in Firestore: {e}")
                # Continue without caching - the app will still work
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        bank_tx = credit = mf_tx = {"error": "Data fetch failed"}
    
    # Ensure variables are not None
    if bank_tx is None:
        bank_tx = {"error": "Data fetch failed"}
    if credit is None:
        credit = {"error": "Data fetch failed"}
    if mf_tx is None:
        mf_tx = {"error": "Data fetch failed"}
    
    # If data fetch failed, use mock data for testing
    if (bank_tx and bank_tx.get('error')) or (credit and credit.get('error')) or (mf_tx and mf_tx.get('error')):
        print("🔄 Using mock data for Guardian analysis")
        # Load mock data for user 2222222222
        import os
        mock_data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fi-mcp-dev', 'test_data_dir', uid)
        
        try:
            # Load bank transactions
            bank_file = os.path.join(mock_data_path, 'fetch_bank_transactions.json')
            if os.path.exists(bank_file):
                with open(bank_file, 'r') as f:
                    bank_tx = json.load(f)
                print("✅ Loaded mock bank transactions")
            
            # Load credit report
            credit_file = os.path.join(mock_data_path, 'fetch_credit_report.json')
            if os.path.exists(credit_file):
                with open(credit_file, 'r') as f:
                    credit = json.load(f)
                print("✅ Loaded mock credit report")
            
            # Load mutual fund transactions
            mf_file = os.path.join(mock_data_path, 'fetch_mf_transactions.json')
            if os.path.exists(mf_file):
                with open(mf_file, 'r') as f:
                    mf_tx = json.load(f)
                print("✅ Loaded mock mutual fund transactions")
                
        except Exception as e:
            print(f"❌ Error loading mock data: {e}")
            # Fallback to error state
            bank_tx = credit = mf_tx = {"error": "Mock data load failed"}
    
    tx_data = bank_tx if bank_tx and not bank_tx.get('error') else "unavailable"
    cr_data = credit if credit and not credit.get('error') else "unavailable"
    mf_data = mf_tx if mf_tx and not mf_tx.get('error') else "unavailable"
    data = {"bank_transactions": tx_data, "credit_report": cr_data, "mf_transactions": mf_data}
    
    # Customize prompt based on selected area
    area_focus = ""
    if area:
        area_focus = f"Focus specifically on {area.replace('_', ' ')} analysis. "
    
    prompt = (
        f"You are Guardian, an AI financial safety agent. "
        f"{area_focus}"
        "You receive the user's bank transactions, credit report, and mutual fund transactions as JSON. "
        "If any data is 'unavailable', still provide at least two actionable, proactive alerts for the user. "
        "If the user's finances are perfect, still suggest at least two ways to improve security, growth, or protection. "
        "Respond ONLY in a valid JSON object: "
        '{"alerts": [{"type":"...", "description":"...", "severity":"..."}]}'"\n"
        f"Data:\n{json.dumps(data)}"
    )
    
    try:
        answer = await asyncio.to_thread(call_gemini_text, prompt)
    except Exception as e:
        print(f"❌ Error calling Gemini: {e}")
        # Return fallback alerts if Gemini fails
        fallback = {
            "alerts": [
                {"type": "Security Reminder", "description": "Review your account security settings regularly.", "severity": "info"},
                {"type": "Growth Tip", "description": "Consider setting up a recurring investment to maximize compounding.", "severity": "info"}
            ]
        }
        return {"alerts": json.dumps(fallback)}
    
    # Try to parse and inject fallback alerts if empty
    try:
        parsed = json.loads(answer.replace("```json", '').replace("```", ''))
        alerts = parsed.get('alerts', [])
        if not alerts:
            alerts = [
                {"type": "Security Reminder", "description": "Review your account security settings regularly.", "severity": "info"},
                {"type": "Growth Tip", "description": "Consider setting up a recurring investment to maximize compounding.", "severity": "info"}
            ]
        parsed['alerts'] = alerts
        # Cache alerts in Firestore
        try:
            await asyncio.to_thread(db.collection("users").document(uid).set, {"guardian_alerts_cache": alerts}, merge=True)
        except Exception as e:
            print(f"❌ WARNING: Failed to cache Guardian alerts in Firestore: {e}")
        return {"alerts": json.dumps(parsed)}
    except Exception:
        # Fallback if parsing fails, try cache
        try:
            user_doc = await asyncio.to_thread(db.collection("users").document(uid).get)
            cache = user_doc.to_dict().get("guardian_alerts_cache") if user_doc.exists else None
            if cache:
                fallback = {"alerts": cache}
                return {"alerts": json.dumps(fallback)}
        except Exception as e:
            print(f"❌ WARNING: Failed to read Guardian alerts cache: {e}")
        fallback = {
            "alerts": [
                {"type": "Security Reminder", "description": "Review your account security settings regularly.", "severity": "info"},
                {"type": "Growth Tip", "description": "Consider setting up a recurring investment to maximize compounding.", "severity": "info"}
            ]
        }
        return {"alerts": json.dumps(fallback)} 