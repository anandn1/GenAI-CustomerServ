#!/bin/bash

# Walmart Whisper - Development Startup Script

echo "🚀 Starting Walmart Whisper Development Environment..."

# Function to check if port is in use
check_port() {
    netstat -an | grep ":$1 " > /dev/null 2>&1
}

# Check if backend is already running
if check_port 8000; then
    echo "⚠️  Port 8000 is already in use. Backend might already be running."
else
    echo "🔧 Starting Backend Server on port 8000..."
    cd backend
    python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
    sleep 3
fi

# Check if frontend is already running
if check_port 5173 || check_port 5174; then
    echo "⚠️  Port 5173/5174 is already in use. Frontend might already be running."
else
    echo "🎨 Starting Frontend Server..."
    cd project
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    sleep 3
fi

echo ""
echo "✅ Walmart Whisper is starting up!"
echo ""
echo "📋 Access URLs:"
echo "   🌐 Frontend: http://localhost:5174"
echo "   🔧 Backend:  http://localhost:8000"
echo "   📚 API Docs: http://localhost:8000/docs"
echo ""
echo "🔍 Health Check:"
echo "   curl http://localhost:8000/api/health"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for user interrupt
wait
