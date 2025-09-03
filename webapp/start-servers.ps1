# INVESTED Server Startup Script (PowerShell)
Write-Host "Starting INVESTED servers..." -ForegroundColor Green

# 1. Install backend dependencies
Write-Host "`n1. Installing backend dependencies..." -ForegroundColor Yellow
Set-Location invested-backend

if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
}

# Activate virtual environment and install dependencies
& "venv\Scripts\Activate.ps1"
pip install -r requirements.txt
pip install firebase-admin google-cloud-aiplatform httpx

# 2. Start backend server
Write-Host "`n2. Starting backend server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd invested-backend; venv\Scripts\Activate.ps1; uvicorn main:app --reload --host 0.0.0.0 --port 8000" -WindowStyle Normal

# 3. Install frontend dependencies
Write-Host "`n3. Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location ..\invested-frontend-webapp

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing npm packages..." -ForegroundColor Cyan
    npm install
}

# 4. Start frontend server
Write-Host "`n4. Starting frontend server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd invested-frontend-webapp; npm start" -WindowStyle Normal

# 5. Start MCP server (if needed)
Write-Host "`n5. Starting MCP server (if needed)..." -ForegroundColor Yellow
Set-Location ..\fi-mcp-dev

if (Test-Path "main.go") {
    Write-Host "Starting Go MCP server..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd fi-mcp-dev; go run main.go" -WindowStyle Normal
}

# Return to root directory
Set-Location ..

Write-Host "`nAll servers are starting..." -ForegroundColor Green
Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "MCP Server: http://localhost:8080" -ForegroundColor Cyan

Write-Host "`nPress any key to exit this launcher..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 