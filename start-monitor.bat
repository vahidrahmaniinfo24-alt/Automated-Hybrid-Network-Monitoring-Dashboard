@echo off
cd /d "%~dp0"

start "Windows Infrastructure Monitor" /min cmd /c ^
""C:\Users\meins\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe" -m uvicorn app:app --reload --host 127.0.0.1 --port 8000"

timeout /t 5 /nobreak >nul

start "" "http://127.0.0.1:8000"

exit