#!/bin/bash
echo "==========================================================="
echo "🛡️  STARTING SENTINELFIN ENTERPRISE DASHBOARD"
echo "==========================================================="
echo "Starting FastAPI Backend (Port 8000)..."
python3 app.py &
BACKEND_PID=$!

echo "Starting React Frontend (Port 5173)..."
cd dashboard
npm install
npm run dev &
FRONTEND_PID=$!

echo "==========================================================="
echo "✅ SYSTEM ONLINE!"
echo "👉 Open your browser to: http://localhost:5173"
echo "==========================================================="
echo "Press CTRL+C to stop both servers."

trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
