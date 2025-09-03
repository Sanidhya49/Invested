from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor

def generate_summary_pdf(net_worth_data: dict, goals_data: list = None) -> BytesIO:
    """Generates a comprehensive PDF summary of user's financial data"""
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # --- Header ---
    p.setFont("Helvetica-Bold", 24)
    p.setFillColor(HexColor("#1A237E"))
    p.drawString(inch, height - inch, "INVESTED - Comprehensive Financial Summary")
    
    # Subtitle
    p.setFont("Helvetica", 14)
    p.setFillColorRGB(0, 0, 0)
    p.drawString(inch, height - 1.3 * inch, "Your Complete Financial Intelligence Report")
    
    # Date
    from datetime import datetime
    p.setFont("Helvetica", 12)
    p.drawString(inch, height - 1.5 * inch, f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")

    # --- Executive Summary ---
    y_pos = height - 2 * inch
    p.setFont("Helvetica-Bold", 16)
    p.setFillColor(HexColor("#3F51B5"))
    p.drawString(inch, y_pos, "Executive Summary")
    p.line(inch, y_pos - 0.1 * inch, width - inch, y_pos - 0.1 * inch)

    p.setFont("Helvetica", 12)
    p.setFillColorRGB(0, 0, 0)
    y_pos -= 0.3 * inch
    p.drawString(inch, y_pos, "INVESTED is your AI-powered financial companion that helps you:")
    y_pos -= 0.25 * inch
    p.drawString(1.2 * inch, y_pos, "• Track your net worth and financial health score")
    y_pos -= 0.2 * inch
    p.drawString(1.2 * inch, y_pos, "• Get AI-powered insights from Oracle, Guardian, Catalyst, and Strategist")
    y_pos -= 0.2 * inch
    p.drawString(1.2 * inch, y_pos, "• Set and monitor financial goals")
    y_pos -= 0.2 * inch
    p.drawString(1.2 * inch, y_pos, "• Analyze investments and portfolio performance")
    y_pos -= 0.2 * inch
    p.drawString(1.2 * inch, y_pos, "• Detect anomalies and security threats")
    y_pos -= 0.2 * inch
    p.drawString(1.2 * inch, y_pos, "• Receive personalized growth recommendations")

    # --- Net Worth Section ---
    y_pos -= 0.4 * inch
    p.setFont("Helvetica-Bold", 16)
    p.setFillColor(HexColor("#3F51B5"))
    p.drawString(inch, y_pos, "Net Worth Overview")
    p.line(inch, y_pos - 0.1 * inch, width - inch, y_pos - 0.1 * inch)

    p.setFont("Helvetica", 12)
    p.setFillColorRGB(0, 0, 0)
    y_pos -= 0.3 * inch
    
    if net_worth_data and "netWorthResponse" in net_worth_data:
        total_net_worth = net_worth_data["netWorthResponse"].get("totalNetWorthValue", {}).get("units", "0")
        p.drawString(inch, y_pos, f"Total Net Worth: ₹ {int(total_net_worth):,}")
        
        # Add net worth breakdown if available
        net_worth_details = net_worth_data["netWorthResponse"]
        y_pos -= 0.4 * inch
        p.setFont("Helvetica-Bold", 14)
        p.drawString(inch, y_pos, "Asset Breakdown:")
        
        p.setFont("Helvetica", 12)
        if "bankAccounts" in net_worth_details:
            y_pos -= 0.25 * inch
            bank_value = net_worth_details['bankAccounts'].get('totalValue', {}).get('units', '0')
            p.drawString(1.2 * inch, y_pos, f"• Bank Accounts: ₹ {int(bank_value):,}")
        
        if "investments" in net_worth_details:
            y_pos -= 0.25 * inch
            inv_value = net_worth_details['investments'].get('totalValue', {}).get('units', '0')
            p.drawString(1.2 * inch, y_pos, f"• Investments: ₹ {int(inv_value):,}")
        
        if "epfDetails" in net_worth_details:
            y_pos -= 0.25 * inch
            epf_value = net_worth_details['epfDetails'].get('totalBalance', {}).get('units', '0')
            p.drawString(1.2 * inch, y_pos, f"• EPF: ₹ {int(epf_value):,}")

    # --- Goals Section ---
    y_pos -= 0.4 * inch
    p.setFont("Helvetica-Bold", 16)
    p.setFillColor(HexColor("#3F51B5"))
    p.drawString(inch, y_pos, "Financial Goals Progress")
    p.line(inch, y_pos - 0.1 * inch, width - inch, y_pos - 0.1 * inch)
    
    if goals_data:
        p.setFont("Helvetica", 12)
        p.setFillColorRGB(0, 0, 0)
        y_pos -= 0.3 * inch
        for i, goal in enumerate(goals_data[:5]):  # Show first 5 goals
            if y_pos < 1.5 * inch:  # Start new page if needed
                p.showPage()
                y_pos = height - inch
                p.setFont("Helvetica-Bold", 16)
                p.setFillColor(HexColor("#3F51B5"))
                p.drawString(inch, y_pos, "Financial Goals Progress (Continued)")
                y_pos -= 0.3 * inch
                p.setFont("Helvetica", 12)
                p.setFillColorRGB(0, 0, 0)
            
            # Convert Pydantic model to dict if needed
            if hasattr(goal, 'dict'):
                goal_dict = goal.dict()
            else:
                goal_dict = goal
            
            current = goal_dict.get('current_amount', 0)
            target = goal_dict.get('target_amount', 0)
            progress = (current / target * 100) if target > 0 else 0
            p.drawString(inch, y_pos, f"• {goal_dict.get('title', 'Goal')}: ₹ {current:,} / ₹ {target:,} ({progress:.1f}%)")
            y_pos -= 0.25 * inch

    # --- AI Features Section ---
    y_pos -= 0.3 * inch
    p.setFont("Helvetica-Bold", 16)
    p.setFillColor(HexColor("#3F51B5"))
    p.drawString(inch, y_pos, "AI-Powered Features Available")
    p.line(inch, y_pos - 0.1 * inch, width - inch, y_pos - 0.1 * inch)
    
    p.setFont("Helvetica", 12)
    p.setFillColorRGB(0, 0, 0)
    y_pos -= 0.3 * inch
    p.drawString(inch, y_pos, "🧙 Oracle: AI-powered financial advice and tax planning")
    y_pos -= 0.2 * inch
    p.drawString(inch, y_pos, "🛡️ Guardian: Anomaly detection and security monitoring")
    y_pos -= 0.2 * inch
    p.drawString(inch, y_pos, "🚀 Catalyst: Growth insights and investment opportunities")
    y_pos -= 0.2 * inch
    p.drawString(inch, y_pos, "📊 Strategist: Portfolio analysis and stock recommendations")
    
    # --- Footer ---
    y_pos -= 0.6 * inch
    p.setFont("Helvetica-Bold", 12)
    p.setFillColor(HexColor("#1A237E"))
    p.drawString(inch, y_pos, "INVESTED - Let AI Talk to Your Money")
    p.setFont("Helvetica", 10)
    p.setFillColorRGB(0, 0, 0)
    p.drawString(inch, y_pos - 0.2 * inch, "Your comprehensive financial intelligence platform")

    p.save()
    buffer.seek(0)
    return buffer