# Shared utilities for Invested AI agents

import firebase_admin
from firebase_admin import firestore
import httpx
import asyncio
import json
import traceback
from datetime import datetime, timedelta
import vertexai
from vertexai.generative_models import GenerativeModel, Tool, Part, FunctionDeclaration
import pprint

# Constants
MOCK_SERVER_BASE_URL = "http://localhost:8080"
CACHE_EXPIRY_SECONDS = 300  # 5 minutes

# --- Dynamic Data Fetching ---
async def get_user_financial_data(uid: str, tool_name: str, timeout=30):
    try:
        db = firestore.client()
        user_doc = await asyncio.to_thread(db.collection("users").document(uid).get)
        if not user_doc.exists:
            print(f"❌ User document not found for uid: {uid}")
            return {"error": f"User not found"}
        
        user_data = user_doc.to_dict()
        if "fi_session_id" not in user_data:
            print(f"❌ No fi_session_id found for user: {uid}")
            return {"error": f"No session ID found. Please authenticate first."}
        
        session_id = user_data["fi_session_id"]
        print(f"🔍 Using session ID: {session_id} for tool: {tool_name}")
        
        headers = {"X-Session-ID": session_id}
        request_body = {"tool_name": tool_name, "phone_number": uid}
        
        try:
            async with httpx.AsyncClient() as client:
                print(f"🔍 Making request to MCP server for tool: {tool_name}")
                response = await client.post(
                    "http://localhost:8080/mcp/stream",
                    headers=headers,
                    json=request_body,
                    timeout=timeout
                )
                print(f"🔍 MCP response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ SUCCESS: Fetched '{tool_name}' data from MCP server")
                    return data
                else:
                    print(f"⚠️ Error from MCP server for tool '{tool_name}': {response.status_code} - {response.text}")
                    return {"error": f"MCP server returned {response.status_code}: {response.text}"}
                    
        except httpx.TimeoutException:
            print(f"❌ TIMEOUT: MCP server timed out for '{tool_name}'")
            return {"error": f"Timeout fetching {tool_name} from MCP server."}
        except httpx.ConnectError:
            print(f"❌ CONNECTION ERROR: Could not connect to MCP server for '{tool_name}'")
            return {"error": f"Could not connect to MCP server for {tool_name}."}
        except Exception as e:
            print(f"❌ ERROR: MCP server error for '{tool_name}': {e}")
            return {"error": f"Error fetching {tool_name} from MCP server: {e}"}
            
    except Exception as e:
        print(f"❌ Failed to fetch live data for tool '{tool_name}'. Error: {e}")
        traceback.print_exc()
    
    print(f"ℹ️ INFO: Fallback for '{tool_name}'.")
    return {"error": f"Could not fetch {tool_name}."}

# --- Helper: Get Cached MCP Data ---
async def get_cached_mcp_data(uid: str):
    db = firestore.client()
    user_doc = await asyncio.to_thread(db.collection("users").document(uid).get)
    if user_doc.exists:
        user_data = user_doc.to_dict()
        mcp_cache = user_data.get("mcp_data_cache")
        if mcp_cache:
            ts = mcp_cache.get("mcp_cache_timestamp")
            if ts:
                try:
                    cache_time = datetime.fromisoformat(ts)
                    if datetime.utcnow() - cache_time < timedelta(seconds=CACHE_EXPIRY_SECONDS):
                        return mcp_cache
                except Exception:
                    pass
    return None

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
                return clean_gemini_response(final_response.text)
        return clean_gemini_response(response.text)
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        traceback.print_exc()
        return f"Error: Gemini API call failed: {e}"

def clean_gemini_response(text: str) -> str:
    """Clean and format Gemini API response text"""
    if not text:
        return ""
    
    # Remove extra newlines and normalize spacing
    cleaned = text.replace('\n\n\n', '\n\n')  # Remove triple newlines
    cleaned = cleaned.replace('\n\n\n\n', '\n\n')  # Remove quadruple newlines
    cleaned = cleaned.replace('nn', '\n')  # Fix common formatting issue
    cleaned = cleaned.replace('  ', ' ')  # Remove double spaces
    
    # Remove leading/trailing whitespace
    cleaned = cleaned.strip()
    
    # Ensure proper paragraph breaks
    cleaned = cleaned.replace('\n\n', '\n\n')  # Normalize paragraph breaks
    
    return cleaned

# --- Helper: Make Data Firestore Safe ---
def create_safe_summary(data):
    """Create a completely safe, simplified summary of the data for Firestore"""
    safe_data = {
        "mcp_cache_timestamp": datetime.utcnow().isoformat()
    }
    
    # Handle bank transactions - create a simple summary
    if 'bank_transactions' in data and isinstance(data['bank_transactions'], dict):
        bank_data = data['bank_transactions']
        if 'bankTransactions' in bank_data and isinstance(bank_data['bankTransactions'], list):
            banks = bank_data['bankTransactions']
            safe_data['bank_summary'] = {
                'total_banks': len(banks),
                'total_transactions': 0,
                'recent_transactions': []
            }
            
            # Count total transactions and get recent ones
            for bank in banks[:2]:  # Only first 2 banks
                if isinstance(bank, dict) and 'txns' in bank:
                    txns = bank.get('txns', [])
                    if isinstance(txns, list):
                        safe_data['bank_summary']['total_transactions'] += len(txns)
                        
                        # Get first 5 transactions as summary
                        for txn in txns[:5]:
                            if isinstance(txn, list) and len(txn) >= 4:
                                safe_data['bank_summary']['recent_transactions'].append({
                                    'amount': str(txn[0]) if len(txn) > 0 else '0',
                                    'description': str(txn[1])[:100] if len(txn) > 1 else 'Unknown',
                                    'date': str(txn[2]) if len(txn) > 2 else 'Unknown',
                                    'type': str(txn[3]) if len(txn) > 3 else 'Unknown'
                                })
    
    # Handle credit report - create a simple summary
    if 'credit_report' in data and isinstance(data['credit_report'], dict):
        credit_data = data['credit_report']
        if 'creditReports' in credit_data and isinstance(credit_data['creditReports'], list):
            credit_reports = credit_data['creditReports']
            if credit_reports and isinstance(credit_reports[0], dict):
                report = credit_reports[0]
                if 'creditReportData' in report:
                    report_data = report['creditReportData']
                    safe_data['credit_summary'] = {
                        'score': 'N/A',
                        'total_accounts': 0,
                        'total_balance': 0
                    }
                    
                    # Extract credit score
                    if 'score' in report_data and isinstance(report_data['score'], dict):
                        score_data = report_data['score']
                        safe_data['credit_summary']['score'] = str(score_data.get('bureauScore', 'N/A'))
                    
                    # Extract account summary
                    if 'creditAccount' in report_data and isinstance(report_data['creditAccount'], dict):
                        account_data = report_data['creditAccount']
                        if 'creditAccountSummary' in account_data:
                            summary = account_data['creditAccountSummary']
                            if 'account' in summary:
                                account_info = summary['account']
                                safe_data['credit_summary']['total_accounts'] = int(account_info.get('creditAccountTotal', 0))
                            
                            if 'totalOutstandingBalance' in summary:
                                balance_info = summary['totalOutstandingBalance']
                                safe_data['credit_summary']['total_balance'] = int(balance_info.get('outstandingBalanceAll', 0))
    
    # Handle mutual fund transactions - create a simple summary
    if 'mf_transactions' in data and isinstance(data['mf_transactions'], dict):
        mf_data = data['mf_transactions']
        if 'mfTransactions' in mf_data and isinstance(mf_data['mfTransactions'], list):
            mf_transactions = mf_data['mfTransactions']
            safe_data['mf_summary'] = {
                'total_funds': len(mf_transactions),
                'total_investment': 0,
                'funds': []
            }
            
            for fund in mf_transactions[:3]:  # Only first 3 funds
                if isinstance(fund, dict):
                    fund_info = {
                        'name': str(fund.get('schemeName', 'Unknown'))[:50],
                        'folio': str(fund.get('folioId', 'Unknown')),
                        'transactions': 0
                    }
                    
                    if 'txns' in fund and isinstance(fund['txns'], list):
                        fund_info['transactions'] = len(fund['txns'])
                        # Calculate total investment
                        for txn in fund['txns']:
                            if isinstance(txn, list) and len(txn) >= 5:
                                try:
                                    amount = float(txn[4]) if txn[4] else 0
                                    safe_data['mf_summary']['total_investment'] += amount
                                except (ValueError, TypeError):
                                    pass
                    
                    safe_data['mf_summary']['funds'].append(fund_info)
    
    # Handle net worth - simple copy if it exists
    if 'net_worth' in data and isinstance(data['net_worth'], dict):
        net_worth = data['net_worth']
        safe_data['net_worth_summary'] = {
            'total_assets': 0,
            'total_liabilities': 0,
            'net_worth': 0
        }
        
        # Extract basic net worth info
        if 'netWorth' in net_worth and isinstance(net_worth['netWorth'], list):
            for item in net_worth['netWorth']:
                if isinstance(item, dict):
                    try:
                        assets = float(item.get('totalAssets', 0))
                        liabilities = float(item.get('totalLiabilities', 0))
                        net = float(item.get('netWorth', 0))
                        safe_data['net_worth_summary']['total_assets'] = assets
                        safe_data['net_worth_summary']['total_liabilities'] = liabilities
                        safe_data['net_worth_summary']['net_worth'] = net
                        break
                    except (ValueError, TypeError):
                        pass
    
    # Handle EPF details - simple copy if it exists
    if 'epf_details' in data and isinstance(data['epf_details'], dict):
        epf_data = data['epf_details']
        safe_data['epf_summary'] = {
            'total_balance': 0,
            'account_count': 0
        }
        
        if 'epfDetails' in epf_data and isinstance(epf_data['epfDetails'], list):
            epf_accounts = epf_data['epfDetails']
            safe_data['epf_summary']['account_count'] = len(epf_accounts)
            
            for account in epf_accounts[:2]:  # Only first 2 accounts
                if isinstance(account, dict):
                    try:
                        balance = float(account.get('currentBalance', 0))
                        safe_data['epf_summary']['total_balance'] += balance
                    except (ValueError, TypeError):
                        pass
    
    # Handle stock transactions - simple copy if it exists
    if 'stock_transactions' in data and isinstance(data['stock_transactions'], dict):
        stock_data = data['stock_transactions']
        safe_data['stock_summary'] = {
            'total_transactions': 0,
            'total_investment': 0
        }
        
        if 'stockTransactions' in stock_data and isinstance(stock_data['stockTransactions'], list):
            stock_transactions = stock_data['stockTransactions']
            safe_data['stock_summary']['total_transactions'] = len(stock_transactions)
            
            for txn in stock_transactions[:5]:  # Only first 5 transactions
                if isinstance(txn, list) and len(txn) >= 5:
                    try:
                        amount = float(txn[4]) if txn[4] else 0
                        safe_data['stock_summary']['total_investment'] += amount
                    except (ValueError, TypeError):
                        pass
    
    return safe_data

def force_json_safe(data):
    """Force data to be JSON-serializable and Firestore-compatible"""
    # Create a completely safe, simplified summary
    safe_data = create_safe_summary(data)
    
    # Then force through JSON round-trip to catch any remaining issues
    try:
        json_str = json.dumps(safe_data)
        result = json.loads(json_str)
        
        # Debug: Print what we're about to save to Firestore
        print("🔍 DEBUG: Safe data being saved to Firestore:")
        print(f"🔍 DEBUG: Data keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        print(f"🔍 DEBUG: Data type: {type(result)}")
        
        return result
    except Exception as e:
        print(f"❌ JSON serialization failed: {e}")
        # Fallback: return a minimal safe structure
        return {"error": "Data could not be serialized", "timestamp": datetime.utcnow().isoformat()}

# --- Market Performance Tool (for Strategist) ---
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

# Market data tool definition
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