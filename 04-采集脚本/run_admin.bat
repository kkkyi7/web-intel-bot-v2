@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo web-intel-bot 本地情报后台
echo ========================================
echo.
echo 启动后打开：
echo http://127.0.0.1:7860
echo.

python admin_app.py
pause
