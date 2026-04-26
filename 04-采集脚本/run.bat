@echo off
cd /d "%~dp0"

if not exist .env (
    echo.
    echo [X] .env file not found.
    echo     Copy .env.template to .env and fill in your API keys first.
    echo.
    pause
    exit /b 1
)

echo ============================================================
echo   web-intel-bot - fetching and analyzing
echo ============================================================
echo.

python daily_digest.py %*

echo.
echo ============================================================
echo   Finished. HTML report saved in the data-samples folder (by date).
echo ============================================================
pause
