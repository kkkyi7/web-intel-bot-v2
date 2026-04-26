@echo off
cd /d "%~dp0"

echo ============================================================
echo   web-intel-bot - DRY RUN (no email sent)
echo ============================================================
echo.

python daily_digest.py --dry-run

echo.
echo HTML report saved in the data-samples folder (by date).
echo Open digest.html in your browser to preview.
pause
