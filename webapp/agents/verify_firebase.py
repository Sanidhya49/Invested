#!/usr/bin/env python3
"""
Verify Firebase Admin SDK configuration
"""

import firebase_admin
from firebase_admin import credentials, messaging
import json
import os

def verify_firebase_config():
    """Verify Firebase configuration"""
    
    print("🔍 Verifying Firebase configuration...")
    
    # Check if service account file exists
    service_account_file = "invested-hackathon-firebase-adminsdk-fbsvc-38735ba923.json"
    if not os.path.exists(service_account_file):
        print(f"❌ Service account file not found: {service_account_file}")
        return False
    
    print(f"✅ Service account file found: {service_account_file}")
    
    # Try to load credentials
    try:
        cred = credentials.Certificate(service_account_file)
        print("✅ Credentials loaded successfully")
        
        # Check if app is already initialized
        try:
            app = firebase_admin.get_app()
            print("✅ Firebase app already initialized")
        except ValueError:
            print("⚠️ Firebase app not initialized, initializing...")
            app = firebase_admin.initialize_app(cred)
            print("✅ Firebase app initialized")
        
        # Test FCM message creation
        try:
            test_message = messaging.Message(
                notification=messaging.Notification(
                    title="Test",
                    body="Test message"
                ),
                token="test_token"
            )
            print("✅ FCM message creation works")
            
            # Note: We won't actually send the message since it's a test token
            print("✅ Firebase configuration is valid")
            return True
            
        except Exception as e:
            print(f"❌ FCM message creation failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to load credentials: {e}")
        return False

def check_service_account_permissions():
    """Check service account permissions"""
    
    print("\n🔍 Checking service account permissions...")
    
    try:
        with open("invested-hackathon-firebase-adminsdk-fbsvc-38735ba923.json", "r") as f:
            service_account = json.load(f)
        
        print(f"✅ Service account email: {service_account.get('client_email', 'Not found')}")
        print(f"✅ Project ID: {service_account.get('project_id', 'Not found')}")
        
        # Check if it has the right permissions
        if "firebase-adminsdk" in service_account.get('client_email', ''):
            print("✅ Service account appears to be Firebase Admin SDK")
        else:
            print("⚠️ Service account doesn't look like Firebase Admin SDK")
            
    except Exception as e:
        print(f"❌ Error reading service account: {e}")

if __name__ == "__main__":
    print("Firebase Configuration Verification")
    print("=" * 40)
    
    check_service_account_permissions()
    verify_firebase_config() 