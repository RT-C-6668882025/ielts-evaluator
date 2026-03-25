@echo off
chcp 65001
cls
echo ==========================================
echo    Starting IELTS Evaluator Backend
echo ==========================================
echo.

cd backend

echo Checking dependencies...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Dependencies not installed!
    echo Please run install-deps.bat first
    pause
    exit /b 1
)

echo Dependencies check passed
echo.
echo Starting backend server...
echo URL: http://localhost:8000
echo.
echo Press Ctrl+C to stop server
echo.

python main.py

pause
