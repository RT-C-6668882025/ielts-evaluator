@echo off
chcp 65001 >nul
echo ==========================================
echo    IELTS Evaluator - 雅思评估助手
echo ==========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo [1/3] 正在检查环境...

REM 切换到后端目录
cd /d "%~dp0backend"

REM 创建虚拟环境（如果不存在）
if not exist "venv" (
    echo [2/3] 正在创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo [3/3] 正在启动服务...
call venv\Scripts\activate

REM 安装依赖
pip install -q -r requirements.txt

REM 检查 API Key
if "%DEEPSEEK_API_KEY%"=="" (
    echo.
    echo [警告] 未设置 DEEPSEEK_API_KEY 环境变量
    echo 请在启动前设置：set DEEPSEEK_API_KEY=your-api-key
    echo.
)

echo.
echo ==========================================
echo 服务启动中...
echo 后端地址: http://localhost:8000
echo 前端地址: http://localhost:3000
echo ==========================================
echo.
echo 按 Ctrl+C 停止服务
echo.

REM 启动后端服务
python main.py

pause
