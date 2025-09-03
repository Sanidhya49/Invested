#!/usr/bin/env python3
"""
Test script for AI Agents integration
"""

import asyncio
import sys
import os

# Add the agents directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))

async def test_agent_imports():
    """Test that all agent modules can be imported"""
    print("🧪 Testing AI Agents Import...")
    
    try:
        from oracle import process_oracle_query
        print("✅ Oracle agent imported successfully")
    except Exception as e:
        print(f"❌ Oracle agent import failed: {e}")
        return False
    
    try:
        from guardian import run_guardian_analysis
        print("✅ Guardian agent imported successfully")
    except Exception as e:
        print(f"❌ Guardian agent import failed: {e}")
        return False
    
    try:
        from catalyst import run_catalyst_analysis
        print("✅ Catalyst agent imported successfully")
    except Exception as e:
        print(f"❌ Catalyst agent import failed: {e}")
        return False
    
    try:
        from strategist import run_strategist_analysis
        print("✅ Strategist agent imported successfully")
    except Exception as e:
        print(f"❌ Strategist agent import failed: {e}")
        return False
    
    return True

async def test_router_import():
    """Test that the agents router can be imported"""
    print("\n🧪 Testing Agents Router Import...")
    
    try:
        # Add the invested-backend directory to the path
        sys.path.append(os.path.join(os.path.dirname(__file__), 'invested-backend'))
        from routers.agents import router
        print("✅ Agents router imported successfully")
        return True
    except Exception as e:
        print(f"❌ Agents router import failed: {e}")
        return False

def test_frontend_components():
    """Test that frontend components exist"""
    print("\n🧪 Testing Frontend Components...")
    
    components_to_check = [
        "invested-frontend-webapp/src/components/AIAgentsPanel.js",
        "invested-frontend-webapp/src/utils/api.js"
    ]
    
    all_exist = True
    for component in components_to_check:
        if os.path.exists(component):
            print(f"✅ {component} exists")
        else:
            print(f"❌ {component} missing")
            all_exist = False
    
    return all_exist

async def main():
    """Run all tests"""
    print("🚀 Starting AI Agents Integration Tests...\n")
    
    # Test agent imports
    agents_ok = await test_agent_imports()
    
    # Test router import
    router_ok = await test_router_import()
    
    # Test frontend components
    frontend_ok = test_frontend_components()
    
    print("\n" + "="*50)
    print("📊 Test Results Summary:")
    print(f"   Agents Import: {'✅ PASS' if agents_ok else '❌ FAIL'}")
    print(f"   Router Import: {'✅ PASS' if router_ok else '❌ FAIL'}")
    print(f"   Frontend Components: {'✅ PASS' if frontend_ok else '❌ FAIL'}")
    
    if all([agents_ok, router_ok, frontend_ok]):
        print("\n🎉 All tests passed! AI Agents integration is ready.")
        print("\n📝 Next steps:")
        print("   1. Start the backend: cd invested-backend && python main.py")
        print("   2. Start the frontend: cd invested-frontend-webapp && npm start")
        print("   3. Navigate to the Dashboard to see the AI Agents panel")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
    
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main()) 