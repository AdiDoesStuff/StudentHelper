@echo off
setlocal enabledelayedexpansion

:: Move to the directory where the batch file is located
cd /d "%~dp0"

echo.
echo ========================================
echo   StudentHelper Installation Script
echo ========================================
echo.

echo [1/4] Checking for virtual environment...
if not exist ".venv" (
    echo [INFO] Creating virtual environment (.venv)...
    python -m venv .venv
    if !ERRORLEVEL! neq 0 (
        echo [ERROR] Failed to create virtual environment.
        echo Make sure Python is installed and in your PATH.
        pause
        exit /b !ERRORLEVEL!
    )
) else (
    echo [INFO] Virtual environment already exists.
)

echo [2/4] Activating environment...
call .venv\Scripts\activate
if !ERRORLEVEL! neq 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b !ERRORLEVEL!
)

echo [3/4] Upgrading pip...
python -m pip install --upgrade pip

echo [4/4] Installing requirements from requirements.txt...
pip install -r requirements.txt
if !ERRORLEVEL! neq 0 (
    echo [ERROR] Failed to install requirements.
    pause
    exit /b !ERRORLEVEL!
)

echo.
echo ========================================
echo   [SUCCESS] Setup complete!
echo   You can now run 'run_app.bat'
echo ========================================
echo.
pause
