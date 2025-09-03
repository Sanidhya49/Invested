#!/usr/bin/env python3
"""
Phone Number Switcher for Invested Project
Easily switch between different test phone numbers for testing various scenarios.
"""

import os
import sys

# Available test phone numbers with descriptions
PHONE_NUMBERS = {
    "9999999999": "Default - Basic transactions with some subscriptions",
    "8888888888": "Rich subscriptions - Many streaming services and gym",
    "2222222222": "Investment focused - More MF and stock transactions",
    "1010101010": "Basic user - Simple transactions",
    "1111111111": "Credit card heavy - More credit transactions",
    "1212121212": "Salary focused - Regular income patterns",
    "1313131313": "Mixed portfolio - Balanced transactions",
    "1414141414": "Conservative - Low risk transactions",
    "2020202020": "High spender - Large transactions",
    "2121212121": "Student - Limited income",
    "2525252525": "Business owner - Business transactions",
    "3333333333": "Retirement focused - EPF heavy",
    "4444444444": "Young professional - Growth investments",
    "5555555555": "Family oriented - Child expenses",
    "6666666666": "Debt heavy - Loan payments",
    "7777777777": "Savings focused - High savings rate",
    "9999999999": "Default - Basic transactions"
}

def update_phone_number(new_phone):
    """Update phone number in all relevant files"""
    
    print(f"🔄 Switching to phone number: {new_phone}")
    print(f"📝 Description: {PHONE_NUMBERS.get(new_phone, 'No description available')}")
    
    # Update agents/main.py
    try:
        with open("agents/main.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Replace all instances of phone numbers
        import re
        content = re.sub(r'phoneNumber":\s*"[0-9]+"', f'phoneNumber": "{new_phone}"', content)
        
        with open("agents/main.py", "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ Updated agents/main.py")
    except Exception as e:
        print(f"❌ Failed to update agents/main.py: {e}")
    
    # Update fi-mcp-dev/main.go
    try:
        with open("fi-mcp-dev/main.go", "r", encoding="utf-8") as f:
            content = f.read()
        
        content = re.sub(r'phoneNumber := "[0-9]+"', f'phoneNumber := "{new_phone}"', content)
        
        with open("fi-mcp-dev/main.go", "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ Updated fi-mcp-dev/main.go")
    except Exception as e:
        print(f"❌ Failed to update fi-mcp-dev/main.go: {e}")
    
    # Update backend environment variable
    try:
        with open("invested-backend/main.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        content = re.sub(r'MCP_AUTH_PHONE_NUMBER = os\.getenv\("MCP_AUTH_PHONE_NUMBER", "[0-9]+"\)', 
                        f'MCP_AUTH_PHONE_NUMBER = os.getenv("MCP_AUTH_PHONE_NUMBER", "{new_phone}")', content)
        
        with open("invested-backend/main.py", "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ Updated invested-backend/main.py")
    except Exception as e:
        print(f"❌ Failed to update invested-backend/main.py: {e}")
    
    print(f"\n🎉 Successfully switched to phone number: {new_phone}")
    print("🔄 Please restart your servers to apply changes:")
    print("   1. Stop all servers (Ctrl+C)")
    print("   2. Restart MCP server: cd fi-mcp-dev && go run .")
    print("   3. Restart agents server: cd agents && uvicorn main:app --reload --port 8001")
    print("   4. Restart backend server: cd invested-backend && uvicorn main:app --reload")

def show_available_numbers():
    """Show all available phone numbers"""
    print("📱 Available Test Phone Numbers:")
    print("=" * 50)
    for phone, desc in PHONE_NUMBERS.items():
        print(f"  {phone}: {desc}")
    print("=" * 50)

def main():
    if len(sys.argv) < 2:
        print("🔧 Phone Number Switcher for Invested Project")
        print("Usage: python switch_phone.py <phone_number>")
        print("       python switch_phone.py --list")
        print()
        show_available_numbers()
        return
    
    if sys.argv[1] == "--list":
        show_available_numbers()
        return
    
    phone = sys.argv[1]
    
    if phone not in PHONE_NUMBERS:
        print(f"❌ Error: Phone number '{phone}' not found in available options.")
        print("Use 'python switch_phone.py --list' to see available numbers.")
        return
    
    update_phone_number(phone)

if __name__ == "__main__":
    main() 