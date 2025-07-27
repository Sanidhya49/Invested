# 🚀 Invested - AI-Powered Personal Finance App

> **Your intelligent financial companion powered by AI agents**

Invested is a comprehensive personal finance application that combines the power of AI agents with real-time financial data to provide personalized insights, recommendations, and automated financial management.

## 🌟 Features

### 🤖 AI Agents
- **Oracle**: Your personal finance assistant for questions and analysis
- **Guardian**: Proactive alerts and security monitoring
- **Catalyst**: Growth opportunities and investment recommendations
- **Strategist**: Portfolio analysis and strategic advice

### 📊 Financial Dashboard
- Real-time net worth tracking
- Asset and liability breakdown
- Interactive charts and visualizations
- Financial insights and trends

### 📱 Subscription Management
- Automatic subscription detection from bank transactions
- Billing cycle tracking
- Cost analysis and optimization suggestions
- Payment reminders

### 📈 Advanced Analytics
- Multi-dimensional financial insights
- Historical trend analysis
- Customizable date ranges
- Export capabilities

## 🏗️ Architecture

```
invested/
├── invested/                 # Flutter Mobile App (Frontend)
│   ├── lib/
│   │   ├── screens/         # UI Screens
│   │   ├── widgets/         # Reusable Components
│   │   └── main.dart        # App Entry Point
│   ├── android/             # Android Platform
│   ├── ios/                 # iOS Platform
│   └── pubspec.yaml         # Flutter Dependencies
├── backend/                 # FastAPI Backend (Python)
│   ├── main.py             # API Server
│   ├── requirements.txt    # Python Dependencies
│   └── .venv/              # Virtual Environment
└── README.md               # This File
```

## 🚀 Quick Start

### Prerequisites

- **Flutter SDK** (3.8.1 or higher)
- **Python** (3.8 or higher)
- **Firebase Account** (for authentication and database)
- **Google Cloud Project** (for Vertex AI)
- **MCP Server** (for financial data)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd invested
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run the backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup

```bash
# Navigate to Flutter app directory
cd invested

# Install Flutter dependencies
flutter pub get

# Run the app
flutter run
```

## 🔧 Configuration

### Firebase Setup

1. Create a Firebase project
2. Enable Authentication and Firestore
3. Download `google-services.json` and place it in `invested/android/app/`
4. Download Firebase service account JSON and place it in `backend/`

### Google Cloud Setup

1. Create a Google Cloud project
2. Enable Vertex AI API
3. Create a service account with Vertex AI permissions
4. Download the service account key and place it in `backend/`

### MCP Server Setup

1. Set up the MCP server for financial data
2. Configure the server URL in `backend/main.py`
3. Ensure the server provides the required financial data endpoints

## 📱 App Screens

### Dashboard
- Financial overview with net worth
- Quick access to all features
- Real-time data updates

### Oracle Chat
- AI-powered financial assistant
- Natural language queries
- Personalized responses

### Guardian Alerts
- Security notifications
- Financial health alerts
- Proactive recommendations

### Catalyst Opportunities
- Investment opportunities
- Growth recommendations
- Risk assessment

### Strategist Analysis
- Portfolio analysis
- Strategic recommendations
- Market insights

### Insights
- Interactive charts
- Financial analytics
- Custom date ranges

### Subscriptions
- Auto-detected subscriptions
- Billing cycle management
- Cost optimization

## 🔌 API Endpoints

### Authentication
- `POST /start-fi-auth` - Initialize FI authentication

### User Data
- `GET /get-user-data` - Fetch user's financial summary
- `GET /get-subscriptions` - Fetch subscription data

### AI Agents
- `POST /ask-oracle` - Oracle AI assistant
- `POST /run-guardian` - Guardian alerts
- `POST /run-catalyst` - Catalyst opportunities
- `POST /run-strategist` - Strategist analysis

### Health
- `GET /health` - Server health check

## 🛠️ Development

### Backend Development

```bash
cd backend
# Activate virtual environment
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest

# Format code
black main.py
```

### Frontend Development

```bash
cd invested

# Install dependencies
flutter pub get

# Run in debug mode
flutter run

# Run tests
flutter test

# Build for production
flutter build apk --release
```

### Code Structure

#### Backend (`backend/`)
- `main.py` - FastAPI application with all endpoints
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (not in git)

#### Frontend (`invested/`)
- `lib/screens/` - App screens and UI
- `lib/widgets/` - Reusable UI components
- `pubspec.yaml` - Flutter dependencies

## 🔒 Security

- Firebase Authentication for user management
- Secure API endpoints with token validation
- Environment variables for sensitive data
- HTTPS enforcement in production

## 📊 Data Sources

- **Bank Transactions**: Via MCP server
- **Credit Reports**: Via MCP server
- **Investment Data**: Via MCP server
- **EPF Details**: Via MCP server
- **Stock Transactions**: Via MCP server

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow Flutter/Dart coding standards
- Use meaningful commit messages
- Add tests for new features
- Update documentation as needed
- Don't commit sensitive data or credentials

## 📝 Environment Variables

### Backend (`.env`)
```env
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
FIREBASE_SERVICE_ACCOUNT=path/to/firebase-service-account.json
MCP_SERVER_URL=http://localhost:8080
```

### Frontend
- Firebase configuration in `google-services.json`
- API base URL in app configuration

## 🚀 Deployment

### Backend Deployment
1. Set up a cloud server (AWS, GCP, Azure)
2. Install Python and dependencies
3. Configure environment variables
4. Use a process manager (PM2, systemd)
5. Set up reverse proxy (Nginx)

### Frontend Deployment
1. Build the Flutter app for target platforms
2. Deploy to app stores (Google Play, App Store)
3. Configure Firebase for production

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Flutter team for the amazing framework
- FastAPI for the high-performance backend
- Firebase for authentication and database
- Google Cloud for AI services
- MCP community for financial data integration

## 📞 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

---

**Made with ❤️ by the Invested Team** 