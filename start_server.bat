@echo off
echo [*] Activating virtual environment ...
call .venv\Scripts\activate
if %ERRORLEVEL% NEQ 0 (
    echo [!] Failed to activate venv. Did you run install_dependencies.bat first?
    pause
    exit /b 1
)

echo [*] Starting ClaraHQ backend on http://127.0.0.1:8000 ...
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 --app-dir backend

pause