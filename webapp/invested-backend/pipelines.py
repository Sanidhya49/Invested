# pipelines.py
import pandas as pd
from typing import List, Dict

def categorize_transaction(description: str) -> str:
    """A simple function to categorize transactions based on keywords."""
    desc = description.lower()
    if any(keyword in desc for keyword in ['zomato', 'swiggy']):
        return 'Food & Dining'
    if 'salary' in desc:
        return 'Income'
    if 'uber' in desc:
        return 'Transport'
    if 'netflix' in desc:
        return 'Entertainment'
    if 'sip' in desc or 'mutual fund' in desc:
        return 'Investments'
    if 'rent' in desc:
        return 'Rent & Utilities'
    if 'groceries' in desc:
        return 'Groceries'
    return 'Other'

def process_transactions(transactions_data: List[Dict]) -> pd.DataFrame:
    """
    Takes raw transaction data, cleans it, categorizes it, and returns a DataFrame.
    """
    if not transactions_data:
        return pd.DataFrame()

    df = pd.DataFrame(transactions_data)
    df['date'] = pd.to_datetime(df['date'])
    df['category'] = df['narration'].apply(categorize_transaction) # Changed 'description' to 'narration' based on fetch_bank_transactions.json
    return df

def calculate_financial_health_score(transactions_df: pd.DataFrame, investments_data: Dict, emergency_fund_progress: float = 0.0) -> Dict:
    """
    Calculates a financial health score based on savings, investments, and emergency fund.
    """
    score = 0
    breakdown = {}

    # --- 1. Savings Rate (Max 40 points) ---
    # Ensure 'type' is correctly mapped to 'CREDIT'/'DEBIT' in process_transactions
    income = transactions_df[transactions_df['type'] == 'CREDIT']['amount'].sum()
    spending = transactions_df[transactions_df['type'] == 'DEBIT']['amount'].sum()
    
    savings_rate = 0
    if income > 0:
        savings_rate = (income - spending) / income

    score_savings = 0
    if savings_rate > 0.20:
        score_savings = 40
    elif savings_rate > 0.10:
        score_savings = 25
    else:
        score_savings = 10
    score += score_savings
    breakdown['savings_score'] = score_savings

    # --- 2. Emergency Fund (Max 30 points) ---
    score_emergency_fund = 0
    if emergency_fund_progress > 0.9:
        score_emergency_fund = 30
    elif emergency_fund_progress > 0.5:
        score_emergency_fund = 20
    else:
        score_emergency_fund = 5
    score += score_emergency_fund
    breakdown['emergency_fund_score'] = score_emergency_fund


    # --- 3. Investment Level (Max 30 points) ---
    total_investments = investments_data.get('total_value', 0)
    annual_income = income * 12
    
    investment_ratio = 0
    if annual_income > 0:
        investment_ratio = total_investments / annual_income

    score_investment = 0
    if investment_ratio > 1:
        score_investment = 30
    elif investment_ratio > 0.5:
        score_investment = 20
    else:
        score_investment = 10
    score += score_investment
    breakdown['investment_score'] = score_investment

    breakdown['total_score'] = score
    return breakdown