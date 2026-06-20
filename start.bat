@echo off
:: MindMate Full Stack Launcher (FastAPI + Next.js)

cd /d "%~dp0"

echo [1/3] Activating AI Environment for Backend...
call "C:\Users\em875\anaconda3\Scripts\activate.bat" AI

echo [2/3] Starting FastAPI Server...
start "MindMate API" cmd /k "python api.py"

echo Waiting 4 seconds for API to load...
timeout /t 4 /nobreak > nul

echo [3/3] Starting Next.js Frontend (React)...
cd /d "%~dp0mindmate-frontend"
npm run dev