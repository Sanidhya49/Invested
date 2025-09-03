#!/usr/bin/env python3
"""
Test script for AI Agents with user 2222222222
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER = "2222222222"

def get_jwt_token():
    """Get JWT token for the test user"""
    try:
        # Login to get JWT token
        login_data = {
            "username": TEST_USER,
            "password": "password123"  # Default password
        }
        
        response = requests.post(f"{BASE_URL}/login", data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get("access_token")
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error getting JWT token: {e}")
        return None

def get_firebase_token(jwt_token):
    """Get Firebase token from backend bridge"""
    try:
        headers = {"Authorization": f"Bearer {jwt_token}"}
        response = requests.post(f"{BASE_URL}/bridge/firebase-token", headers=headers)
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get("firebase_token")
        else:
            print(f"❌ Firebase token failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error getting Firebase token: {e}")
        return None

def test_agent(agent_name, endpoint, method="GET", data=None, firebase_token=None):
    """Test a specific agent"""
    print(f"\n🧪 Testing {agent_name} Agent...")
    
    headers = {"Content-Type": "application/json"}
    if firebase_token:
        headers["Authorization"] = f"Bearer {firebase_token}"
    
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        else:
            response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json=data)
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {agent_name} Agent Success!")
            print(f"📊 Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ {agent_name} Agent Failed: {response.status_code}")
            print(f"📄 Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ {agent_name} Agent Error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting AI Agents Test for User 2222222222")
    print("=" * 60)
    
    # Step 1: Get JWT token
    print("\n🔑 Step 1: Getting JWT token...")
    jwt_token = get_jwt_token()
    if not jwt_token:
        print("❌ Cannot proceed without JWT token")
        return
    
    print("✅ JWT token obtained")
    
    # Step 2: Get Firebase token
    print("\n🔥 Step 2: Getting Firebase token...")
    firebase_token = get_firebase_token(jwt_token)
    if not firebase_token:
        print("❌ Cannot proceed without Firebase token")
        return
    
    print("✅ Firebase token obtained")
    
    # Step 3: Test all agents
    print("\n🤖 Step 3: Testing all AI Agents...")
    
    agents_to_test = [
        {
            "name": "Oracle",
            "endpoint": "/agents/oracle/chat",
            "method": "POST",
            "data": {"question": "What is my current financial health and what should I focus on?"}
        },
        {
            "name": "Guardian",
            "endpoint": "/agents/guardian/alerts",
            "method": "GET"
        },
        {
            "name": "Catalyst",
            "endpoint": "/agents/catalyst/tips",
            "method": "GET"
        },
        {
            "name": "Strategist",
            "endpoint": "/agents/strategist/portfolio",
            "method": "GET"
        }
    ]
    
    results = {}
    
    for agent in agents_to_test:
        success = test_agent(
            agent["name"],
            agent["endpoint"],
            agent["method"],
            agent.get("data"),
            firebase_token
        )
        results[agent["name"]] = success
        time.sleep(1)  # Small delay between requests
    
    # Step 4: Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    for agent_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {agent_name}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    failed_tests = total_tests - passed_tests
    
    print(f"\n📈 Overall Results:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {failed_tests}")
    print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests == 0:
        print("\n🎉 All agents are working perfectly!")
    else:
        print(f"\n⚠️ {failed_tests} agent(s) need attention")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main() 