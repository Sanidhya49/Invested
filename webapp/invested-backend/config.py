"""
Configuration module for the Invested Backend.
Centralizes all environment variable handling and provides fallbacks.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Environment detection
ENV = os.getenv("ENV", "development")
IS_PRODUCTION = ENV == "production"

# MCP Server Configuration
def get_mcp_server_url():
    """Get MCP server URL with environment-based fallback."""
    if IS_PRODUCTION:
        url = os.getenv("FI_MCP_SERVER_URL")
        if not url:
            print("WARNING: FI_MCP_SERVER_URL not set in production environment")
            return None
        return url
    else:
        return os.getenv("FI_MCP_SERVER_URL", "http://localhost:8080")

FI_MCP_SERVER_URL = get_mcp_server_url()

# Authentication Configuration
MCP_AUTH_PHONE_NUMBER = os.getenv("MCP_AUTH_PHONE_NUMBER", "8888888888")

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# File Paths
MCP_FILE_PATH = os.getenv("MCP_FILE_PATH")

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# CORS Configuration
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # Add production origins here when deploying
]

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

def validate_config():
    """Validate that all required configuration is present."""
    errors = []
    
    if IS_PRODUCTION and not FI_MCP_SERVER_URL:
        errors.append("FI_MCP_SERVER_URL is required in production")
    
    if not GEMINI_API_KEY:
        print("WARNING: GEMINI_API_KEY not set. Gemini/Agent features will not work.")
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    return True

# Log configuration on startup
def log_config():
    """Log current configuration for debugging."""
    print(f"🔍 Environment: {ENV}")
    print(f"🔍 MCP server set to: {FI_MCP_SERVER_URL}")
    print(f"🔍 MCP auth phone: {MCP_AUTH_PHONE_NUMBER}")
    print(f"🔍 Gemini API key configured: {'Yes' if GEMINI_API_KEY else 'No'}")
    print(f"🔍 MCP file path: {MCP_FILE_PATH}")

# Initialize and validate configuration
if __name__ == "__main__":
    log_config()
    try:
        validate_config()
        print("✅ Configuration validation passed")
    except ValueError as e:
        print(f"❌ Configuration validation failed: {e}")
        exit(1) 