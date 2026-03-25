@echo off
chcp 65001 >nul
echo ==========================================
echo    IELTS Evaluator - 前端服务器
echo ==========================================
echo.

cd /d "%~dp0frontend"

echo 启动前端服务器...
echo 访问地址: http://localhost:3000
echo.
echo 按 Ctrl+C 停止服务
echo.

python -m http.server 3000

pause
