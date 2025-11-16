@echo off
echo [*] Creating virtual environment .venv ...
python -m venv .venv
if %ERRORLEVEL% NEQ 0 (
    echo [!] Failed to create virtual environment. Make sure Python 3.13 is installed.
    pause
    exit /b 1
)

echo [*] Activating venv and installing dependencies ...
call .venv\Scripts\activate
pip install --upgrade pip
pip install -r backend\requirements.txt

if %ERRORLEVEL% EQU 0 (
    echo [*] All dependencies installed successfully.
) else (
    echo [!] There was an error installing dependencies.
)

pause