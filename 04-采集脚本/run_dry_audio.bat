@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================================
echo   web-intel-bot - DRY RUN + TTS Audio (commute mode)
echo ============================================================
echo.

python daily_digest.py --dry-run --tts

echo.
echo Done. Open the HTML in 05-data/YYYY-MM-DD/digest.html
echo The HTML is self-contained (audio embedded), just double-click to play.
pause
