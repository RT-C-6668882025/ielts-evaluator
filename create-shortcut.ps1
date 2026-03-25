# 创建桌面快捷方式脚本
# Create Desktop Shortcut for IELTS Evaluator

$WshShell = New-Object -comObject WScript.Shell

# 获取路径
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BatchFile = Join-Path $ProjectDir "IELTS-Evaluator.bat"
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "IELTS Evaluator.lnk"

# 创建快捷方式
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $BatchFile
$Shortcut.WorkingDirectory = $ProjectDir
$Shortcut.Description = "雅思评估助手 - IELTS Evaluator"
$Shortcut.IconLocation = "%SystemRoot%\System32\shell32.dll,13"
$Shortcut.WindowStyle = 1  # 正常窗口

# 保存快捷方式
$Shortcut.Save()

Write-Host ""
Write-Host "==============================================" -ForegroundColor Green
Write-Host "  桌面快捷方式创建成功！" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Green
Write-Host ""
Write-Host "快捷方式位置: $ShortcutPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "现在你可以：" -ForegroundColor Yellow
Write-Host "  1. 双击桌面上的 'IELTS Evaluator' 图标启动" -ForegroundColor White
Write-Host "  2. 一键启动前后端服务并自动打开浏览器" -ForegroundColor White
Write-Host ""

pause
