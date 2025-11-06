@echo off
REM Validation script for Windows

echo ====================================
echo Construction AI - Validation Script
echo ====================================
echo.

echo [1/4] Validating Frontend Build...
cd frontend
call npm run build > nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Frontend builds successfully
) else (
    echo [FAIL] Frontend build failed
    echo Run: cd frontend ^&^& npm run build
)
cd ..

echo.
echo [2/4] Validating Backend Imports...
cd backend
python -c "import sys; sys.path.insert(0, '.'); from src.core.config import settings; print('[OK] Backend imports work')" 2>nul
if %errorlevel% neq 0 (
    echo [FAIL] Backend imports failed
    echo Run: cd backend ^&^& pip install -r requirements.txt
) else (
    echo [OK] Backend imports validated
)
cd ..

echo.
echo [3/4] Checking Docker Services...
docker ps | findstr postgres > nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] PostgreSQL is running
) else (
    echo [WARN] PostgreSQL not running
    echo Run: npm run docker:up
)

echo.
echo [4/4] Checking Ports...
netstat -an | findstr :8000 > nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Backend is running on port 8000
) else (
    echo [INFO] Backend not running
)

netstat -an | findstr :5173 > nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Frontend is running on port 5173
) else (
    echo [INFO] Frontend not running
)

echo.
echo ====================================
echo Validation Complete
echo ====================================
pause
