#!/bin/bash
# SentraX IDS - Startup Script
# This script starts both the FastAPI backend and the React/Vite frontend.

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting SentraX IDS System...${NC}"

# Function to cleanly shut down both processes on exit
cleanup() {
    echo -e "\n${BLUE}Shutting down SentraX IDS...${NC}"
    kill $(jobs -p) 2>/dev/null
    exit
}

# Trap SIGINT and SIGTERM to run cleanup
trap cleanup SIGINT SIGTERM

# Start FastAPI Backend
echo -e "${GREEN}[Backend] Starting FastAPI Server...${NC}"
python3 -m uvicorn api:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to initialize
sleep 2

# Start React Frontend
echo -e "${GREEN}[Frontend] Starting Vite Dev Server...${NC}"
cd frontend && npm run dev -- --host &
FRONTEND_PID=$!

echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}SentraX IDS is now running!${NC}"
echo -e "${BLUE}Backend API:${NC} http://localhost:8000"
echo -e "${BLUE}Frontend UI:${NC} http://localhost:5173"
echo -e "${BLUE}=========================================${NC}"
echo -e "Press Ctrl+C to stop both servers."

# Wait for background processes
wait $BACKEND_PID
wait $FRONTEND_PID
