@echo off
chcp 65001
cls
echo ==========================================
echo    IELTS Evaluator - Quick Start
echo ==========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

REM Check dependencies
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Dependencies not installed.
    echo [INFO] Running install-deps.bat first...
    echo.
    call install-deps.bat
)

echo.
echo ==========================================
echo    Starting Services...
echo ==========================================
echo.

REM Start backend in new window
start "IELTS Backend" cmd /c "cd backend && python main.py"

REM Wait for backend
timeout /t 3 >nul

REM Start frontend in new window
start "IELTS Frontend" cmd /c "cd frontend && python -m http.server 3000"

REM Wait for frontend
timeout /t 2 >nul

echo.
echo ==========================================
echo    Services Started!
echo ==========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Opening browser...
start http://localhost:3000
echo.
pause
