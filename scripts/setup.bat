@echo off
REM Initial project setup script for Windows

echo ====================================
echo Construction AI - Initial Setup
echo ====================================
echo.

echo [1/4] Installing frontend dependencies...
cd frontend
call npm install
cd ..

echo.
echo [2/4] Installing backend dependencies...
cd backend
pip install -r requirements.txt
cd ..

echo.
echo [3/4] Starting Docker services...
cd infrastructure\docker
docker-compose up -d
cd ..\..

echo.
echo [4/4] Initializing database...
timeout /t 5 /nobreak > nul
cd backend
python scripts\init_db.py
cd ..

echo.
echo ====================================
echo Setup complete!
echo ====================================
echo.
echo To start development:
echo   Option 1: npm run dev:all  (from root)
echo   Option 2: scripts\start-dev.bat
echo.
echo ====================================
pause
