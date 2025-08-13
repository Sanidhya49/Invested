# Invested Monorepo — Complete Setup & Run Guide

End‑to‑end, multi‑service personal finance app powered by AI agents. This single guide combines everything you need to build and run the entire stack: Flutter app, Notification/REST backend, Go MCP server, and Python MCP proxy.

## Repository Layout

```
invested/                      # Monorepo root (this README)
├─ invested/                   # Flutter app
│  ├─ lib/
│  ├─ android/
│  ├─ ios/
│  └─ pubspec.yaml
├─ backend/                    # Notification/REST backend (FastAPI on 8000)
│  ├─ main.py
│  └─ requirements.txt
└─ fi_mcp_with_backend-main/   # MCP server (Go) + Python proxy
   └─ fi_mcp_with_backend-main/
      ├─ fi-mcp-dev/           # Go MCP server (port 8080)
      │  ├─ main.go
      │  └─ test_data_dir/     # Dummy data per phone number
      └─ python-backend/       # Python MCP backend (port 8001)
         ├─ main.py
         └─ requirements.txt
```

## Ports Matrix

- 8000: Notification/REST backend (`backend/`)
- 8080: Go MCP server (`fi-mcp-dev/`)
- 8001: Python MCP backend (`python-backend/`)
- Android emulator access to localhost: use `http://10.0.2.2:<port>`

## Prerequisites

- Flutter SDK 3.8+
- Android Studio or VS Code with Flutter/Dart plugins
- Python 3.10+
- Go 1.23+
- Firebase project (for the Flutter app)
- Gemini API key (for MCP Python backend)

## 1) Start Notification/REST Backend (port 8000)

This is the backend the Flutter app talks to (e.g., notifications at `/send-notification`).

```bash
cd backend
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 2) Start Go MCP Server (port 8080)

The MCP server exposes:
- `/mockWebPage?sessionId=...` — simple login page
- `/login` — POST form `{ sessionId, phoneNumber }` (phone numbers must exist as folders in `test_data_dir/`)
- `/mcp/stream` — tool invocations, requires header `X-Session-ID: <sessionId>` previously registered via `/login`

```bash
cd fi_mcp_with_backend-main/fi_mcp_with_backend-main/fi-mcp-dev
go mod tidy
# macOS/Linux
FI_MCP_PORT=8080 go run .
# Windows PowerShell
$env:FI_MCP_PORT="8080"; go run .
```

## 3) Start Python MCP Backend (port 8001)

Proxies to the Go server and manages a global MCP session at startup.

```bash
cd fi_mcp_with_backend-main/fi_mcp_with_backend-main/python-backend
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Create .env
# On Windows PowerShell:
"GEMINI_API_KEY=your_gemini_api_key" | Out-File -Encoding utf8 .env
"FI_MCP_SERVER_URL=http://localhost:8080" | Out-File -Append -Encoding utf8 .env
"MCP_AUTH_PHONE_NUMBER=2222222222" | Out-File -Append -Encoding utf8 .env

# On macOS/Linux instead:
# cat > .env << 'EOF'
# GEMINI_API_KEY=your_gemini_api_key
# FI_MCP_SERVER_URL=http://localhost:8080
# MCP_AUTH_PHONE_NUMBER=2222222222
# EOF

uvicorn main:app --port 8001 --reload
```

On startup it should print: “Successfully obtained global MCP session: backend_session_…”.

## 4) Run the Flutter App

```bash
cd invested/invested
flutter pub get
flutter run
```

### Android notes (local notifications, Firebase Messaging)
- Already configured: core library desugaring and notification channels.
- If you see desugaring errors, ensure `invested/android/app/build.gradle.kts` has:
  - `compileOptions { isCoreLibraryDesugaringEnabled = true }`
  - `dependencies { coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.0.4") }`
- Emulator to host: use `http://10.0.2.2:<port>`.

### Backend endpoints used by the Flutter app
- Notification send: `POST http://10.0.2.2:8000/send-notification`
  - Body includes `token`, `title`, `body`, `category`, `data`

## Typical Local Workflow

1. Start 8000 (Notification/REST) → Start 8080 (Go MCP) → Start 8001 (Python MCP) → Run Flutter app
2. If the Flutter app needs the MCP login page, open `http://10.0.2.2:8080/mockWebPage?sessionId=<YOUR_SESSION>` in the emulator; submit an allowed phone number (a folder in `fi-mcp-dev/test_data_dir/`).
3. To use the MCP endpoints through the Python backend, call its endpoints (e.g., `POST /process_agent_request`) so it reuses the global session established at startup.

## Configuration

### Firebase Setup
1. Create a Firebase project
2. Enable Authentication and Firestore
3. Download `google-services.json` and place it in `invested/android/app/`

### MCP Server Setup
1. Go server runs on `8080` and exposes `/mockWebPage`, `/login`, `/mcp/stream`.
2. Python backend proxies to it on `8001` and sets up a global MCP session at startup.
3. Flutter app should open the login web page on the Go MCP port (`http://10.0.2.2:8080/...`) if doing a client‑side login.

## Troubleshooting

- 404 for `/mockWebPage`
  - You are hitting the wrong port. The login page is served by the Go MCP server (8080), not the Python backend.
- "Session NOT FOUND" in MCP logs
  - The `X-Session-ID` used for `/mcp/stream` was not registered via `/login`. Reuse the same session ID for both steps, or always go through the Python MCP backend which manages a single global session.
- Port already in use
  - Change `FI_MCP_PORT` for the Go server and update `FI_MCP_SERVER_URL` in the Python MCP backend accordingly.
- Android cannot reach localhost
  - Use `http://10.0.2.2:<port>` from the emulator.

## Environment Variables

### Python MCP backend (`fi_mcp_with_backend-main/.../python-backend/.env`)
```env
GEMINI_API_KEY=your_gemini_api_key
FI_MCP_SERVER_URL=http://localhost:8080
MCP_AUTH_PHONE_NUMBER=2222222222
```

### Notification/REST backend (`backend/.env` if applicable)
```env
# Example — adapt to your backend
FIREBASE_PROJECT_ID=...
FIREBASE_CREDENTIALS_JSON=...  # or GOOGLE_APPLICATION_CREDENTIALS=path/to/key.json
```

## Data

- Dummy financial data is stored in `fi-mcp-dev/test_data_dir/<phone_number>/*.json`.
- Allowed phone numbers are the directory names in `test_data_dir/`.

## License

see `LICENSE`.

---

Made by team "Hacktic"
