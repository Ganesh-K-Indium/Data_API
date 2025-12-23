#!/bin/bash

# Data API Frontend Startup Script

echo "🚀 Starting Data API Frontend Dashboard..."
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo ""
fi

# Check if backend is running
echo "🔍 Checking backend API..."
if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    echo "✅ Backend API is running on http://localhost:8000"
else
    echo "⚠️  Warning: Backend API is not responding on http://localhost:8000"
    echo "   Please start the backend API first:"
    echo "   cd ../api_services && ./start.sh"
    echo ""
fi

echo ""
echo "📊 Starting frontend development server..."
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo ""

npm run dev
