@echo off
echo Starting Productivity Scheduler...
cd /d "%~dp0backend"
start "Scheduler API" python -m uvicorn app.main:app --reload
timeout /t 3 /nobreak >nul
start "" "http://localhost:8000"
