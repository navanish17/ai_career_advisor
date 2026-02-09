@echo off
echo Starting AI Career Advisor Development Environment...

REM Set Project Root
set PROJECT_ROOT=%~dp0
cd /d "%PROJECT_ROOT%"

REM Activate Conda Environment (Adjust path if needed)
call D:\anaconda\Scripts\activate.bat D:\anaconda\envs\ai-career

REM Set PYTHONPATH for Backend
set PYTHONPATH=%PROJECT_ROOT%

echo 1. Starting Backend Server...
start "Backend Server" cmd /k "cd backend && uvicorn src.ai_career_advisor.main:app --reload --host 0.0.0.0 --port 8000"

echo 2. Starting Frontend Server...
start "Frontend Server" cmd /k "cd frontend && npm run dev"

echo ===================================================
echo Environment Started!
echo Frontend: http://localhost:8080
echo Backend:  http://localhost:8000
echo ===================================================
pause
