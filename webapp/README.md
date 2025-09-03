# INVESTED - AI-Powered Financial Intelligence Platform

<div align="center">
  <img src="invested-frontend-webapp/public/logo.png" alt="INVESTED Logo" width="200"/>
  <h3>Let AI Talk to Your Money 💰</h3>
</div>

## 🚀 Overview

**INVESTED** is a comprehensive financial intelligence platform that leverages Google Cloud, Vertex AI, and modern web technologies to deliver smart financial insights, anomaly detection, tax planning, and subscription management through conversational AI.

## ✨ Key Features

### 🤖 AI Agents
- **🧙 Oracle** - AI-powered personal finance assistant for tax questions and general financial advice
- **🛡️ Guardian** - Anomaly detection and security alerts for financial safety
- **🚀 Catalyst** - Growth recognition and investment tips powered by AI
- **📊 Strategist** - Portfolio analysis and stock recommendations

### 💻 Technology Stack
- **Backend**: FastAPI (Python) with Go-based MCP server
- **Frontend**: React.js with modern UI components
- **AI/ML**: Google Cloud Vertex AI, Gemini Chat
- **Authentication**: JWT-based security
- **Database**: Firebase integration
- **Cloud**: Google Cloud Platform

## 🏗️ Architecture

### Current Structure
```
invested/
├── invested-backend/          # FastAPI backend server
├── invested-frontend-webapp/  # React frontend application
├── fi-mcp-dev/               # Go-based MCP server
├── agents/                   # AI agent implementations
└── agent-server/            # Agent server components
```

### Target Structure (After Push)
```
webapp/
├── invested-backend/          # FastAPI backend server
├── invested-frontend-webapp/  # React frontend application
├── fi-mcp-dev/               # Go-based MCP server
├── agents/                   # AI agent implementations
├── agent-server/            # Agent server components
└── README.md                # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Go (for MCP server)
- Google Cloud Platform account

### Option 1: Automated Setup (Recommended)
```powershell
# Install dependencies
.\install-dependencies.ps1

# Start all servers
.\start-servers.ps1
```

### Option 2: Manual Setup

#### 1. Backend Setup
```powershell
cd invested-backend
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install firebase-admin google-cloud-aiplatform httpx
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. Frontend Setup
```powershell
cd invested-frontend-webapp
npm install
npm start
```

#### 3. MCP Server (Optional)
```powershell
cd fi-mcp-dev
go run main.go
```

## 🌐 Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **MCP Server**: http://localhost:8080

## 🔧 API Endpoints

### AI Agents
- `POST /agents/oracle/chat` - Ask Oracle for financial advice
- `GET /agents/guardian/alerts` - Get security alerts
- `GET /agents/catalyst/tips` - Get growth insights
- `GET /agents/strategist/portfolio` - Get portfolio analysis
- `GET /agents/status` - Check agent status

### Core Features
- User authentication and management
- Financial data integration
- Real-time notifications
- Portfolio tracking
- Goal management

## 🎯 AI Agent Capabilities

### Oracle Agent
- Tax planning and advice
- General financial guidance
- Conversational AI interface
- Context-aware responses

### Guardian Agent
- Fraud detection
- Unusual transaction alerts
- Security monitoring
- Proactive safety recommendations

### Catalyst Agent
- Growth opportunity identification
- Investment recommendations
- Market analysis insights
- Diversification suggestions

### Strategist Agent
- Portfolio optimization
- Stock investment strategies
- Risk assessment
- Market trend analysis

## 🔒 Security Features

- JWT-based authentication
- Google Cloud KMS integration
- Secret Manager for sensitive data
- Rate limiting with Redis
- CORS configuration
- Input validation and sanitization

## 📊 Data Integration

The platform integrates with various financial data sources:
- Bank transactions
- Credit reports
- EPF details
- Mutual fund transactions
- Stock transactions
- Net worth calculations

## 🛠️ Development

### Project Structure
```
invested/
├── invested-backend/
│   ├── routers/           # API route handlers
│   ├── services.py        # Business logic
│   ├── schemas.py         # Data models
│   └── utils/            # Utility functions
├── invested-frontend-webapp/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   └── utils/        # Utility functions
│   └── public/           # Static assets
├── fi-mcp-dev/           # Go MCP server
└── agents/              # AI agent implementations
```

### Testing
```powershell
# Test AI agents
python test_agents.py

# Test user functionality
python test_user_2222222222.py
```

## 🚀 Deployment

### Environment Setup
1. Copy `invested-backend/env.example` to `invested-backend/.env`
2. Configure Google Cloud credentials
3. Set up Firebase project
4. Configure environment variables

### Production Deployment
- Backend: Deploy to Google Cloud Run or similar
- Frontend: Deploy to Vercel, Netlify, or similar
- Database: Use Google Cloud Firestore
- AI Services: Configure Vertex AI endpoints

## 📦 Repository Structure Setup

### Pushing to Target Repository

To push this entire repository under a `webapp` directory in the target repository:

#### Method 1: Using Git Subtree (Recommended)
```bash
# Add the target repository as a remote
git remote add target https://github.com/Sanidhya49/invested3.git

# Push the current repository to the target as a subtree
git subtree push --prefix=webapp target main
```

#### Method 2: Manual Directory Restructure
```bash
# Create webapp directory and move all files
mkdir webapp
git mv * webapp/ 2>/dev/null || true
git mv .* webapp/ 2>/dev/null || true

# Commit the restructure
git add .
git commit -m "Restructure repository under webapp directory"

# Push to target repository
git remote add target https://github.com/Sanidhya49/invested3.git
git push target main
```

#### Method 3: Using Git Filter-Branch (Advanced)
```bash
# Create a new branch with the restructured content
git filter-branch --tree-filter '
mkdir -p webapp
mv * webapp/ 2>/dev/null || true
mv .* webapp/ 2>/dev/null || true
' --prune-empty HEAD

# Push the restructured branch
git remote add target https://github.com/Sanidhya49/invested3.git
git push target HEAD:main
```

### After Pushing

Once pushed, the target repository will have this structure:
```
invested3/
├── webapp/
│   ├── invested-backend/
│   ├── invested-frontend-webapp/
│   ├── fi-mcp-dev/
│   ├── agents/
│   ├── agent-server/
│   ├── README.md
│   └── ... (all other files)
├── backend/          # (existing in target repo)
├── invested/         # (existing in target repo)
└── README.md         # (existing in target repo)
```

### Updating Paths

After pushing, you may need to update some paths in your code:
- Update any absolute paths that reference the root directory
- Update import statements if they reference parent directories
- Update configuration files that reference file paths

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Troubleshooting

### Common Issues

#### PowerShell Issues
- Use `;` instead of `&&` for command chaining
- Use `.\start-servers.ps1` to run the PowerShell script

#### Missing Dependencies
- Make sure to install `firebase-admin` and `google-cloud-aiplatform`
- Check that all Python packages are installed in the virtual environment

#### Import Errors
- The agents router includes fallback functions if agent modules can't be imported
- Check that the `agents/` directory exists and contains the agent files

#### Port Conflicts
- Backend: 8000
- Frontend: 3000
- MCP: 8080
- Make sure these ports are available

#### Repository Push Issues
- Ensure you have write access to the target repository
- Check that the target repository exists and is accessible
- Verify your Git credentials are properly configured
- If using subtree push, make sure the target repository is clean

### Getting Help
- Check the logs in each service directory
- Verify environment variables are set correctly
- Ensure all dependencies are installed
- Check network connectivity for external services

## 🔮 Roadmap

- [ ] Mobile app development (Flutter)
- [ ] Advanced AI features and machine learning
- [ ] Real-time notifications
- [ ] Advanced portfolio visualization
- [ ] Voice commands and natural language processing
- [ ] Multi-language support
- [ ] Advanced security features
- [ ] Performance optimizations

## 📞 Support

For support and questions:
- Create an issue in this repository
- Check the troubleshooting section
- Review the API documentation

---

<div align="center">
  <p>Built with ❤️ using modern technologies</p>
  <p>Let AI help you make smarter financial decisions!</p>
  <br>
  <p><strong>Team: hacktic</strong></p>
</div>




