@echo off
chcp 65001 >nul
echo.
echo ==============================================
echo   创建 IELTS Evaluator 桌面快捷方式
echo ==============================================
echo.

REM 检查 PowerShell
powershell -Command "Get-Host" >nul 2>&1
if errorlevel 1 (
    echo [错误] 无法运行 PowerShell
    pause
    exit /b 1
)

REM 运行 PowerShell 脚本
echo 正在创建快捷方式...
powershell -ExecutionPolicy Bypass -File "%~dp0create-shortcut.ps1"

if errorlevel 1 (
    echo.
    echo [错误] 创建快捷方式失败
    pause
    exit /b 1
)

echo.
echo 完成！
timeout /t 2 >nul
