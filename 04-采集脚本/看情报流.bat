@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 正在重建情报流...
python feed_build.py
echo.
start "" "..\情报流.html"
