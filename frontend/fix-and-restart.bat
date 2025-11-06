@echo off
echo ==========================================
echo Fixing Vite/React Import Issues
echo ==========================================
echo.

echo Step 1: Stopping any running Vite processes...
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak > nul

echo Step 2: Clearing Vite cache...
if exist "node_modules\.vite" (
    rmdir /s /q "node_modules\.vite"
    echo   - Cleared .vite cache
)

echo Step 3: Clearing dist folder...
if exist "dist" (
    rmdir /s /q "dist"
    echo   - Cleared dist folder
)

echo Step 4: Reinstalling dependencies...
call npm install
if %errorlevel% neq 0 (
    echo ERROR: npm install failed
    pause
    exit /b 1
)

echo.
echo Step 5: Starting dev server...
echo ==========================================
echo If browser doesn't auto-open, go to:
echo http://localhost:5173
echo.
echo Then do a HARD REFRESH (Ctrl+Shift+R)
echo ==========================================
echo.
npm run dev
