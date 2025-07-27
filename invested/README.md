# 📱 Invested - Flutter Mobile App

> **AI-Powered Personal Finance Mobile Application**

This is the Flutter frontend for the Invested personal finance app, featuring AI agents, real-time financial data, and comprehensive financial management tools.

## 🚀 Features

### 🤖 AI-Powered Features
- **Oracle Chat**: Interactive AI financial assistant
- **Guardian Alerts**: Proactive financial security monitoring
- **Catalyst Opportunities**: Investment and growth recommendations
- **Strategist Analysis**: Portfolio analysis and strategic advice

### 📊 Financial Dashboard
- Real-time net worth tracking
- Asset and liability visualization
- Interactive charts using `fl_chart`
- Financial insights and trends

### 📱 Subscription Management
- Automatic subscription detection from bank transactions
- Billing cycle tracking and reminders
- Cost analysis and optimization
- Payment due date notifications

### 📈 Advanced Analytics
- Multi-dimensional financial insights
- Historical trend analysis
- Customizable date ranges
- Beautiful data visualizations

## 🏗️ Project Structure

```
lib/
├── main.dart                    # App entry point
├── screens/                     # App screens
│   ├── dashboard_screen.dart    # Main dashboard
│   ├── oracle_chat_screen.dart  # AI chat interface
│   ├── guardian_alerts_screen.dart
│   ├── catalyst_opportunities_screen.dart
│   ├── strategist_screen.dart
│   ├── insights_screen.dart     # Analytics & charts
│   ├── subscriptions_screen.dart
│   └── profile_screen.dart
├── widgets/                     # Reusable components
│   └── add_goal_modal.dart
└── utils/                       # Utilities
    ├── app_theme.dart
    └── formatters.dart
```

## 🛠️ Setup & Installation

### Prerequisites

- **Flutter SDK** (3.8.1 or higher)
- **Android Studio** or **VS Code**
- **Firebase Account** (for authentication)
- **Backend Server** running on `http://10.0.2.2:8000`

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd invested
   ```

2. **Install dependencies**
   ```bash
   flutter pub get
   ```

3. **Configure Firebase**
   - Download `google-services.json` from Firebase Console
   - Place it in `android/app/google-services.json`

4. **Run the app**
   ```bash
   flutter run
   ```

## 📱 App Screens

### 🏠 Dashboard
- Financial overview with net worth display
- Quick access cards to all features
- Real-time data updates
- Bottom navigation for easy access

### 🤖 Oracle Chat
- AI-powered financial assistant
- Natural language queries
- Personalized financial advice
- Chat history and context

### 🛡️ Guardian Alerts
- Security notifications
- Financial health alerts
- Proactive recommendations
- Alert categorization

### 🚀 Catalyst Opportunities
- Investment opportunities
- Growth recommendations
- Risk assessment
- Actionable insights

### 📊 Strategist Analysis
- Portfolio analysis
- Strategic recommendations
- Market insights
- Performance tracking

### 📈 Insights
- Interactive financial charts
- Multi-dimensional analytics
- Custom date range selection
- Data visualization

### 📋 Subscriptions
- Auto-detected subscriptions from bank data
- Billing cycle management
- Cost optimization suggestions
- Payment tracking

## 🔧 Dependencies

### Core Dependencies
```yaml
dependencies:
  flutter:
    sdk: flutter
  firebase_core: ^2.24.2
  firebase_auth: ^4.16.0
  google_sign_in: ^6.2.1
  cloud_firestore: ^4.13.6
  http: ^1.2.1
  fl_chart: ^0.64.0
  intl: ^0.19.0
  url_launcher: ^6.3.2
```

### Development Dependencies
```yaml
dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^5.0.0
```

## 🎨 UI/UX Features

### Design System
- Material Design 3 principles
- Consistent color scheme
- Responsive layout
- Accessibility support

### Charts & Visualizations
- **fl_chart** for data visualization
- Interactive pie charts for asset breakdown
- Line charts for trends
- Bar charts for comparisons

### Navigation
- Bottom navigation bar
- Consistent back buttons
- Intuitive screen flow
- Quick access features

## 🔌 API Integration

### Backend Communication
- RESTful API calls to FastAPI backend
- Firebase Authentication integration
- Real-time data synchronization
- Error handling and retry logic

### Endpoints Used
- `GET /get-user-data` - Financial summary
- `GET /get-subscriptions` - Subscription data
- `POST /ask-oracle` - AI chat
- `POST /run-guardian` - Security alerts
- `POST /run-catalyst` - Opportunities
- `POST /run-strategist` - Analysis

## 🧪 Testing

### Unit Tests
```bash
flutter test
```

### Widget Tests
```bash
flutter test test/widget_test.dart
```

### Integration Tests
```bash
flutter drive --target=test_driver/app.dart
```

## 📦 Building

### Debug Build
```bash
flutter build apk --debug
```

### Release Build
```bash
flutter build apk --release
```

### App Bundle (for Play Store)
```bash
flutter build appbundle --release
```

## 🔒 Security

- Firebase Authentication
- Secure API communication
- Token-based authentication
- Data encryption in transit

## 🚀 Performance

- Optimized widget rebuilds
- Efficient state management
- Lazy loading for large datasets
- Memory management best practices

## 🐛 Debugging

### Common Issues

1. **Backend Connection**
   - Ensure backend is running on `http://10.0.2.2:8000`
   - Check network connectivity

2. **Firebase Setup**
   - Verify `google-services.json` is in correct location
   - Check Firebase project configuration

3. **Dependencies**
   - Run `flutter clean` and `flutter pub get`
   - Check for version conflicts

### Debug Commands
```bash
# Clean and rebuild
flutter clean
flutter pub get

# Check for issues
flutter doctor
flutter analyze

# Hot reload during development
flutter run --hot
```

## 📝 Development Guidelines

### Code Style
- Follow Dart/Flutter conventions
- Use meaningful variable names
- Add comments for complex logic
- Keep functions small and focused

### State Management
- Use `setState` for local state
- Consider Provider/Riverpod for complex state
- Minimize widget rebuilds

### Error Handling
- Implement proper try-catch blocks
- Show user-friendly error messages
- Log errors for debugging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Code Review Checklist
- [ ] Code follows Dart/Flutter conventions
- [ ] UI is responsive and accessible
- [ ] Error handling is implemented
- [ ] Tests are added/updated
- [ ] Documentation is updated

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Flutter team for the amazing framework
- fl_chart for beautiful visualizations
- Firebase for authentication and backend
- The open-source community

---

**Built with ❤️ using Flutter**
