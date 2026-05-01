@echo off
:: Move to the directory where the batch file is located
cd /d "%~dp0"

echo [1/3] Checking environment...
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found at .venv\Scripts\python.exe
    pause
    exit /b
)

echo [2/3] Activating environment...
:: Set local paths for this session
set "VIRTUAL_ENV=%~dp0.venv"
set "PATH=%~dp0.venv\Scripts;%PATH%"

echo [3/3] Launching Streamlit...
echo (If this window closes, please check for errors below)
echo.

:: Run python directly to ensure we use the venv's interpreter
python -m streamlit run app.py

echo.
echo [PROCESS ENDED]
if %ERRORLEVEL% neq 0 (
    echo The app exited with an error code: %ERRORLEVEL%
)
pause
