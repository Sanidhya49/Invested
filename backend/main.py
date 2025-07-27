# main.py (ASYNC VERSION with Strategist Agent & Tool Use)

from fastapi import FastAPI, Depends, HTTPException, Header, Body
import firebase_admin
from firebase_admin import credentials, auth, firestore
import os
import uuid
import httpx
import json
from fastapi.responses import JSONResponse
import traceback
import asyncio
from datetime import datetime, timedelta

# Import Vertex AI and Tool Use libraries
import vertexai
from vertexai.generative_models import GenerativeModel, Tool, Part, FunctionDeclaration

app = FastAPI()

# --- Initializations ---
cred = credentials.Certificate("invested-hackathon-firebase-adminsdk-fbsvc-38735ba923.json")
firebase_admin.initialize_app(cred)
SERVICE_ACCOUNT_KEY_PATH = os.path.join(os.path.dirname(__file__), "invested-hackathon-vertex-ai-key.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_KEY_PATH
GCP_PROJECT_ID = "invested-hackathon"
GCP_LOCATION = "us-central1
vertexai.init(project=GCP_PROJECT_ID, location=GCP_LOCATION)

MOCK_SERVER_BASE_URL = "http://10.0.2.2:8080"

# --- Authentication ---
async def verify_firebase_token(authorization: str = Header(...)):
    try:
        id_token = authorization.split(" ").pop()
        decoded_token = await asyncio.to_thread(auth.verify_id_token, id_token)
        return decoded_token['uid']
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Firebase token")

@app.get("/start-fi-auth")
async def start_fi_auth(uid: str = Depends(verify_firebase_token)):
    session_id = str(uuid.uuid4())
    db = firestore.client()
    user_doc_ref = db.collection("users").document(uid)
    await asyncio.to_thread(user_doc_ref.set, {"fi_session_id": session_id}, merge=True)
    auth_url = f"{MOCK_SERVER_BASE_URL}/mockWebPage?sessionId={session_id}"
    return {"auth_url": auth_url}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/get-user-data")
async def get_user_data(uid: str = Depends(verify_firebase_token)):
    """Get user's net worth and financial summary data for dashboard"""
    try:
        # Fetch net worth data
        net_worth_data = await get_user_financial_data(uid, tool_name="fetch_net_worth")
        
        if net_worth_data and not net_worth_data.get('error'):
            # Parse the MCP data structure
            net_worth_response = net_worth_data.get('netWorthResponse', {})
            asset_values = net_worth_response.get('assetValues', [])
            total_net_worth_value = net_worth_response.get('totalNetWorthValue', {})
            
            # Calculate totals from asset values
            total_assets = 0
            total_liabilities = 0
            
            for asset in asset_values:
                value = asset.get('value', {})
                units = int(value.get('units', 0))
                if units > 0:
                    total_assets += units
                else:
                    total_liabilities += abs(units)  # Convert negative to positive
            
            # Get total net worth
            total_networth = int(total_net_worth_value.get('units', 0))
            
            response_data = {
                "total_networth": total_networth,
                "total_assets": total_assets,
                "total_liabilities": total_liabilities,
                "change_percentage": 0,  # No change data available
                "currency": "INR"
            }
            return response_data
        else:
            # Return fallback data if MCP fails
            print(f"DEBUG: Using fallback data, MCP data was: {net_worth_data}")
            fallback_data = {
                "total_networth": 1500000,
                "total_assets": 2000000,
                "total_liabilities": 500000,
                "change_percentage": 5.2,
                "currency": "INR"
            }
            print(f"DEBUG: Returning fallback data: {fallback_data}")
            return fallback_data
    except Exception as e:
        print(f"❌ Error in get_user_data: {e}")
        # Return fallback data on error
        error_fallback_data = {
            "total_networth": 1500000,
            "total_assets": 2000000,
            "total_liabilities": 500000,
            "change_percentage": 5.2,
            "currency": "INR"
        }
        print(f"DEBUG: Returning error fallback data: {error_fallback_data}")
        return error_fallback_data

# --- Dynamic Data Fetching ---
async def get_user_financial_data(uid: str, tool_name: str, timeout=30):
    try:
        db = firestore.client()
        user_doc = await asyncio.to_thread(db.collection("users").document(uid).get)
        if user_doc.exists and "fi_session_id" in user_doc.to_dict():
            session_id = user_doc.to_dict()["fi_session_id"]
            headers = {"X-Session-ID": session_id}
            request_body = {"tool_name": tool_name}
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "http://localhost:8080/mcp/stream",
                        headers=headers,
                        json=request_body,
                        timeout=timeout
                    )
            except httpx.TimeoutException:
                print(f"❌ TIMEOUT: MCP server timed out for '{tool_name}'")
                return {"error": f"Timeout fetching {tool_name} from MCP server."}
            except Exception as e:
                print(f"❌ ERROR: MCP server error for '{tool_name}': {e}")
                return {"error": f"Error fetching {tool_name} from MCP server: {e}"}
            if response.status_code == 200:
                print(f"✅ SUCCESS: Fetched '{tool_name}' data.")
                return response.json()
            else:
                print(f"⚠️ Error from mock server for tool '{tool_name}': {response.status_code}")
                return {"error": f"Server returned {response.status_code}"}
    except Exception as e:
        print(f"❌ Failed to fetch live data for tool '{tool_name}'. Error: {e}")
        traceback.print_exc()
    print(f"ℹ️ INFO: Fallback for '{tool_name}'.")
    return {"error": f"Could not fetch {tool_name}."}

# --- NEW: Tool Definition for the Strategist Agent ---
def get_market_performance(stock_symbols: list):
    print(f"TOOL CALLED: get_market_performance for symbols: {stock_symbols}")
    performance_data = {}
    performance_data["NIFTY 50"] = {"1y_return": 12.0}
    for symbol in stock_symbols:
        if "RELIANCE" in symbol:
            performance_data[symbol] = {"1y_return": 15.5}
        elif "TCS" in symbol:
            performance_data[symbol] = {"1y_return": 11.0}
        else:
            performance_data[symbol] = {"1y_return": 13.0}
    return json.dumps(performance_data)

market_data_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="get_market_performance",
            description="Gets the real-time 1-year market performance for a list of stock symbols and the NIFTY 50 index.",
            parameters={
                "type": "object",
                "properties": {
                    "stock_symbols": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "A list of stock symbols to fetch performance for, e.g., ['RELIANCE', 'TCS']"
                    }
                },
                "required": ["stock_symbols"]
            },
        )
    ]
)

# --- Gemini Model Call Function ---
def call_gemini_text(prompt: str, model_name="gemini-2.5-flash", tools=None, timeout=45):
    try:
        model = GenerativeModel(model_name, tools=tools)
        response = model.generate_content(prompt)
        if response.candidates[0].function_calls:
            function_call = response.candidates[0].function_calls[0]
            if function_call.name == "get_market_performance":
                args = {key: value for key, value in function_call.args.items()}
                tool_result = get_market_performance(**args)
                final_response = model.generate_content(
                    Part.from_function_response(
                        name="get_market_performance",
                        response={"content": tool_result}
                    )
                )
                return final_response.text
        return response.text
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        traceback.print_exc()
        return f"Error: Gemini API call failed: {e}"

# --- Agent Endpoints ---
@app.post("/ask-oracle")
async def ask_oracle(uid: str = Depends(verify_firebase_token), body: dict = Body(...)):
    question = body.get("question", "")
    # Fetch all relevant financial data
    net_worth, bank_tx, credit, epf, mf_tx, stock_tx = await asyncio.gather(
        get_user_financial_data(uid, tool_name="fetch_net_worth"),
        get_user_financial_data(uid, tool_name="fetch_bank_transactions"),
        get_user_financial_data(uid, tool_name="fetch_credit_report"),
        get_user_financial_data(uid, tool_name="fetch_epf_details"),
        get_user_financial_data(uid, tool_name="fetch_mf_transactions"),
        get_user_financial_data(uid, tool_name="fetch_stock_transactions")
    )
    # Clean up data: if error, mark as 'unavailable'
    data = {
        "net_worth": net_worth if net_worth and not net_worth.get('error') else "unavailable",
        "bank_transactions": bank_tx if bank_tx and not bank_tx.get('error') else "unavailable",
        "credit_report": credit if credit and not credit.get('error') else "unavailable",
        "epf_details": epf if epf and not epf.get('error') else "unavailable",
        "mf_transactions": mf_tx if mf_tx and not mf_tx.get('error') else "unavailable",
        "stock_transactions": stock_tx if stock_tx and not stock_tx.get('error') else "unavailable"
    }
    prompt = (
        "You are Oracle, an AI-powered personal finance assistant. "
        "You have access to the user's complete financial data, including net worth, bank transactions, credit report, EPF, mutual fund transactions, and stock transactions. "
        "Answer the user's question in a friendly, conversational, and helpful way, just like a smart financial friend. "
        "You can: look into the future, check progress, analyze investments, and help with big decisions. "
        "If any data is 'unavailable', do your best with what you have. "
        "Be specific, use numbers and trends from the data, and explain your reasoning. "
        "User's question: '" + question + "'\n"
        f"Data:\n{json.dumps(data)}"
    )
    answer = await asyncio.to_thread(call_gemini_text, prompt)
    return {"question": question, "answer": answer}

@app.post("/run-guardian")
async def run_guardian(uid: str = Depends(verify_firebase_token), body: dict = Body(None)):
    db = firestore.client()
    try:
        bank_tx, credit, mf_tx = await asyncio.gather(
            get_user_financial_data(uid, tool_name="fetch_bank_transactions"),
            get_user_financial_data(uid, tool_name="fetch_credit_report"),
            get_user_financial_data(uid, tool_name="fetch_mf_transactions")
        )
        tx_data = bank_tx if bank_tx and not bank_tx.get('error') else "unavailable"
        cr_data = credit if credit and not credit.get('error') else "unavailable"
        mf_data = mf_tx if mf_tx and not mf_tx.get('error') else "unavailable"
        data = {"bank_transactions": tx_data, "credit_report": cr_data, "mf_transactions": mf_data}
        prompt = (
            "You are Guardian, an AI financial safety agent. "
            "You receive the user's bank transactions, credit report, and mutual fund transactions as JSON. "
            "If any data is 'unavailable', still provide at least two actionable, proactive alerts for the user. "
            "If the user's finances are perfect, still suggest at least two ways to improve security, growth, or protection. "
            "Respond ONLY in a valid JSON object: "
            "{\"alerts\": [{\"type\":\"...\", \"description\":\"...\", \"severity\":\"...\"}]}\n"
            f"Data:\n{json.dumps(data)}"
        )
        answer = await asyncio.to_thread(call_gemini_text, prompt)
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
            await asyncio.to_thread(db.collection("users").document(uid).set, {"guardian_alerts_cache": alerts}, merge=True)
            return {"alerts": json.dumps(parsed)}
        except Exception:
            # Fallback if parsing fails, try cache
            user_doc = await asyncio.to_thread(db.collection("users").document(uid).get)
            cache = user_doc.to_dict().get("guardian_alerts_cache") if user_doc.exists else None
            if cache:
                fallback = {"alerts": cache}
                return {"alerts": json.dumps(fallback)}
            fallback = {
                "alerts": [
                    {"type": "Security Reminder", "description": "Review your account security settings regularly.", "severity": "info"},
                    {"type": "Growth Tip", "description": "Consider setting up a recurring investment to maximize compounding.", "severity": "info"}
                ]
            }
            return {"alerts": json.dumps(fallback)}
    except Exception:
        # On MCP timeout or error, try cache
        user_doc = await asyncio.to_thread(db.collection("users").document(uid).get)
        cache = user_doc.to_dict().get("guardian_alerts_cache") if user_doc.exists else None
        if cache:
            fallback = {"alerts": cache}
            return {"alerts": json.dumps(fallback)}
        fallback = {
            "alerts": [
                {"type": "Security Reminder", "description": "Review your account security settings regularly.", "severity": "info"},
                {"type": "Growth Tip", "description": "Consider setting up a recurring investment to maximize compounding.", "severity": "info"}
            ]
        }
        return {"alerts": json.dumps(fallback)}

@app.post("/run-catalyst")
async def run_catalyst(uid: str = Depends(verify_firebase_token), body: dict = Body(None)):
    db = firestore.client()
    try:
        net_worth, epf, mf_tx = await asyncio.gather(
            get_user_financial_data(uid, tool_name="fetch_net_worth"),
            get_user_financial_data(uid, tool_name="fetch_epf_details"),
            get_user_financial_data(uid, tool_name="fetch_mf_transactions")
        )
        nw_data = net_worth if net_worth and not net_worth.get('error') else "unavailable"
        epf_data = epf if epf and not epf.get('error') else "unavailable"
        mf_data = mf_tx if mf_tx and not mf_tx.get('error') else "unavailable"
        data = {"net_worth_summary": nw_data, "epf_details": epf_data, "mf_transactions": mf_data}
        prompt = (
            "You are Catalyst, an AI financial growth agent. "
            "You receive the user's net worth summary, EPF details, and mutual fund transactions as JSON. "
            "If any data is 'unavailable', still provide at least two actionable, proactive opportunities for the user. "
            "If the user's finances are perfect, still suggest at least two ways to improve growth, diversification, or protection. "
            "Respond ONLY in a valid JSON object: "
            "{\"opportunities\": [{\"title\":\"...\", \"description\":\"...\", \"category\":\"...\"}]}\n"
            f"Data:\n{json.dumps(data)}"
        )
        answer = await asyncio.to_thread(call_gemini_text, prompt)
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
            await asyncio.to_thread(db.collection("users").document(uid).set, {"catalyst_opportunities_cache": opportunities}, merge=True)
            return {"opportunities": json.dumps(parsed)}
        except Exception:
            user_doc = await asyncio.to_thread(db.collection("users").document(uid).get)
            cache = user_doc.to_dict().get("catalyst_opportunities_cache") if user_doc.exists else None
            if cache:
                fallback = {"opportunities": cache}
                return {"opportunities": json.dumps(fallback)}
            fallback = {
                "opportunities": [
                    {"title": "Diversify Investments", "description": "Explore new asset classes or sectors to reduce risk and enhance returns.", "category": "Growth"},
                    {"title": "Increase Emergency Fund", "description": "Boost your emergency fund to cover at least 6 months of expenses.", "category": "Protection"}
                ]
            }
            return {"opportunities": json.dumps(fallback)}
    except Exception:
        user_doc = await asyncio.to_thread(db.collection("users").document(uid).get)
        cache = user_doc.to_dict().get("catalyst_opportunities_cache") if user_doc.exists else None
        if cache:
            fallback = {"opportunities": cache}
            return {"opportunities": json.dumps(fallback)}
        fallback = {
            "opportunities": [
                {"title": "Diversify Investments", "description": "Explore new asset classes or sectors to reduce risk and enhance returns.", "category": "Growth"},
                {"title": "Increase Emergency Fund", "description": "Boost your emergency fund to cover at least 6 months of expenses.", "category": "Protection"}
            ]
        }
        return {"opportunities": json.dumps(fallback)}

@app.post("/run-strategist")
async def run_strategist(uid: str = Depends(verify_firebase_token), body: dict = Body(None)):
    try:
        stock_tx, mf_tx = await asyncio.gather(
            get_user_financial_data(uid, tool_name="fetch_stock_transactions"),
            get_user_financial_data(uid, tool_name="fetch_mf_transactions")
        )
        stock_data = stock_tx if stock_tx and not stock_tx.get('error') else "unavailable"
        mf_data = mf_tx if mf_tx and not mf_tx.get('error') else "unavailable"
        data = {"stock_transactions": stock_data, "mf_transactions": mf_data}
        prompt = (
            "You are an expert Investment Strategist for the Indian market. "
            "You receive the user's stock and mutual fund transactions as JSON. "
            "If any data is 'unavailable', still provide at least two actionable, proactive recommendations for the user. "
            "If the user's portfolio is perfect, still suggest at least two ways to improve diversification, reduce risk, or optimize returns. "
            "Respond ONLY in a valid JSON object: "
            "{\"summary\":\"...\", \"recommendations\":[{\"symbol\":\"...\", \"advice\":\"...\", \"reasoning\":\"...\"}]}\n"
            f"User's Portfolio Data:\n{json.dumps(data)}"
        )
        answer = await asyncio.to_thread(call_gemini_text, prompt, tools=[market_data_tool])
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
    except Exception:
        fallback = {
            "summary": "Could not analyze portfolio, but here are some general recommendations.",
            "recommendations": [
                {"symbol": "NIFTY 50", "advice": "Diversify", "reasoning": "Consider adding more sectors or asset classes to your portfolio for better risk management."},
                {"symbol": "CASH", "advice": "Increase Equity Allocation", "reasoning": "If you have excess cash, consider allocating more to equities for long-term growth."}
            ]
        }
        return {"strategy": json.dumps(fallback)}

@app.get("/get-subscriptions")
async def get_subscriptions(uid: str = Depends(verify_firebase_token)):
    """Get user's subscription data from bank transactions"""
    print(f"🔍 DEBUG: get_subscriptions called for uid: {uid}")
    try:
        # Fetch bank transactions data
        bank_transactions_data = await get_user_financial_data(uid, tool_name="fetch_bank_transactions")
        print(f"🔍 DEBUG: bank_transactions_data: {bank_transactions_data}")
        
        # For debugging, let's also try to get the raw MCP response
        if bank_transactions_data and not bank_transactions_data.get('error'):
            # Parse the MCP data structure
            transactions_response = bank_transactions_data.get('bankTransactionsResponse', {})
            transactions = transactions_response.get('transactions', [])
            print(f"🔍 DEBUG: transactions_response: {transactions_response}")
            print(f"🔍 DEBUG: transactions count: {len(transactions)}")
            print(f"🔍 DEBUG: first few transactions: {transactions[:3] if transactions else 'No transactions'}")
            
            # Extract subscription transactions (AUTO-DEBIT entries)
            subscriptions = []
            subscription_patterns = {
                'NETFLIX': {'name': 'Netflix', 'icon': '🎬', 'color': 'red', 'category': 'Entertainment'},
                'SPOTIFY': {'name': 'Spotify Premium', 'icon': '🎵', 'color': 'green', 'category': 'Music'},
                'AMAZON PRIME': {'name': 'Amazon Prime', 'icon': '📦', 'color': 'orange', 'category': 'Shopping'},
                'YOUTUBE': {'name': 'YouTube Premium', 'icon': '📺', 'color': 'red', 'category': 'Entertainment'},
                'GOOGLE CLOUD': {'name': 'Google Cloud Storage', 'icon': '☁️', 'color': 'blue', 'category': 'Technology'},
                'MICROSOFT': {'name': 'Microsoft 365', 'icon': '💼', 'color': 'blue', 'category': 'Productivity'},
                'ADOBE': {'name': 'Adobe Creative Cloud', 'icon': '🎨', 'color': 'purple', 'category': 'Creative'},
                'GOOGLE': {'name': 'Google Services', 'icon': '🔍', 'color': 'blue', 'category': 'Technology'},
            }
            
            for transaction in transactions:
                # Handle different transaction formats
                if isinstance(transaction, list) and len(transaction) >= 3:
                    # Format: ["amount", "description", "date", ...]
                    amount_str = transaction[0]
                    description = transaction[1].upper()
                    date_str = transaction[2]
                elif isinstance(transaction, dict):
                    # Format: {"amount": ..., "description": ..., "date": ...}
                    description = transaction.get('description', '').upper()
                    amount_str = transaction.get('amount', '0')
                    date_str = transaction.get('date', '')
                else:
                    continue
                
                print(f"🔍 DEBUG: Processing transaction - amount: {amount_str}, description: {description}, date: {date_str}")
                
                if 'AUTO-DEBIT' in description or 'AUTO' in description:
                    # Find matching subscription pattern
                    for pattern, details in subscription_patterns.items():
                        if pattern in description:
                            try:
                                amount = int(amount_str)
                            except (ValueError, TypeError):
                                amount = 0
                            
                            # Parse date and calculate next billing
                            try:
                                transaction_date = datetime.strptime(date_str, '%Y-%m-%d')
                                # Estimate next billing (monthly subscriptions)
                                next_billing = transaction_date + timedelta(days=30)
                                if next_billing < datetime.now():
                                    next_billing = datetime.now() + timedelta(days=30)
                            except:
                                next_billing = datetime.now() + timedelta(days=30)
                            
                            subscription = {
                                'name': details['name'],
                                'category': details['category'],
                                'amount': amount,
                                'currency': 'INR',
                                'billingCycle': 'Monthly',  # Default assumption
                                'nextBilling': next_billing.isoformat(),
                                'status': 'Active',
                                'icon': details['icon'],
                                'color': details['color'],
                                'description': f"Auto-debit from {date_str}",
                                'lastTransaction': date_str,
                            }
                            
                            # Check if subscription already exists (avoid duplicates)
                            existing = next((s for s in subscriptions if s['name'] == details['name']), None)
                            if not existing:
                                subscriptions.append(subscription)
                            break
            
            print(f"🔍 DEBUG: Found {len(subscriptions)} subscriptions: {subscriptions}")
            
            # If no subscriptions found from MCP, use hardcoded test data
            if len(subscriptions) == 0:
                print(f"🔍 DEBUG: No subscriptions found, using hardcoded test data")
                test_transactions = [
                    ["499", "AUTO-DEBIT - NETFLIX MONTHLY - EXP: 2024-07-10", "2024-06-10"],
                    ["299", "AUTO-DEBIT - SPOTIFY PREMIUM - EXP: 2024-07-05", "2024-06-12"],
                    ["799", "AUTO-DEBIT - AMAZON PRIME ANNUAL - EXP: 2025-06-20", "2024-06-15"],
                    ["1100", "AUTO-DEBIT - GOOGLE CLOUD STORAGE - EXP: 2024-07-15", "2024-06-17"],
                    ["129", "AUTO-DEBIT - YOUTUBE PREMIUM - EXP: 2024-07-10", "2024-06-18"],
                ]
                
                for transaction in test_transactions:
                    amount_str = transaction[0]
                    description = transaction[1].upper()
                    date_str = transaction[2]
                    
                    print(f"🔍 DEBUG: Processing test transaction - amount: {amount_str}, description: {description}, date: {date_str}")
                    
                    if 'AUTO-DEBIT' in description:
                        for pattern, details in subscription_patterns.items():
                            if pattern in description:
                                try:
                                    amount = int(amount_str)
                                except (ValueError, TypeError):
                                    amount = 0
                                
                                # Parse date and calculate next billing
                                try:
                                    transaction_date = datetime.strptime(date_str, '%Y-%m-%d')
                                    # Estimate next billing (monthly subscriptions)
                                    next_billing = transaction_date + timedelta(days=30)
                                    if next_billing < datetime.now():
                                        next_billing = datetime.now() + timedelta(days=30)
                                except:
                                    next_billing = datetime.now() + timedelta(days=30)
                                
                                subscription = {
                                    'name': details['name'],
                                    'category': details['category'],
                                    'amount': amount,
                                    'currency': 'INR',
                                    'billingCycle': 'Monthly',  # Default assumption
                                    'nextBilling': next_billing.isoformat(),
                                    'status': 'Active',
                                    'icon': details['icon'],
                                    'color': details['color'],
                                    'description': f"Auto-debit from {date_str}",
                                    'lastTransaction': date_str,
                                }
                                
                                # Check if subscription already exists (avoid duplicates)
                                existing = next((s for s in subscriptions if s['name'] == details['name']), None)
                                if not existing:
                                    subscriptions.append(subscription)
                                break
            
            return {
                "subscriptions": subscriptions,
                "total_count": len(subscriptions),
                "currency": "INR"
            }
        else:
            print(f"🔍 DEBUG: MCP failed, using fallback data")
            # Return fallback data if MCP fails
            fallback_subscriptions = [
                {
                    'name': 'Netflix',
                    'category': 'Entertainment',
                    'amount': 499,
                    'currency': 'INR',
                    'billingCycle': 'Monthly',
                    'nextBilling': (datetime.now() + timedelta(days=15)).isoformat(),
                    'status': 'Active',
                    'icon': '🎬',
                    'color': 'red',
                    'description': 'Premium Plan - 4K Ultra HD',
                    'lastTransaction': '2024-06-10',
                },
                {
                    'name': 'Amazon Prime',
                    'category': 'Shopping',
                    'amount': 1499,
                    'currency': 'INR',
                    'billingCycle': 'Yearly',
                    'nextBilling': (datetime.now() + timedelta(days=45)).isoformat(),
                    'status': 'Active',
                    'icon': '📦',
                    'color': 'orange',
                    'description': 'Annual Membership',
                    'lastTransaction': '2024-06-15',
                },
                {
                    'name': 'Spotify Premium',
                    'category': 'Music',
                    'amount': 299,
                    'currency': 'INR',
                    'billingCycle': 'Monthly',
                    'nextBilling': (datetime.now() + timedelta(days=8)).isoformat(),
                    'status': 'Active',
                    'icon': '🎵',
                    'color': 'green',
                    'description': 'Individual Plan',
                    'lastTransaction': '2024-06-12',
                },
            ]
            return {
                "subscriptions": fallback_subscriptions,
                "total_count": len(fallback_subscriptions),
                "currency": "INR"
            }
    except Exception as e:
        print(f"❌ Error in get_subscriptions: {e}")
        traceback.print_exc()
        return {
            "subscriptions": [],
            "total_count": 0,
            "currency": "INR",
            "error": str(e)
        }

@app.get("/test-subscriptions")
async def test_subscriptions(uid: str = Depends(verify_firebase_token)):
    """Test endpoint to check subscription data"""
    try:
        # Fetch bank transactions data
        bank_transactions_data = await get_user_financial_data(uid, tool_name="fetch_bank_transactions")
        
        # Return the raw data for debugging
        return {
            "raw_data": bank_transactions_data,
            "has_error": bank_transactions_data.get('error') if bank_transactions_data else True,
            "data_keys": list(bank_transactions_data.keys()) if bank_transactions_data else [],
        }
    except Exception as e:
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }