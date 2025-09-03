# main.py (REFACTORED VERSION with Modular Agents)

from fastapi import FastAPI, Depends, HTTPException, Header, Body
import firebase_admin
from firebase_admin import credentials, auth, firestore, messaging
import os
import uuid
import httpx
import json
from fastapi.responses import JSONResponse
import traceback
import asyncio
import jwt
from datetime import datetime

# Import Vertex AI
import vertexai

# Import agent modules
try:
    from oracle import process_oracle_query
    from guardian import run_guardian_analysis
    from catalyst import run_catalyst_analysis
    from strategist import run_strategist_analysis
except ImportError as e:
    print(f"Warning: Could not import agent modules: {e}")
    # Create dummy functions
    async def process_oracle_query(uid: str, question: str):
        return {"question": question, "answer": "Oracle agent not available"}
    async def run_guardian_analysis(uid: str):
        return {"alerts": "Guardian agent not available"}
    async def run_catalyst_analysis(uid: str):
        return {"opportunities": "Catalyst agent not available"}
    async def run_strategist_analysis(uid: str):
        return {"strategy": "Strategist agent not available"}

# Import shared utilities
try:
    from shared_utils import (
        get_user_financial_data,
        get_cached_mcp_data,
        force_json_safe,
        MOCK_SERVER_BASE_URL
    )
except ImportError as e:
    print(f"Warning: Could not import shared_utils: {e}")
    MOCK_SERVER_BASE_URL = "http://localhost:8080"
    
    async def get_user_financial_data(uid: str, tool_name: str):
        return {"error": f"Mock data for {tool_name}"}
    
    async def get_cached_mcp_data(uid: str):
        return None
    
    def force_json_safe(data):
        return {"mock_data": True, "timestamp": "2024-01-01T00:00:00"}

app = FastAPI()

# Add CORS middleware for frontend integration
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Initializations ---
# You can change this to your own service account key file
FIREBASE_CREDENTIALS_FILE = os.getenv("FIREBASE_CREDENTIALS_FILE", "invested-hackathon-firebase-adminsdk-fbsvc-38735ba923.json")
cred = credentials.Certificate(FIREBASE_CREDENTIALS_FILE)
firebase_admin.initialize_app(cred)
SERVICE_ACCOUNT_KEY_PATH = os.path.join(os.path.dirname(__file__), "invested-hackathon-vertex-ai-key.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_KEY_PATH
GCP_PROJECT_ID = "invested-hackathon"
GCP_LOCATION = "us-central1"
vertexai.init(project=GCP_PROJECT_ID, location=GCP_LOCATION)

# --- Authentication ---
async def verify_firebase_token(authorization: str = Header(...)):
    try:
        id_token = authorization.split(" ").pop()
        
        # Try Firebase verification first
        try:
            decoded_token = await asyncio.to_thread(auth.verify_id_token, id_token)
            return decoded_token['uid']
        except Exception:
            # Fallback: try to decode as JWT bridge token
            try:
                # Use a simple secret for demo (should match invested-backend SECRET_KEY)
                decoded_token = jwt.decode(id_token, "supersecretkey", algorithms=["HS256"])
                return decoded_token.get('uid') or decoded_token.get('phone_number')
            except Exception:
                raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Firebase token")

@app.get("/start-fi-auth")
async def start_fi_auth(uid: str = Depends(verify_firebase_token)):
    session_id = str(uuid.uuid4())
    
    # First, create session with MCP server
    try:
        async with httpx.AsyncClient() as client:
            # Step 1: Create session
            response1 = await client.get(f"{MOCK_SERVER_BASE_URL}/mockWebPage?sessionId={session_id}")
            if response1.status_code != 200:
                print(f"❌ Failed to create MCP session: {response1.status_code}")
                raise HTTPException(status_code=500, detail="Failed to create MCP session")
            
            # Step 2: Login with session
            response2 = await client.post(
                f"{MOCK_SERVER_BASE_URL}/login",
                data={"sessionId": session_id, "phoneNumber": "8888888888"}
            )
            if response2.status_code != 200:
                print(f"❌ Failed to login to MCP server: {response2.status_code}")
                raise HTTPException(status_code=500, detail="Failed to login to MCP server")
            
            print(f"✅ Successfully created and logged into MCP session: {session_id}")
    except Exception as e:
        print(f"❌ Error setting up MCP session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to setup MCP session: {e}")
    
    # Store session ID in Firestore
    db = firestore.client()
    user_doc_ref = db.collection("users").document(uid)
    await asyncio.to_thread(user_doc_ref.set, {"fi_session_id": session_id}, merge=True)
    
    auth_url = f"{MOCK_SERVER_BASE_URL}/mockWebPage?sessionId={session_id}"
    return {"auth_url": auth_url, "session_id": session_id}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/test-firestore")
async def test_firestore():
    """Test Firestore connectivity"""
    try:
        db = firestore.client()
        
        # Try to read from a test document
        test_doc = await asyncio.to_thread(db.collection("test").document("connection").get)
        
        # Try to write a test document
        await asyncio.to_thread(
            db.collection("test").document("connection").set,
            {"timestamp": datetime.utcnow().isoformat(), "status": "connected"}
        )
        
        return {
            "status": "success",
            "message": "Firestore connection working",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Firestore connection error: {e}")
        return {
            "status": "error",
            "message": f"Firestore connection failed: {e}",
            "timestamp": datetime.utcnow().isoformat()
        }

@app.post("/test-data-fetch")
async def test_data_fetch(uid: str = Depends(verify_firebase_token)):
    """Test endpoint to manually trigger data fetching and see what happens"""
    print(f"🔍 TEST: Starting manual data fetch test for user {uid}")
    
    # Check if user has session
    db = firestore.client()
    user_doc = await asyncio.to_thread(db.collection("users").document(uid).get)
    if not user_doc.exists:
        return {"error": "User document not found"}
    
    user_data = user_doc.to_dict()
    session_id = user_data.get("fi_session_id")
    
    if not session_id:
        return {"error": "No session ID found. Please authenticate first."}
    
    print(f"🔍 TEST: Using session ID: {session_id}")
    
    # Test single data fetch
    print(f"🔍 TEST: Fetching bank transactions...")
    bank_tx = await get_user_financial_data(uid, tool_name="fetch_bank_transactions")
    
    print(f"🔍 TEST: Bank transactions result: {bank_tx}")
    
    return {
        "session_id": session_id,
        "bank_transactions": bank_tx,
        "user_exists": user_doc.exists,
        "has_session": bool(session_id)
    }

@app.post("/clear-cache")
async def clear_cache(uid: str = Depends(verify_firebase_token)):
    """Clear the MCP data cache for a user to force fresh data fetching"""
    try:
        db = firestore.client()
        user_doc_ref = db.collection("users").document(uid)
        
        # Remove the mcp_data_cache field
        await asyncio.to_thread(user_doc_ref.update, {"mcp_data_cache": None})
        
        print(f"✅ Cleared cache for user {uid}")
        return {"status": "success", "message": "Cache cleared successfully"}
        
    except Exception as e:
        print(f"❌ Error clearing cache: {e}")
        return {"status": "error", "message": f"Failed to clear cache: {e}"}

@app.post("/setup-mcp-session")
async def setup_mcp_session(uid: str = Depends(verify_firebase_token)):
    """Setup MCP session for a user if they don't have one"""
    try:
        db = firestore.client()
        user_doc = await asyncio.to_thread(db.collection("users").document(uid).get)
        
        if user_doc.exists and "fi_session_id" in user_doc.to_dict():
            session_id = user_doc.to_dict()["fi_session_id"]
            return {"status": "success", "message": "Session already exists", "session_id": session_id}
        
        # Create new session
        session_id = str(uuid.uuid4())
        
        # Setup session with MCP server
        async with httpx.AsyncClient() as client:
            # Step 1: Create session
            response1 = await client.get(f"{MOCK_SERVER_BASE_URL}/mockWebPage?sessionId={session_id}")
            if response1.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to create MCP session")
            
            # Step 2: Login with session
            response2 = await client.post(
                f"{MOCK_SERVER_BASE_URL}/login",
                data={"sessionId": session_id, "phoneNumber": "9999999999"}
            )
            if response2.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to login to MCP server")
        
        # Store session ID in Firestore
        user_doc_ref = db.collection("users").document(uid)
        await asyncio.to_thread(user_doc_ref.set, {"fi_session_id": session_id}, merge=True)
        
        return {"status": "success", "message": "MCP session created successfully", "session_id": session_id}
        
    except Exception as e:
        print(f"❌ Error setting up MCP session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to setup MCP session: {e}")

@app.get("/test-fcm")
async def test_fcm():
    """Test FCM configuration"""
    try:
        # Test if Firebase Admin SDK is properly initialized
        print("🔍 Testing FCM configuration...")
        
        # Try to create a test message (won't send it)
        test_message = messaging.Message(
            notification=messaging.Notification(
                title="Test",
                body="Test message"
            ),
            token="test_token"
        )
        
        print("✅ FCM configuration is working")
        return {"status": "FCM is properly configured"}
        
    except Exception as e:
        print(f"❌ FCM configuration error: {e}")
        return {"status": "FCM configuration error", "error": str(e)}

# --- Prefetch Data Endpoint ---
@app.post("/prefetch-data")
async def prefetch_data(uid: str = Depends(verify_firebase_token)):
    db = firestore.client()
    # Fetch all MCP data types in parallel
    net_worth, bank_tx, credit, epf, mf_tx, stock_tx = await asyncio.gather(
        get_user_financial_data(uid, tool_name="fetch_net_worth"),
        get_user_financial_data(uid, tool_name="fetch_bank_transactions"),
        get_user_financial_data(uid, tool_name="fetch_credit_report"),
        get_user_financial_data(uid, tool_name="fetch_epf_details"),
        get_user_financial_data(uid, tool_name="fetch_mf_transactions"),
        get_user_financial_data(uid, tool_name="fetch_stock_transactions")
    )
    mcp_data = {
        "net_worth": net_worth,
        "bank_transactions": bank_tx,
        "credit_report": credit,
        "epf_details": epf,
        "mf_transactions": mf_tx,
        "stock_transactions": stock_tx,
        "mcp_cache_timestamp": datetime.utcnow().isoformat()
    }
    safe_mcp_data = force_json_safe(mcp_data)
    
    # Try to save to Firestore with error handling
    try:
        await asyncio.to_thread(db.collection("users").document(uid).set, {"mcp_data_cache": safe_mcp_data}, merge=True)
        print("✅ SUCCESS: MCP data cached in Firestore")
    except Exception as e:
        print(f"❌ WARNING: Failed to cache MCP data in Firestore: {e}")
        # Continue without caching - the app will still work
    
    return {"status": "prefetched", "mcp_data": safe_mcp_data}

# --- Agent Endpoints ---
@app.post("/ask-oracle")
async def ask_oracle(uid: str = Depends(verify_firebase_token), body: dict = Body(...)):
    """Oracle Agent - AI-powered personal finance assistant"""
    question = body.get("question", "")
    return await process_oracle_query(uid, question)

@app.post("/run-guardian")
async def run_guardian(uid: str = Depends(verify_firebase_token), body: dict = Body(None)):
    """Guardian Agent - AI financial safety agent"""
    return await run_guardian_analysis(uid)

@app.post("/run-catalyst")
async def run_catalyst(uid: str = Depends(verify_firebase_token), body: dict = Body(None)):
    """Catalyst Agent - AI financial growth agent"""
    return await run_catalyst_analysis(uid)

@app.post("/run-strategist")
async def run_strategist(uid: str = Depends(verify_firebase_token), body: dict = Body(None)):
    """Strategist Agent - Investment strategy expert"""
    return await run_strategist_analysis(uid)

# --- Notification Endpoint ---
@app.post("/send-notification")
async def send_notification(uid: str = Depends(verify_firebase_token), body: dict = Body(...)):
    try:
        print(f"🔍 DEBUG: Received notification request for user {uid}")
        print(f"🔍 DEBUG: Request body keys: {list(body.keys())}")
        
        # Extract notification data from request body
        notification_type = body.get('type', 'general')
        title = body.get('title', 'Invested Alert')
        body_text = body.get('body', 'You have a new notification')
        data = body.get('data', {})
        
        # Get FCM token - try multiple sources
        fcm_token = None
        
        # 1. Try to get from request body first (fallback)
        if 'fcm_token' in body:
            fcm_token = body['fcm_token']
            print(f"✅ Using FCM token from request body: {fcm_token[:50]}...")
        
        # 2. If not in request body, try Firestore
        if not fcm_token:
            try:
                db = firestore.client()
                user_doc = await asyncio.to_thread(db.collection("users").document(uid).get)
                
                if user_doc.exists:
                    user_data = user_doc.to_dict()
                    fcm_token = user_data.get('fcm_token')
                    if fcm_token:
                        print(f"✅ Using FCM token from Firestore: {fcm_token[:50]}...")
            except Exception as e:
                print(f"⚠️ Could not get FCM token from Firestore: {e}")
        
        if not fcm_token:
            print(f"❌ No FCM token found in request body or Firestore")
            print(f"🔍 DEBUG: Request body: {body}")
            raise HTTPException(status_code=400, detail="FCM token not found for user")
        
        print(f"✅ FCM token found: {fcm_token[:50]}...")
        
        # Create the message
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body_text,
            ),
            data=data,
            token=fcm_token,
        )
        
        print(f"🔍 DEBUG: Created FCM message: {message}")
        
        # Send the message
        try:
            response = await asyncio.to_thread(messaging.send, message)
            print(f"✅ Notification sent successfully: {response}")
        except Exception as fcm_error:
            print(f"❌ FCM send error: {fcm_error}")
            print(f"🔍 DEBUG: FCM error type: {type(fcm_error)}")
            raise HTTPException(status_code=500, detail=f"FCM send failed: {str(fcm_error)}")
        
        return {
            "success": True,
            "message_id": response,
            "notification_type": notification_type
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"❌ Error sending notification: {e}")
        print(f"🔍 DEBUG: Error type: {type(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to send notification: {str(e)}")

# --- Background Task for Proactive Notifications ---
@app.post("/trigger-guardian-alert")
async def trigger_guardian_alert(uid: str = Depends(verify_firebase_token)):
    """Trigger a proactive Guardian alert notification"""
    try:
        # This would typically be called by a scheduled task or webhook
        # For demo purposes, we'll send a sample alert
        
        notification_data = {
            "type": "guardian_alert",
            "title": "🚨 Guardian Alert",
            "body": "Unusual spending pattern detected in your account!",
            "data": {
                "type": "guardian_alert",
                "alert_id": f"alert_{uuid.uuid4().hex[:8]}",
                "severity": "high",
                "action_required": "true"
            }
        }
        
        # Call the send-notification endpoint
        return await send_notification(uid, notification_data)
        
    except Exception as e:
        print(f"❌ Error triggering Guardian alert: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to trigger alert: {str(e)}")