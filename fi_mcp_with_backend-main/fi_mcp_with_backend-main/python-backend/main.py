# main.py (Final Version)
from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel
import os
import httpx
import google.generativeai as genai
import json
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# --- Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FI_MCP_SERVER_URL = os.getenv("FI_MCP_SERVER_URL")
MCP_AUTH_PHONE_NUMBER = os.getenv("MCP_AUTH_PHONE_NUMBER")
BACKEND_MCP_SESSION_ID = f"backend_session_{os.urandom(8).hex()}"

if not all([GEMINI_API_KEY, FI_MCP_SERVER_URL, MCP_AUTH_PHONE_NUMBER]):
    raise ValueError("One or more environment variables (GEMINI_API_KEY, FI_MCP_SERVER_URL, MCP_AUTH_PHONE_NUMBER) are not set.")

genai.configure(api_key=GEMINI_API_KEY)

# --- Pydantic Models ---
class AgentBuilderRequest(BaseModel):
    intent: str
    entities: dict = {}
    session_id: str

class FinancialInsightResponse(BaseModel):
    status: str
    message: str
    data: dict = {}

# --- Global MCP Session ---
GLOBAL_MCP_SESSION_ID = None

# --- MCP Tool and Gemini Helper Functions ---

async def call_mcp_tool(tool_name: str) -> dict:
    """Calls the specified tool on the MCP server and returns the data."""
    if not GLOBAL_MCP_SESSION_ID:
        raise HTTPException(status_code=500, detail="MCP session not established during startup.")

    headers = {"Content-Type": "application/json", "X-Session-ID": GLOBAL_MCP_SESSION_ID}
    payload = {"tool_name": tool_name, "params": {}}
    
    print(f"Calling MCP Tool: '{tool_name}'")
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
        print(f"ERROR: An unexpected error occurred in call_mcp_tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def get_financial_insight(tool_name: str, prompt_template: str) -> dict:
    """
    A reusable helper function that gets data from an MCP tool,
    sends it to Gemini with a specific prompt, and returns the structured insight.
    """
    # 1. Get data from the MCP server
    mcp_data = await call_mcp_tool(tool_name)
    
    # 2. Format the prompt with the fetched data
    prompt = prompt_template.format(mcp_data=json.dumps(mcp_data, indent=2))
    
    # 3. Call the Gemini model
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    gemini_response = await model.generate_content_async(
        prompt,
        generation_config=genai.types.GenerationConfig(response_mime_type="application/json")
    )
    
    # 4. Clean and parse the JSON response
    insight_json_string = gemini_response.text
    if insight_json_string.startswith("```json"):
        insight_json_string = insight_json_string[7:-3].strip()
        
    return json.loads(insight_json_string)

# --- Prompt Templates and Intent Configuration ---
# Moving prompts out of the main logic makes them easier to manage.

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

# This dictionary makes adding new intents very easy.
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

# --- FastAPI Events and Endpoints ---

@app.on_event("startup")
async def startup_event():
    """Establishes a session with the MCP server when the application starts."""
    print("Attempting to get MCP session for common use...")
    global GLOBAL_MCP_SESSION_ID
    try:
        async with httpx.AsyncClient() as client:
            await client.get(f"{FI_MCP_SERVER_URL}/mockWebPage?sessionId={BACKEND_MCP_SESSION_ID}")
            await client.post(
                f"{FI_MCP_SERVER_URL}/login",
                data={"sessionId": BACKEND_MCP_SESSION_ID, "phoneNumber": MCP_AUTH_PHONE_NUMBER}
            )
        GLOBAL_MCP_SESSION_ID = BACKEND_MCP_SESSION_ID
        print(f"Successfully obtained global MCP session: {GLOBAL_MCP_SESSION_ID}")
    except Exception as e:
        print(f"FATAL: Could not get MCP session at startup. Error: {e}")
        # In a real app, you might want the application to exit if this fails.
        # For this project, we'll allow it to start but tool calls will fail.

@app.post("/process_agent_request", response_model=FinancialInsightResponse)
async def process_agent_request(request: AgentBuilderRequest):
    """
    Receives a recognized intent, gets financial data, sends it to Gemini for analysis,
    and returns a structured insight.
    """
    # Look up the configuration for the requested intent
    config = INTENT_CONFIG.get(request.intent)

    if not config:
        raise HTTPException(status_code=400, detail=f"Intent '{request.intent}' not supported.")

    try:
        # Call our reusable helper function with the correct tool and prompt
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
        # Re-raise HTTPExceptions to let FastAPI handle them
        raise he
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")

        