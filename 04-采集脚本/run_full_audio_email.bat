@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================================
echo   web-intel-bot - FULL RUN + TTS Audio + Email
echo ============================================================
echo.

python daily_digest.py --tts

echo.
echo Done. Check your email inbox for the digest HTML attachment.
pause
