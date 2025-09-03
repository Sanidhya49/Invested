# invested-backend/main.py
from fastapi import FastAPI, HTTPException, status, Depends, Request
from fastapi.responses import StreamingResponse
from typing import List
from uuid import UUID
import datetime
import services
from schemas import SubscriptionInfo, FinancialGoal, FinancialGoalUpdate
from utils.pdf_generator import generate_summary_pdf
import pipelines # Added for financial health, but note to use tool-based approach later
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
import time

# Import agents router
from routers.agents import router as agents_router
# --- Gemini & MCP Agent Integration ---
import os
import httpx
import google.generativeai as genai
import json
import asyncio
from pydantic import BaseModel

# Import configuration
from config import (
    FI_MCP_SERVER_URL, 
    MCP_AUTH_PHONE_NUMBER, 
    GEMINI_API_KEY, 
    SECRET_KEY, 
    ALGORITHM, 
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALLOWED_ORIGINS,
    log_config
)

# Initialize Firebase Admin SDK
import firebase_admin
from firebase_admin import credentials, firestore
import os

# Get the path to the Firebase credentials file
current_dir = os.path.dirname(os.path.abspath(__file__))
agents_dir = os.path.join(os.path.dirname(current_dir), 'agents')
firebase_credentials_path = os.path.join(agents_dir, 'invested-hackathon-firebase-adminsdk-fbsvc-38735ba923.json')

try:
    # Initialize Firebase if not already initialized
    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_credentials_path)
        firebase_admin.initialize_app(cred)
        print("✅ Firebase Admin SDK initialized successfully")
    else:
        print("✅ Firebase Admin SDK already initialized")
except Exception as e:
    print(f"❌ Failed to initialize Firebase Admin SDK: {e}")
    print("⚠️ Agents may not work properly without Firebase")

# Log configuration on startup
log_config()

BACKEND_MCP_SESSION_ID = f"backend_session_{os.urandom(8).hex()}"

if not all([GEMINI_API_KEY, FI_MCP_SERVER_URL, MCP_AUTH_PHONE_NUMBER]):
    print("WARNING: One or more environment variables (GEMINI_API_KEY, FI_MCP_SERVER_URL, MCP_AUTH_PHONE_NUMBER) are not set. Gemini/Agent endpoint will not work.")
else:
    genai.configure(api_key=GEMINI_API_KEY)

# --- Agent Endpoint Models ---
class AgentBuilderRequest(BaseModel):
    intent: str
    entities: dict = {}
    session_id: str

class FinancialInsightResponse(BaseModel):
    status: str
    message: str
    data: dict = {}

GLOBAL_MCP_SESSION_ID = None

async def call_mcp_tool_agent(tool_name: str) -> dict:
    if not GLOBAL_MCP_SESSION_ID:
        raise HTTPException(status_code=500, detail="MCP session not established during startup.")
    headers = {"Content-Type": "application/json", "X-Session-ID": GLOBAL_MCP_SESSION_ID}
    payload = {"tool_name": tool_name, "params": {}}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{FI_MCP_SERVER_URL}/mcp/stream", json=payload, headers=headers, timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        detail = f"MCP Server returned an error: {e.response.status_code}. Body: {e.response.text}"
        print(f"ERROR: {detail}")
        raise HTTPException(status_code=500, detail=detail)
    except Exception as e:
        print(f"ERROR: An unexpected error occurred in call_mcp_tool_agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def get_financial_insight(tool_name: str, prompt_template: str) -> dict:
    mcp_data = await call_mcp_tool_agent(tool_name)
    prompt = prompt_template.format(mcp_data=json.dumps(mcp_data, indent=2))
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    gemini_response = await model.generate_content_async(
        prompt,
        generation_config=genai.types.GenerationConfig(response_mime_type="application/json")
    )
    insight_json_string = gemini_response.text
    if insight_json_string.startswith("```json"):
        insight_json_string = insight_json_string[7:-3].strip()
    return json.loads(insight_json_string)

SPENDING_ANALYSIS_PROMPT = """
You are a helpful financial assistant. Analyze the following bank transactions to provide a summary of spending habits. Highlight top 3 spending categories and any unusual or large transactions.

Transaction Data:
{mcp_data}

Please provide a structured JSON response with a 'summary' string, a 'categories' dictionary (category: total_amount), and a 'notable_transactions' list.
"""

NET_WORTH_PROMPT = """
You are a helpful financial assistant. Summarize the user's net worth based on the following data. Highlight the total net worth and provide a breakdown by asset and liability types.

Net Worth Data:
{mcp_data}

Provide a structured JSON response with a 'summary' string and a 'details' dictionary containing 'total_net_worth', 'assets', and 'liabilities'.
"""

CREDIT_REPORT_PROMPT = """
You are a helpful financial assistant. Analyze the user's credit report data. Summarize the credit score, active loans, credit utilization, and any notable history. Also, state the date of birth from the report.

Credit Report Data:
{mcp_data}

Provide a structured JSON response with a 'summary' string, 'credit_score' (int), 'active_accounts' (list), and 'date_of_birth' (string YYYY-MM-DD).
"""

INTENT_CONFIG = {
    "analyze_spending": {
        "tool_name": "fetch_bank_transactions",
        "prompt_template": SPENDING_ANALYSIS_PROMPT,
        "message": "Here's a summary of your spending habits:"
    },
    "fetch_net_worth": {
        "tool_name": "fetch_net_worth",
        "prompt_template": NET_WORTH_PROMPT,
        "message": "Here's your net worth summary:"
    },
    "fetch_credit_report": {
        "tool_name": "fetch_credit_report",
        "prompt_template": CREDIT_REPORT_PROMPT,
        "message": "Here's your credit report summary:"
    }
}

app = FastAPI(
    title="Invested Backend API",
    description="API for financial analysis, goal planning, and reporting."
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include agents router
app.include_router(agents_router)

@app.on_event("startup")
async def startup_event_agent():
    global GLOBAL_MCP_SESSION_ID
    print(f"🔍 DEBUG: FI_MCP_SERVER_URL = {FI_MCP_SERVER_URL}")
    print(f"🔍 DEBUG: MCP_AUTH_PHONE_NUMBER = {MCP_AUTH_PHONE_NUMBER}")
    print(f"🔍 DEBUG: BACKEND_MCP_SESSION_ID = {BACKEND_MCP_SESSION_ID}")
    
    if not all([FI_MCP_SERVER_URL, MCP_AUTH_PHONE_NUMBER]):
        print("WARNING: FI_MCP_SERVER_URL or MCP_AUTH_PHONE_NUMBER not set. Skipping MCP session setup.")
        return
    print("Attempting to get MCP session for agent endpoint...")
    
    # Try to connect to MCP server with retries
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            print(f"🔍 DEBUG: Attempting to connect to {FI_MCP_SERVER_URL}/mockWebPage?sessionId={BACKEND_MCP_SESSION_ID}")
            async with httpx.AsyncClient() as client:
                response1 = await client.get(f"{FI_MCP_SERVER_URL}/mockWebPage?sessionId={BACKEND_MCP_SESSION_ID}")
                print(f"🔍 DEBUG: MockWebPage response status: {response1.status_code}")
                
                print(f"🔍 DEBUG: Attempting to login with sessionId={BACKEND_MCP_SESSION_ID}, phoneNumber={MCP_AUTH_PHONE_NUMBER}")
                response2 = await client.post(
                    f"{FI_MCP_SERVER_URL}/login",
                    data={"sessionId": BACKEND_MCP_SESSION_ID, "phoneNumber": MCP_AUTH_PHONE_NUMBER}
                )
                print(f"🔍 DEBUG: Login response status: {response2.status_code}")
                
            GLOBAL_MCP_SESSION_ID = BACKEND_MCP_SESSION_ID
            print(f"✅ Successfully obtained global MCP session: {GLOBAL_MCP_SESSION_ID}")
            return
        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1}/{max_retries}: Could not connect to MCP server: {e}")
            print(f"🔍 DEBUG: Exception type: {type(e).__name__}")
            if attempt < max_retries - 1:
                print(f"⏳ Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print("❌ Failed to connect to MCP server after all retries. Agent endpoints will not work until MCP server is available.")
                print("💡 Make sure to start the MCP server (fi-mcp-dev) before using agent features.")

@app.post("/process_agent_request", response_model=FinancialInsightResponse)
async def process_agent_request(request: AgentBuilderRequest):
    config = INTENT_CONFIG.get(request.intent)
    if not config:
        raise HTTPException(status_code=400, detail=f"Intent '{request.intent}' not supported.")
    try:
        insight_data = await get_financial_insight(
            tool_name=config["tool_name"],
            prompt_template=config["prompt_template"]
        )
        return FinancialInsightResponse(
            status="success",
            message=config["message"],
            data=insight_data
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    phone_number: str | None = None

def make_json_serializable(obj):
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(v) for v in obj]
    elif isinstance(obj, UUID):
        return str(obj)
    elif isinstance(obj, datetime.date):
        return obj.isoformat()
    else:
        return obj

# OTP login: always accept any OTP for demo
@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    phone_number = form_data.username
    # Accept any OTP (form_data.password)
    access_token = jwt.encode({"sub": phone_number, "exp": int(time.time()) + 3600}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_phone_number(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        phone_number: str = payload.get("sub")
        if phone_number is None:
            raise credentials_exception
        return phone_number
    except JWTError:
        raise credentials_exception

# Update all endpoints to use phone_number from JWT, not from request
@app.get(f"/api/me/goals", response_model=List[FinancialGoal])
async def get_all_goals(current_phone_number: str = Depends(get_current_phone_number)):
    data = await services.call_mcp_get_goals(current_phone_number)
    if data is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Goals not found")
    return [FinancialGoal(**goal) for goal in data]

@app.post(f"/api/me/goals", response_model=List[FinancialGoal], status_code=status.HTTP_201_CREATED)
async def add_new_goal(goal: FinancialGoal, current_phone_number: str = Depends(get_current_phone_number)):
    serializable_goal = make_json_serializable(goal.dict())
    data = await services.call_mcp_add_goal(current_phone_number, serializable_goal)
    if data is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to add goal")
    return [FinancialGoal(**goal) for goal in data]

@app.put(f"/api/me/goals/{{goal_id}}", response_model=FinancialGoal)
async def update_existing_goal(goal_id: UUID, goal_update: FinancialGoalUpdate, current_phone_number: str = Depends(get_current_phone_number)):
    serializable_update = make_json_serializable(goal_update.dict(exclude_unset=True))
    data = await services.call_mcp_update_goal(current_phone_number, str(goal_id), serializable_update)
    if data is None or not data:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Goal not found")
    updated_goal = next((goal for goal in data if str(goal.get('goal_id')) == str(goal_id)), None)
    if not updated_goal:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Updated goal not found")
    return FinancialGoal(**updated_goal)

@app.delete(f"/api/me/goals/{{goal_id}}", response_model=List[FinancialGoal])
async def delete_existing_goal(goal_id: UUID, current_phone_number: str = Depends(get_current_phone_number)):
    data = await services.call_mcp_delete_goal(current_phone_number, str(goal_id))
    if data is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Goal not found")
    return [FinancialGoal(**goal) for goal in data]


# --- Feature 5: Endpoint for PDF Export ---
@app.get(f"/api/me/export/summary.pdf")
async def export_summary_pdf(current_phone_number: str = Depends(get_current_phone_number)):
    try:
        # Fetch net worth data
        net_worth_data = await services.call_mcp_net_worth(current_phone_number)
        if net_worth_data is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Net worth data not found")
        
        # Fetch goals data
        goals_data = await services.get_goals(current_phone_number)
        
        # Generate PDF
        pdf_buffer = generate_summary_pdf(net_worth_data, goals_data)
        
        return StreamingResponse(
            pdf_buffer, 
            media_type="application/pdf", 
            headers={
                "Content-Disposition": f"attachment; filename=invested_summary_{current_phone_number}.pdf"
            }
        )
    except Exception as e:
        print(f"PDF generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

# --- Feature 6: Financial Health Score (Placeholder - will update later with tools) ---
@app.get(f"/api/me/analysis/financial-health", summary="Get Financial Health Score")
async def get_financial_health_score(current_phone_number: str = Depends(get_current_phone_number)):
    """Get comprehensive financial health score"""
    try:
        score_data = await services.calculate_financial_health_score(current_phone_number)
        return score_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate financial health score: {e}")

@app.get(f"/api/me/analysis/detailed", summary="Get Detailed Financial Analysis")
async def get_detailed_analysis(current_phone_number: str = Depends(get_current_phone_number)):
    """Get detailed financial analysis with breakdowns and recommendations"""
    try:
        analysis_data = await services.get_detailed_financial_analysis(current_phone_number)
        return analysis_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get detailed analysis: {e}")
    transactions_data = await services.call_mcp_tool("GetBankTransactions", current_phone_number) 
    
    # These still use direct file fetch for now. We'll make them tools later.
    net_worth_data = await services.fetch_from_mcp(current_phone_number, "fetch_net_worth.json")
    investments_data_mf = await services.fetch_from_mcp(current_phone_number, "fetch_mf_transactions.json")
    investments_data_epf = await services.fetch_from_mcp(current_phone_number, "fetch_epf_details.json")

    if transactions_data is None: 
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Bank transactions not found for financial health analysis")
    if net_worth_data is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Net worth data not found for financial health analysis")


    all_txns_flat = []
    if 'bankTransactions' in transactions_data:
        for bank_account in transactions_data['bankTransactions']:
            for txn_raw in bank_account['txns']:
                all_txns_flat.append({
                    'amount': float(txn_raw[0]),
                    'narration': txn_raw[1],
                    'date': txn_raw[2],
                    'type': 'CREDIT' if txn_raw[3] == 1 else 'DEBIT',
                    'mode': txn_raw[4],
                    'balance': float(txn_raw[5])
                })

    transactions_df = pipelines.process_transactions(all_txns_flat)

    total_investment_value = 0
    if investments_data_mf and 'mfTransactions' in investments_data_mf:
        for mf_txn_group in investments_data_mf['mfTransactions']:
            for txn in mf_txn_group['txns']:
                total_investment_value += txn[4]

    if investments_data_epf and 'uanAccounts' in investments_data_epf:
        for account in investments_data_epf['uanAccounts']:
            if 'rawDetails' in account and 'overall_pf_balance' in account['rawDetails']:
                total_investment_value += float(account['rawDetails']['overall_pf_balance'].get('current_pf_balance', 0))
                total_investment_value += float(account['rawDetails']['overall_pf_balance'].get('pension_balance', 0))

    # Get stock value from net_worth_data as it contains current aggregate values
    stock_investment_value = 0
    if net_worth_data and 'netWorthResponse' in net_worth_data and 'assetValues' in net_worth_data['netWorthResponse']:
        for asset in net_worth_data['netWorthResponse']['assetValues']:
            if asset.get('netWorthAttribute') == 'ASSET_TYPE_INDIAN_SECURITIES' or \
               asset.get('netWorthAttribute') == 'ASSET_TYPE_US_SECURITIES':
                stock_investment_value += float(asset['value']['units'])


    aggregated_investments = {"total_value": total_investment_value + stock_investment_value}

    emergency_fund_progress = 0.0
    goals = await services.get_goals(current_phone_number)
    for goal in goals:
        if "emergency fund" in goal.title.lower():
            if goal.target_amount > 0:
                emergency_fund_progress = goal.current_amount / goal.target_amount
            break

    financial_health = pipelines.calculate_financial_health_score(transactions_df, aggregated_investments, emergency_fund_progress)
    return financial_health

@app.get(f"/api/me/net-worth")
async def get_net_worth(current_phone_number: str = Depends(get_current_phone_number)):
    data = await services.call_mcp_net_worth(current_phone_number)
    if data is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return data

@app.get(f"/api/me/mf-transactions")
async def get_mf_transactions(current_phone_number: str = Depends(get_current_phone_number)):
    data = await services.call_mcp_mf_transactions(current_phone_number)
    if data is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User mutual fund transactions not found or tool failed")
    return data

@app.get(f"/api/me/stock-transactions")
async def get_stock_transactions(current_phone_number: str = Depends(get_current_phone_number)):
    data = await services.call_mcp_stock_transactions(current_phone_number)
    if data is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User stock transactions not found or tool failed")
    return data

@app.get(f"/api/me/epf-details")
async def get_epf_details(current_phone_number: str = Depends(get_current_phone_number)):
    data = await services.call_mcp_epf_details(current_phone_number)
    if data is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User EPF details not found or tool failed")
    return data

@app.get(f"/api/me/credit-report")
async def get_credit_report(current_phone_number: str = Depends(get_current_phone_number)):
    data = await services.call_mcp_credit_report(current_phone_number)
    if data is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User credit report not found or tool failed")
    return data

@app.get(f"/api/me/analysis/subscriptions")
async def analyze_subscriptions(current_phone_number: str = Depends(get_current_phone_number)):
    transactions = await services.call_mcp_tool("GetBankTransactions", current_phone_number)
    if transactions is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User transactions not found for subscription analysis")
    return services.detect_subscriptions(transactions)

@app.get(f"/api/me/bank-transactions")
async def get_bank_transactions(current_phone_number: str = Depends(get_current_phone_number)):
    data = await services.call_mcp_tool("GetBankTransactions", current_phone_number)
    if data is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User bank transactions not found or tool failed")
    return data

@app.post("/bridge/firebase-token")
async def get_firebase_token(current_phone_number: str = Depends(get_current_phone_number)):
    """
    Bridge endpoint to get a Firebase token for the agents server.
    This allows the frontend to use the existing JWT system with the agents server.
    """
    try:
        # For demo purposes, create a simple Firebase-like token
        # In production, you'd integrate with Firebase Auth
        firebase_token = jwt.encode(
            {
                "uid": current_phone_number,
                "phone_number": current_phone_number,
                "exp": int(time.time()) + 3600
            }, 
            SECRET_KEY, 
            algorithm=ALGORITHM
        )
        return {"firebase_token": firebase_token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Firebase token: {e}")

@app.post("/retry-mcp-connection")
async def retry_mcp_connection():
    """
    Manual endpoint to retry connecting to the MCP server.
    Useful if the MCP server wasn't available during startup.
    """
    global GLOBAL_MCP_SESSION_ID
    if not all([FI_MCP_SERVER_URL, MCP_AUTH_PHONE_NUMBER]):
        raise HTTPException(status_code=500, detail="MCP server URL or phone number not configured")
    
    try:
        async with httpx.AsyncClient() as client:
            await client.get(f"{FI_MCP_SERVER_URL}/mockWebPage?sessionId={BACKEND_MCP_SESSION_ID}")
            await client.post(
                f"{FI_MCP_SERVER_URL}/login",
                data={"sessionId": BACKEND_MCP_SESSION_ID, "phoneNumber": MCP_AUTH_PHONE_NUMBER}
            )
        GLOBAL_MCP_SESSION_ID = BACKEND_MCP_SESSION_ID
        return {"status": "success", "message": f"Successfully connected to MCP server. Session ID: {GLOBAL_MCP_SESSION_ID}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to MCP server: {e}")