@echo off
echo ============================================================
echo   web-intel-bot - install dependencies
echo ============================================================
echo.

REM Check Python
where python >nul 2>nul
if errorlevel 1 (
    echo [X] Python not found.
    echo     Install from https://www.python.org/downloads
    echo     Be sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)

echo [OK] Python is installed:
python --version
echo.

REM Make sure pip exists; if not, bootstrap it
echo [1/3] Checking pip...
python -m pip --version >nul 2>nul
if errorlevel 1 (
    echo     pip not found, installing via ensurepip...
    python -m ensurepip --upgrade
    if errorlevel 1 (
        echo.
        echo [X] ensurepip failed. Please reinstall Python and make sure
        echo     the "pip" option is checked during installation.
        echo     Download: https://www.python.org/downloads
        pause
        exit /b 1
    )
)
echo [OK] pip is available.
echo.

echo [2/3] Upgrading pip...
python -m pip install --upgrade pip

echo.
echo [3/3] Installing requirements...
python -m pip install -r "%~dp0requirements.txt"
if errorlevel 1 (
    echo.
    echo [X] Failed to install requirements. See errors above.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Done. Next steps:
echo     1. Copy .env.template to .env
echo     2. Fill in your API keys in .env
echo     3. Double-click run_dry.bat (test) or run.bat (with email)
echo ============================================================
echo.
pause
