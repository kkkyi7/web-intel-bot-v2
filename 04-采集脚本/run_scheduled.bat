@echo off
REM ============================================================
REM   定时任务专用：跑完即退，不弹 pause、不留终端
REM   每天 9:30 由 Windows 任务计划程序触发
REM ============================================================
chcp 65001 >nul
cd /d "%~dp0"

REM 把日志写到当天的 log 文件，方便事后排错
set LOG_DIR=%~dp0..\06-定时日志
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
set LOG_FILE=%LOG_DIR%\%date:~0,4%-%date:~5,2%-%date:~8,2%.log

echo [%date% %time%] === 定时任务开始 === >> "%LOG_FILE%"
python daily_digest.py --tts >> "%LOG_FILE%" 2>&1
echo [%date% %time%] === 定时任务结束 === >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"
