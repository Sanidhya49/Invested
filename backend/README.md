# 🔧 Invested - FastAPI Backend

> **AI-Powered Personal Finance Backend API**

This is the FastAPI backend for the Invested personal finance app, providing AI-powered financial analysis, data processing, and secure API endpoints.

## 🚀 Features

### 🤖 AI Agents
- **Oracle**: Natural language financial assistant using Vertex AI
- **Guardian**: Proactive security and financial health monitoring
- **Catalyst**: Investment opportunities and growth recommendations
- **Strategist**: Portfolio analysis and strategic advice

### 📊 Data Processing
- Real-time financial data integration via MCP server
- Bank transaction analysis
- Subscription detection and categorization
- Net worth calculation and tracking

### 🔐 Security
- Firebase Authentication integration
- Token-based API security
- Secure data transmission
- Environment variable management

## 🏗️ Architecture

```
backend/
├── main.py                    # FastAPI application
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (not in git)
├── .venv/                    # Virtual environment
└── README.md                # This file
```

## 🛠️ Setup & Installation

### Prerequisites

- **Python** (3.8 or higher)
- **Firebase Account** (for authentication)
- **Google Cloud Project** (for Vertex AI)
- **MCP Server** (for financial data)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   
   # Activate virtual environment
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Create .env file
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up service accounts**
   - Download Firebase service account JSON
   - Download Google Cloud service account JSON
   - Place them in the backend directory

6. **Run the server**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Firebase Configuration
FIREBASE_SERVICE_ACCOUNT=path/to/firebase-service-account.json

# Google Cloud Configuration
GOOGLE_APPLICATION_CREDENTIALS=path/to/google-cloud-service-account.json
GCP_PROJECT_ID=your-project-id
GCP_LOCATION=us-central1

# MCP Server Configuration
MCP_SERVER_BASE_URL=http://localhost:8080

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

### Service Account Setup

1. **Firebase Service Account**
   - Go to Firebase Console → Project Settings → Service Accounts
   - Generate new private key
   - Download JSON file
   - Place in backend directory

2. **Google Cloud Service Account**
   - Go to Google Cloud Console → IAM & Admin → Service Accounts
   - Create new service account with Vertex AI permissions
   - Download JSON key
   - Place in backend directory

## 🔌 API Endpoints

### Authentication
```http
POST /start-fi-auth
```
Initialize FI authentication for user

### User Data
```http
GET /get-user-data
```
Fetch user's financial summary and net worth

```http
GET /get-subscriptions
```
Fetch subscription data from bank transactions

### AI Agents
```http
POST /ask-oracle
Content-Type: application/json

{
  "question": "What is my current net worth?"
}
```

```http
POST /run-guardian
```
Generate security alerts and recommendations

```http
POST /run-catalyst
```
Generate investment opportunities

```http
POST /run-strategist
```
Generate portfolio analysis and strategy

### Health Check
```http
GET /health
```
Server health status

## 🤖 AI Integration

### Vertex AI Configuration
- Uses Gemini 2.5 Flash model
- Tool integration for market data
- Structured JSON responses
- Error handling and fallbacks

### AI Agent Prompts
Each agent has specialized prompts:
- **Oracle**: Conversational financial assistant
- **Guardian**: Security and monitoring focus
- **Catalyst**: Growth and opportunity focus
- **Strategist**: Portfolio and strategy focus

## 📊 Data Sources

### MCP Server Integration
- Bank transactions via `fetch_bank_transactions`
- Credit reports via `fetch_credit_report`
- EPF details via `fetch_epf_details`
- Mutual fund transactions via `fetch_mf_transactions`
- Stock transactions via `fetch_stock_transactions`
- Net worth data via `fetch_net_worth`

### Data Processing
- Transaction categorization
- Subscription detection
- Financial calculations
- Trend analysis

## 🔒 Security

### Authentication
- Firebase ID token validation
- Secure token verification
- User session management

### API Security
- CORS configuration
- Rate limiting (can be added)
- Input validation
- Error handling

## 🧪 Testing

### Unit Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest
```

### API Testing
```bash
# Using curl
curl -X GET "http://localhost:8000/health"

# Using Python requests
import requests
response = requests.get("http://localhost:8000/health")
print(response.json())
```

## 📝 Development

### Code Structure
```python
# main.py structure
├── Imports and configurations
├── Firebase initialization
├── Vertex AI setup
├── API endpoints
├── Helper functions
└── Error handling
```

### Adding New Endpoints
1. Define the endpoint function
2. Add authentication dependency
3. Implement error handling
4. Add documentation
5. Test thoroughly

### Debugging
```bash
# Run with debug mode
uvicorn main:app --reload --log-level debug

# Check logs
tail -f uvicorn.log
```

## 🚀 Deployment

### Local Development
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Deployment
1. **Set up server**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Set environment variables
   export DEBUG=false
   export HOST=0.0.0.0
   export PORT=8000
   ```

2. **Use process manager**
   ```bash
   # Using systemd
   sudo systemctl start invested-backend
   
   # Using PM2
   pm2 start main.py --name invested-backend
   ```

3. **Set up reverse proxy (Nginx)**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## 📊 Monitoring

### Logging
- Structured logging with timestamps
- Error tracking and reporting
- Performance monitoring
- API usage analytics

### Health Checks
- Database connectivity
- External service status
- Memory and CPU usage
- Response time monitoring

## 🔧 Troubleshooting

### Common Issues

1. **Firebase Authentication Errors**
   - Check service account JSON path
   - Verify Firebase project configuration
   - Ensure proper permissions

2. **Vertex AI Errors**
   - Verify Google Cloud credentials
   - Check API quotas and limits
   - Ensure Vertex AI API is enabled

3. **MCP Server Connection**
   - Verify MCP server is running
   - Check network connectivity
   - Validate session IDs

### Debug Commands
```bash
# Check Python environment
python --version
pip list

# Test Firebase connection
python -c "import firebase_admin; print('Firebase OK')"

# Test Google Cloud connection
python -c "import vertexai; print('Vertex AI OK')"

# Check server status
curl http://localhost:8000/health
```

## 📝 API Documentation

### Interactive Docs
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Request/Response Examples
```python
# Example: Get user data
import requests

headers = {
    'Authorization': 'Bearer YOUR_FIREBASE_TOKEN'
}

response = requests.get(
    'http://localhost:8000/get-user-data',
    headers=headers
)

print(response.json())
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Development Guidelines
- Follow PEP 8 style guide
- Add type hints
- Include error handling
- Write comprehensive tests
- Update documentation

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- FastAPI team for the excellent framework
- Firebase for authentication services
- Google Cloud for AI capabilities
- MCP community for financial data integration

---

**Built with ❤️ using FastAPI and Python** 