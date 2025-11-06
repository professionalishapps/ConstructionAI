@echo off
REM Development startup script for Windows

echo ====================================
echo Construction AI - Development Setup
echo ====================================
echo.

echo [1/3] Starting Docker services...
cd infrastructure\docker
docker-compose up -d
cd ..\..

echo.
echo [2/3] Starting Backend (FastAPI)...
start cmd /k "cd backend && uvicorn main:app --reload"

echo.
echo [3/3] Starting Frontend (Vite)...
timeout /t 2 /nobreak > nul
start cmd /k "cd frontend && npm run dev"

echo.
echo ====================================
echo All services started!
echo ====================================
echo Backend API: http://localhost:8000
echo API Docs:    http://localhost:8000/docs
echo Frontend:    http://localhost:5173
echo ====================================
echo.
echo Press any key to stop all services...
pause > nul

echo.
echo Stopping services...
cd infrastructure\docker
docker-compose down
cd ..\..
