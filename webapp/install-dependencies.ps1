# INVESTED Dependencies Installation Script
Write-Host "Installing INVESTED dependencies..." -ForegroundColor Green

# Backend dependencies
Write-Host "`nInstalling backend dependencies..." -ForegroundColor Yellow
Set-Location invested-backend

if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
}

# Activate virtual environment
& "venv\Scripts\Activate.ps1"

# Install all required packages
Write-Host "Installing Python packages..." -ForegroundColor Cyan
pip install -r requirements.txt
pip install firebase-admin google-cloud-aiplatform httpx reportlab

Write-Host "✅ Backend dependencies installed" -ForegroundColor Green

# Frontend dependencies
Write-Host "`nInstalling frontend dependencies..." -ForegroundColor Yellow
Set-Location ..\invested-frontend-webapp

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing npm packages..." -ForegroundColor Cyan
    npm install
} else {
    Write-Host "Updating npm packages..." -ForegroundColor Cyan
    npm install
}

Write-Host "✅ Frontend dependencies installed" -ForegroundColor Green

# Return to root
Set-Location ..

Write-Host "`n🎉 All dependencies installed successfully!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Run: .\start-servers.ps1" -ForegroundColor Cyan
Write-Host "2. Or manually start servers using the commands in QUICK_START.md" -ForegroundColor Cyan 