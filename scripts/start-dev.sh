#!/bin/bash

# Development startup script for Unix/Linux/Mac

echo "===================================="
echo "Construction AI - Development Setup"
echo "===================================="
echo ""

echo "[1/3] Starting Docker services..."
cd infrastructure/docker
docker-compose up -d
cd ../..

echo ""
echo "[2/3] Starting Backend (FastAPI)..."
cd backend
uvicorn main:app --reload &
BACKEND_PID=$!
cd ..

echo ""
echo "[3/3] Starting Frontend (Vite)..."
sleep 2
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "===================================="
echo "All services started!"
echo "===================================="
echo "Backend API: http://localhost:8000"
echo "API Docs:    http://localhost:8000/docs"
echo "Frontend:    http://localhost:5173"
echo "===================================="
echo ""
echo "Press Ctrl+C to stop all services..."

# Trap SIGINT and SIGTERM to clean up
trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; cd infrastructure/docker; docker-compose down; cd ../..; exit" SIGINT SIGTERM

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
