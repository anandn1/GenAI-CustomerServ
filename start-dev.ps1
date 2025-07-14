# Walmart Whisper - Development Startup Script (PowerShell)

Write-Host "🚀 Starting Walmart Whisper Development Environment..." -ForegroundColor Green

# Function to check if port is in use
function Test-Port {
    param([int]$Port)
    try {
        $listener = [System.Net.NetworkInformation.IPGlobalProperties]::GetIPGlobalProperties()
        $endpoints = $listener.GetActiveTcpListeners()
        return $endpoints | Where-Object { $_.Port -eq $Port }
    }
    catch {
        return $false
    }
}

# Check if backend is already running
if (Test-Port 8000) {
    Write-Host "⚠️  Port 8000 is already in use. Backend might already be running." -ForegroundColor Yellow
} else {
    Write-Host "🔧 Starting Backend Server on port 8000..." -ForegroundColor Cyan
    Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000" -WorkingDirectory "backend" -WindowStyle Hidden
    Start-Sleep 3
}

# Check if frontend is already running
if ((Test-Port 5173) -or (Test-Port 5174)) {
    Write-Host "⚠️  Port 5173/5174 is already in use. Frontend might already be running." -ForegroundColor Yellow
} else {
    Write-Host "🎨 Starting Frontend Server..." -ForegroundColor Cyan
    Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WorkingDirectory "project" -WindowStyle Hidden
    Start-Sleep 3
}

Write-Host ""
Write-Host "✅ Walmart Whisper is starting up!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Access URLs:" -ForegroundColor White
Write-Host "   🌐 Frontend: http://localhost:5174" -ForegroundColor Cyan
Write-Host "   🔧 Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "   📚 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔍 Health Check:" -ForegroundColor White
Write-Host "   Invoke-WebRequest -Uri 'http://localhost:8000/api/health'" -ForegroundColor Gray
Write-Host ""

# Test health endpoint
try {
    Start-Sleep 5
    Write-Host "🏥 Testing backend health..." -ForegroundColor Yellow
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Backend is healthy!" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Backend health check failed. Please wait for startup to complete." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 Ready to use! Open http://localhost:5174 in your browser" -ForegroundColor Green
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
