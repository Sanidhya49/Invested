@echo off
echo Starting INVESTED servers...

echo.
echo 1. Installing backend dependencies...
cd invested-backend
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate
pip install -r requirements.txt
pip install firebase-admin google-cloud-aiplatform httpx

echo.
echo 2. Starting backend server...
start "Backend Server" cmd /k "cd invested-backend && venv\Scripts\activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo 3. Installing frontend dependencies...
cd ..\invested-frontend-webapp
if not exist node_modules (
    echo Installing npm packages...
    npm install
)

echo.
echo 4. Starting frontend server...
start "Frontend Server" cmd /k "cd invested-frontend-webapp && npm start"

echo.
echo 5. Starting MCP server (if needed)...
cd ..\fi-mcp-dev
if exist main.go (
    echo Starting Go MCP server...
    start "MCP Server" cmd /k "cd fi-mcp-dev && go run main.go"
)

echo.
echo All servers are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo MCP Server: http://localhost:8080
echo.
echo Press any key to exit this launcher...
pause > nul 