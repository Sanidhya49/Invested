
import httpx
import pandas as pd
from datetime import datetime
from uuid import UUID, uuid4
from typing import Dict, List, Any
from schemas import Subscription, SubscriptionInfo, FinancialGoal, FinancialGoalUpdate
from pathlib import Path
import json

# Import configuration
from config import FI_MCP_SERVER_URL, MCP_FILE_PATH

# Keep MCP_MOCK_SERVER_URL for backward compatibility (deprecated)
MCP_MOCK_SERVER_URL = FI_MCP_SERVER_URL

# --- MODIFIED: Core MCP Data Fetching using Tool Calls ---
async def call_mcp_tool(tool_name: str, phone: str, inputs: Dict = None) -> Any:
    """Calls a specific MCP tool to fetch data."""


    if inputs is None:
        inputs = {}


    # Try both 'phoneNumber' and 'phone_number' as the parameter key, but do NOT send 'tool_name' in params
    tried_keys = ["phoneNumber", "phone_number"]
    for key in tried_keys:
        arguments = {key: phone}
        if inputs:
            arguments.update(inputs)
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": str(uuid4())
        }
        print(f"DEBUG: Trying payload with key '{key}': {payload}")
        url = f"{FI_MCP_SERVER_URL}/mcp/"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, timeout=10.0)
                if response.status_code == 400:
                    print(f"DEBUG: 400 Bad Request for key '{key}'. Response content: {response.text}. Trying next key if available.")
                    continue
                response.raise_for_status()

                result = response.json()
                print(f"DEBUG: Successfully called tool {tool_name} with key '{key}'. Result type: {result.get('type')}")

                # PATCH: Handle Go MCP server's result format
                if 'result' in result and 'content' in result['result']:
                    for content_item in result['result']['content']:
                        if content_item.get('type') == 'text' and 'text' in content_item:
                            try:
                                parsed_json = json.loads(content_item['text'])
                                print(f"DEBUG: Tool {tool_name} returned JSON embedded in 'text' field (Go MCP style).")
                                return parsed_json
                            except json.JSONDecodeError:
                                print(f"INFO: Tool {tool_name} returned plain text: {content_item['text']}")
                                return None
                    print(f"WARNING: No valid text content found in tool result for {tool_name}.")
                    return None
                # --- End PATCH ---

                if result.get('type') == 'json' and 'json' in result:
                    try:
                        return json.loads(result['json'])
                    except json.JSONDecodeError:
                        print(f"ERROR: Tool {tool_name} returned invalid JSON in 'json' field: {result['json']}")
                        return None
                elif result.get('type') == 'text' and 'text' in result:
                    try:
                        parsed_json = json.loads(result['text'])
                        print(f"DEBUG: Tool {tool_name} returned JSON embedded in 'text' field.")
                        return parsed_json
                    except json.JSONDecodeError:
                        print(f"INFO: Tool {tool_name} returned plain text: {result['text']}")
                        return None
                else:
                    print(f"WARNING: Unexpected tool result format for {tool_name}: {result}")
                    return None

            except httpx.RequestError as e:
                print(f"ERROR: Error connecting to MCP server for tool {tool_name}: {e}")
                return None
            except httpx.HTTPStatusError as e:
                print(f"ERROR: MCP server returned an error for tool {tool_name} with key '{key}': {e}")
                if e.response.status_code == 404:
                    return None
                if e.response.status_code == 400:
                    print(f"DEBUG: HTTP 400 for key '{key}', will try next key if available.")
                    continue
                raise
    print("ERROR: All tried keys for phone parameter resulted in 400 Bad Request.")
    return None

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=10.0)
            response.raise_for_status()

            result = response.json()
            print(f"DEBUG: Successfully called tool {tool_name}. Result type: {result.get('type')}")

            if result.get('type') == 'json' and 'json' in result:
                try:
                    return json.loads(result['json'])
                except json.JSONDecodeError:
                    print(f"ERROR: Tool {tool_name} returned invalid JSON in 'json' field: {result['json']}")
                    return None
            elif result.get('type') == 'text' and 'text' in result:
                try:
                    parsed_json = json.loads(result['text'])
                    print(f"DEBUG: Tool {tool_name} returned JSON embedded in 'text' field.")
                    return parsed_json
                except json.JSONDecodeError:
                    print(f"INFO: Tool {tool_name} returned plain text: {result['text']}")
                    return None
            else:
                print(f"WARNING: Unexpected tool result format for {tool_name}: {result}")
                return None

        except httpx.RequestError as e:
            print(f"ERROR: Error connecting to MCP server for tool {tool_name}: {e}")
            return None
        except httpx.HTTPStatusError as e:
            print(f"ERROR: MCP server returned an error for tool {tool_name}: {e}")
            if e.response.status_code == 404:
                return None
            raise

async def call_mcp_net_worth(phone: str) -> Any:
    """Calls the GetNetWorth tool for a given user."""
    return await call_mcp_tool("GetNetWorth", phone)

async def call_mcp_mf_transactions(phone: str) -> Any:
    """Calls the GetMFTransactions tool for a given user."""
    return await call_mcp_tool("GetMFTransactions", phone)

async def call_mcp_stock_transactions(phone: str) -> Any:
    """Calls the GetStockTransactions tool for a given user."""
    return await call_mcp_tool("GetStockTransactions", phone)

async def call_mcp_epf_details(phone: str) -> Any:
    """Calls the GetEPFDetails tool for a given user."""
    return await call_mcp_tool("GetEPFDetails", phone)

async def call_mcp_credit_report(phone: str) -> Any:
    """Calls the GetCreditReport tool for a given user."""
    return await call_mcp_tool("GetCreditReport", phone)

async def call_mcp_get_goals(phone: str) -> Any:
    """Calls the GetGoals tool for a given user."""
    return await call_mcp_tool("GetGoals", phone)

async def call_mcp_add_goal(phone: str, goal: dict) -> Any:
    """Calls the AddGoal tool to add a new goal for a user."""
    # The tool expects arguments: {"phoneNumber": phone, "goal": goal}
    return await call_mcp_tool("AddGoal", phone, inputs={"phoneNumber": phone, "goal": goal})

async def call_mcp_update_goal(phone: str, goal_id: str, goal_update: dict) -> Any:
    """Calls the UpdateGoal tool to update an existing goal for a user."""
    return await call_mcp_tool("UpdateGoal", phone, inputs={"phoneNumber": phone, "goal_id": goal_id, "goal_update": goal_update})

async def call_mcp_delete_goal(phone: str, goal_id: str) -> Any:
    """Calls the DeleteGoal tool to delete a goal for a user."""
    return await call_mcp_tool("DeleteGoal", phone, inputs={"phoneNumber": phone, "goal_id": goal_id})

async def fetch_from_mcp(phone: str, file: str) -> Any:
    """Fetches data for a given user from the mock server (direct file access)."""
    url = f"{FI_MCP_SERVER_URL}/user/{phone}/{file}"
    print(f"DEBUG: Direct fetching from mock server: {url}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            print(f"DEBUG: Successfully direct fetched {file} for {phone}.")
            return response.json()
        except httpx.RequestError as e:
            print(f"ERROR: Error connecting to mock server for direct fetch {url}: {e}")
            return None
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404 and file == "goals.json":
                print(f"DEBUG: {file} not found for {phone}, returning empty list.")
                return []
            print(f"ERROR: Mock server returned an error for direct fetch {url}: {e}")
            return None

async def write_to_mcp(phone: str, file: str, data: Any):
    # ... (This function remains unchanged, as it writes to local disk) ...
    if not MCP_FILE_PATH:
        print("ERROR: MCP_FILE_PATH is not set in your .env file. Cannot write goal.")
        return

    try:
        path = Path(MCP_FILE_PATH) / 'test_data_dir' / phone / file
        print(f"DEBUG: Attempting to write to: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"DEBUG: Successfully wrote to {path}")
        
    except Exception as e:
        print(f"ERROR: An error occurred while writing the file {path}: {e}")


# --- Feature 3: Subscription Detection (Modify to use new call_mcp_tool) ---
def detect_subscriptions(transactions_data: Dict) -> SubscriptionInfo:
    # This logic remains mostly the same, but the transactions_data input will now come from a tool call.
    if not transactions_data or 'bankTransactions' not in transactions_data:
        return SubscriptionInfo(total_monthly_cost=0, potential_savings=0, subscriptions=[])
    
    all_txns = []
    for bank_account in transactions_data['bankTransactions']:
        all_txns.extend(bank_account['txns'])

    df = pd.DataFrame(all_txns, columns=['amount', 'narration', 'date', 'type', 'mode', 'balance'])
    df['date'] = pd.to_datetime(df['date'])
    df = df[df['type'] == 2].copy() # Filter for debits only
    df['amount'] = pd.to_numeric(df['amount'])

    # Normalize narration to find similar transactions
    df['narration_key'] = df['narration'].str.extract(r'([a-zA-Z\s]+)')[0].str.strip().str.upper()

    subscriptions = []
    total_monthly_cost = 0
    potential_savings = 0
    
    today = datetime.strptime("2025-07-22", "%Y-%m-%d").date() # Using fixed date for consistent results

    for key, group in df.groupby('narration_key'):
        if len(group) > 1: # It's recurring if it happened more than once
            avg_cost = group['amount'].mean()
            last_paid_date = group['date'].max().date()
            days_since_last_paid = (today - last_paid_date).days
            
            status = "active"
            if days_since_last_paid > 45: # If not paid in ~1.5 months, flag it
                status = "potentially_unused"
                potential_savings += avg_cost

            subscriptions.append(Subscription(
                name=key.title(),
                last_paid_date=last_paid_date,
                estimated_monthly_cost=round(avg_cost, 2),
                transaction_count=len(group),
                status=status
            ))
            total_monthly_cost += avg_cost

    return SubscriptionInfo(
        total_monthly_cost=round(total_monthly_cost, 2),
        potential_savings=round(potential_savings, 2),
        subscriptions=sorted(subscriptions, key=lambda s: s.last_paid_date, reverse=True)
    )

# --- Feature 4: Goal Planning (Uses direct file fetch/write, not tools yet) ---
async def get_goals(phone: str) -> List[FinancialGoal]:
    """Retrieves all financial goals for a user."""
    goals_data = await fetch_from_mcp(phone, "goals.json") # Still uses direct fetch for now
    if goals_data is None: return []
    return [FinancialGoal(**goal) for goal in goals_data]

async def create_goal(phone: str, goal: FinancialGoal) -> List[FinancialGoal]:
    """Adds a new financial goal for a user."""
    all_goals = await get_goals(phone)
    all_goals.append(goal)
    goals_dict = [g.dict() for g in all_goals]
    await write_to_mcp(phone, "goals.json", goals_dict)
    return all_goals

async def update_goal(phone: str, goal_id: UUID, goal_update: FinancialGoalUpdate) -> FinancialGoal:
    """Updates an existing financial goal."""
    all_goals = await get_goals(phone)
    target_goal = None
    for i, goal in enumerate(all_goals):
        if goal.goal_id == goal_id:
            existing_goal_data = goal.dict()
            update_data = goal_update.dict(exclude_unset=True)
            merged_data = {**existing_goal_data, **update_data}
            
            all_goals[i] = FinancialGoal(**merged_data)
            target_goal = all_goals[i]
            break
    
    if not target_goal:
        raise ValueError("Goal not found")

    await write_to_mcp(phone, "goals.json", [g.dict() for g in all_goals])
    return target_goal

async def delete_goal(phone: str, goal_id: UUID) -> List[FinancialGoal]:
    """Deletes a financial goal."""
    all_goals = await get_goals(phone)
    updated_goals = [goal for goal in all_goals if goal.goal_id != goal_id]
    
    if len(all_goals) == len(updated_goals):
        raise ValueError("Goal not found")

    await write_to_mcp(phone, "goals.json", [g.dict() for g in updated_goals])
    return updated_goals

async def calculate_financial_health_score(phone_number: str) -> dict:
    """
    Calculate a comprehensive financial health score based on multiple factors
    """
    try:
        # Fetch user's financial data
        net_worth_data = await call_mcp_net_worth(phone_number)
        bank_transactions = await call_mcp_tool("GetBankTransactions", phone_number)
        credit_report = await call_mcp_credit_report(phone_number)
        mf_transactions = await call_mcp_mf_transactions(phone_number)
        stock_transactions = await call_mcp_stock_transactions(phone_number)
        
        # Initialize score components
        score_components = {
            "emergency_fund": 0,
            "debt_management": 0,
            "savings_rate": 0,
            "investment_diversification": 0,
            "credit_health": 0
        }
        
        # 1. Emergency Fund Score (0-20 points)
        if net_worth_data and "netWorthResponse" in net_worth_data:
            net_worth_str = net_worth_data["netWorthResponse"].get("totalNetWorthValue", {}).get("units", "0")
            net_worth = float(net_worth_str) if isinstance(net_worth_str, str) else float(net_worth_str or 0)
            if bank_transactions:
                # Estimate monthly expenses from transactions
                monthly_expenses = 50000  # Default estimate
                emergency_fund_ratio = net_worth / (monthly_expenses * 6) if monthly_expenses > 0 else 0
                if emergency_fund_ratio >= 1:
                    score_components["emergency_fund"] = 20
                elif emergency_fund_ratio >= 0.5:
                    score_components["emergency_fund"] = 15
                elif emergency_fund_ratio >= 0.25:
                    score_components["emergency_fund"] = 10
                else:
                    score_components["emergency_fund"] = 5
        
        # 2. Debt Management Score (0-20 points)
        if credit_report and "creditReportResponse" in credit_report:
            credit_data = credit_report["creditReportResponse"]
            active_loans = credit_data.get("activeLoans", [])
            if not active_loans:
                score_components["debt_management"] = 20
            elif len(active_loans) <= 2:
                score_components["debt_management"] = 15
            elif len(active_loans) <= 4:
                score_components["debt_management"] = 10
            else:
                score_components["debt_management"] = 5
        
        # 3. Savings Rate Score (0-20 points)
        if bank_transactions and mf_transactions:
            # Calculate savings rate (simplified)
            total_investments = len(mf_transactions.get("mfTransactionsResponse", {}).get("transactions", []))
            if total_investments > 10:
                score_components["savings_rate"] = 20
            elif total_investments > 5:
                score_components["savings_rate"] = 15
            elif total_investments > 2:
                score_components["savings_rate"] = 10
            else:
                score_components["savings_rate"] = 5
        
        # 4. Investment Diversification Score (0-20 points)
        investment_types = 0
        if mf_transactions:
            investment_types += 1
        if stock_transactions:
            investment_types += 1
        if net_worth_data and net_worth_data.get("netWorthResponse", {}).get("epfDetails"):
            investment_types += 1
        
        if investment_types >= 3:
            score_components["investment_diversification"] = 20
        elif investment_types == 2:
            score_components["investment_diversification"] = 15
        elif investment_types == 1:
            score_components["investment_diversification"] = 10
        else:
            score_components["investment_diversification"] = 5
        
        # 5. Credit Health Score (0-20 points)
        if credit_report and "creditReportResponse" in credit_report:
            credit_data = credit_report["creditReportResponse"]
            credit_score = credit_data.get("creditScore", 0)
            if credit_score >= 750:
                score_components["credit_health"] = 20
            elif credit_score >= 650:
                score_components["credit_health"] = 15
            elif credit_score >= 550:
                score_components["credit_health"] = 10
            else:
                score_components["credit_health"] = 5
        
        # Calculate total score
        total_score = sum(score_components.values())
        
        # Determine health level
        if total_score >= 80:
            health_level = "Excellent"
            feedback = "Outstanding! You're managing your finances exceptionally well."
        elif total_score >= 60:
            health_level = "Good"
            feedback = "Good! You're on track with most goals."
        elif total_score >= 40:
            health_level = "Fair"
            feedback = "Fair. There's room for improvement in several areas."
        else:
            health_level = "Poor"
            feedback = "Needs attention. Consider focusing on building emergency funds and reducing debt."
        
        return {
            "score": total_score,
            "health_level": health_level,
            "feedback": feedback,
            "components": score_components,
            "max_score": 100
        }
        
    except Exception as e:
        print(f"Error calculating financial health score: {e}")
        return {
            "score": 50,
            "health_level": "Unknown",
            "feedback": "Unable to calculate score due to data issues.",
            "components": {},
            "max_score": 100
        }

async def get_detailed_financial_analysis(phone_number: str) -> dict:
    """
    Get detailed financial analysis with breakdowns and recommendations
    """
    try:
        # Fetch all financial data
        net_worth_data = await call_mcp_net_worth(phone_number)
        bank_transactions = await call_mcp_tool("GetBankTransactions", phone_number)
        credit_report = await call_mcp_credit_report(phone_number)
        mf_transactions = await call_mcp_mf_transactions(phone_number)
        stock_transactions = await call_mcp_stock_transactions(phone_number)
        epf_details = await call_mcp_epf_details(phone_number)
        
        # Calculate score components
        score_data = await calculate_financial_health_score(phone_number)
        
        # Prepare detailed analysis
        analysis = {
            "overview": {
                "total_net_worth": net_worth_data.get("netWorthResponse", {}).get("totalNetWorthValue", {}).get("units", "0"),
                "financial_health_score": score_data.get("score", 0),
                "health_level": score_data.get("health_level", "Unknown")
            },
            "components": {
                "emergency_fund": {
                    "score": score_data.get("components", {}).get("emergency_fund", 0),
                    "max_score": 20,
                    "description": "Measures if you have 6+ months of expenses saved",
                    "recommendation": "Aim to save 6-12 months of living expenses in a liquid account"
                },
                "debt_management": {
                    "score": score_data.get("components", {}).get("debt_management", 0),
                    "max_score": 20,
                    "description": "Evaluates your current debt load and management",
                    "recommendation": "Keep debt-to-income ratio below 40% and prioritize high-interest debt"
                },
                "savings_rate": {
                    "score": score_data.get("components", {}).get("savings_rate", 0),
                    "max_score": 20,
                    "description": "Assesses your regular savings and investment contributions",
                    "recommendation": "Save at least 20% of your income, including retirement contributions"
                },
                "investment_diversification": {
                    "score": score_data.get("components", {}).get("investment_diversification", 0),
                    "max_score": 20,
                    "description": "Evaluates portfolio diversification across asset classes",
                    "recommendation": "Diversify across stocks, bonds, real estate, and other assets"
                },
                "credit_health": {
                    "score": score_data.get("components", {}).get("credit_health", 0),
                    "max_score": 20,
                    "description": "Measures your credit score and credit history",
                    "recommendation": "Maintain a credit score above 750 and keep credit utilization low"
                }
            },
            "recommendations": [
                "Build an emergency fund covering 6-12 months of expenses",
                "Increase your monthly savings rate to at least 20%",
                "Diversify your investment portfolio across different asset classes",
                "Monitor and improve your credit score regularly",
                "Consider consulting a financial advisor for personalized advice"
            ],
            "data_summary": {
                "total_transactions": len(bank_transactions.get("bankTransactionsResponse", {}).get("transactions", [])),
                "investment_count": len(mf_transactions.get("mfTransactionsResponse", {}).get("transactions", [])),
                "stock_count": len(stock_transactions.get("stockTransactionsResponse", {}).get("transactions", [])),
                "active_loans": len(credit_report.get("creditReportResponse", {}).get("activeLoans", []))
            }
        }
        
        return analysis
        
    except Exception as e:
        print(f"Error getting detailed financial analysis: {e}")
        return {
            "error": "Unable to generate detailed analysis due to data issues.",
            "overview": {
                "total_net_worth": "0",
                "financial_health_score": 50,
                "health_level": "Unknown"
            }
        }