@echo off
chcp 65001
cls
echo ==========================================
echo    Installing IELTS Evaluator Dependencies
echo ==========================================
echo.

echo [1/3] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+
    pause
    exit /b 1
)
echo Python check passed
echo.

echo [2/3] Installing dependencies...
echo This may take a few minutes, please wait...
echo.

pip install fastapi uvicorn httpx pydantic python-multipart --no-cache-dir

if errorlevel 1 (
    echo.
    echo [ERROR] Installation failed, trying with China mirror...
    pip install fastapi uvicorn httpx pydantic python-multipart -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
)

echo.
echo [3/3] Verifying installation...
python -c "import fastapi; print('FastAPI version:', fastapi.__version__)" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Installation verification failed
    pause
    exit /b 1
)

echo.
echo ==========================================
echo    Dependencies installed successfully!
echo ==========================================
echo.
echo Now you can start the backend server:
echo   cd backend
echo   python main.py
echo.
pause
