# BREEZER Quick Start Script
# PowerShell script to get BREEZER running quickly

param(
    [string]$DeepSeekKey = ""
)

$ErrorActionPreference = "Stop"

Write-Host @"
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   🏄 BREEZER - AI-Powered Development Platform          ║
║      by RICHDALE AI                                      ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

# Check prerequisites
Write-Host "`n🔍 Checking prerequisites..." -ForegroundColor Yellow

# Check Docker
if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker not found. Please install Docker Desktop." -ForegroundColor Red
    Write-Host "   Download from: https://www.docker.com/products/docker-desktop/" -ForegroundColor White
    exit 1
}
Write-Host "✅ Docker found" -ForegroundColor Green

# Check Docker is running
try {
    docker ps | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Setup .env file
Write-Host "`n📝 Setting up configuration..." -ForegroundColor Yellow

if (!(Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Created .env file" -ForegroundColor Green
    
    if ($DeepSeekKey) {
        (Get-Content ".env") -replace 'DEEPSEEK_API_KEY=sk-your-deepseek-key-here', "DEEPSEEK_API_KEY=$DeepSeekKey" | Set-Content ".env"
        Write-Host "✅ Added DeepSeek API key" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Please add your DeepSeek API key to .env file" -ForegroundColor Yellow
        Write-Host "   Edit .env and set: DEEPSEEK_API_KEY=sk-your-key" -ForegroundColor White
        
        $response = Read-Host "`nDo you have a DeepSeek API key now? (y/n)"
        if ($response -eq "y") {
            $key = Read-Host "Enter your DeepSeek API key"
            (Get-Content ".env") -replace 'DEEPSEEK_API_KEY=sk-your-deepseek-key-here', "DEEPSEEK_API_KEY=$key" | Set-Content ".env"
            Write-Host "✅ Added DeepSeek API key" -ForegroundColor Green
        } else {
            Write-Host "`nGet your API key from: https://platform.deepseek.com/" -ForegroundColor Cyan
            Write-Host "Then run this script again with: .\quick-start.ps1 -DeepSeekKey sk-your-key" -ForegroundColor White
            exit 0
        }
    }
} else {
    Write-Host "✅ .env file exists" -ForegroundColor Green
}

# Start services
Write-Host "`n🚀 Starting BREEZER backend services..." -ForegroundColor Yellow
Write-Host "   This may take a few minutes on first run (downloading images)..." -ForegroundColor Gray

docker-compose up -d

# Wait for services
Write-Host "`n⏳ Waiting for services to be ready..." -ForegroundColor Yellow

$maxAttempts = 30
$attempt = 0
$healthy = $false

while ($attempt -lt $maxAttempts -and !$healthy) {
    Start-Sleep -Seconds 2
    $attempt++
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2
        if ($response.StatusCode -eq 200) {
            $healthy = $true
            Write-Host "✅ Backend is ready!" -ForegroundColor Green
        }
    } catch {
        Write-Host "." -NoNewline -ForegroundColor Gray
    }
}

if (!$healthy) {
    Write-Host "`n❌ Services did not start properly. Check logs with:" -ForegroundColor Red
    Write-Host "   docker-compose logs -f" -ForegroundColor White
    exit 1
}

# Test the system
Write-Host "`n🧪 Testing agent system..." -ForegroundColor Yellow

$testQuery = @{
    query = "Write a simple hello world function in Python"
    workspace_path = "C:/temp"
} | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Uri "http://localhost:8000/api/agent/query" `
        -Method POST `
        -Body $testQuery `
        -ContentType "application/json"
    
    Write-Host "✅ Agent test successful!" -ForegroundColor Green
    Write-Host "`nAgent Response Preview:" -ForegroundColor Cyan
    Write-Host ($result.content.Substring(0, [Math]::Min(200, $result.content.Length)) + "...") -ForegroundColor White
} catch {
    Write-Host "⚠️  Agent test failed, but services are running" -ForegroundColor Yellow
    Write-Host "   Check API key configuration in .env" -ForegroundColor Gray
}

# Success message
Write-Host @"

╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   ✅ BREEZER is running!                                 ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

📍 Services:
   • Backend API:  http://localhost:8000
   • API Docs:     http://localhost:8000/docs
   • Health:       http://localhost:8000/health/detailed

📖 Next Steps:

1. View API documentation:
   Start-Process http://localhost:8000/docs

2. Build BREEZER IDE (all platforms):
   docker-compose -f docker/docker-compose.build.yml up
   
   Or push to GitHub for automatic builds:
   git push origin main

3. Check logs:
   docker-compose logs -f backend

4. Stop services:
   docker-compose down

📚 Documentation:
   • Setup Guide: SETUP.md
   • Full Summary: PROJECT_SUMMARY.md
   • README: README.md

🏄 Happy coding with BREEZER!

"@ -ForegroundColor Green

# Open browser
$openBrowser = Read-Host "`nOpen API documentation in browser? (y/n)"
if ($openBrowser -eq "y") {
    Start-Process "http://localhost:8000/docs"
}

Write-Host "`n© 2025 RICHDALE AI. All rights reserved.`n" -ForegroundColor Gray
