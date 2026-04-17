@echo off
REM Quick start script for Document Intelligence Pipeline (Windows)

setlocal enabledelayedexpansion

echo.
echo ==================================
echo Document Intelligence Pipeline
echo Quick Start Setup (Windows)
echo ==================================
echo.

REM Check for Docker
echo 1. Checking prerequisites...
docker --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Docker not found!
    echo Install Docker Desktop from https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)
echo.✓ Docker found

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)
echo ✓ Python found: %python --version%

REM Create .env file
echo.
echo 2. Setting up environment...
if not exist .env (
    copy .env.example .env
    echo.
    echo ⚠️  Created .env file - PLEASE ADD YOUR OPENAI_API_KEY
    echo    Edit .env and set: OPENAI_API_KEY=sk-...
    echo.
    pause
) else (
    echo ✓ .env file exists
)

REM Start Qdrant
echo.
echo 3. Starting Qdrant...
docker-compose up -d
echo ✓ Qdrant started on port 6333
timeout /t 2 /nobreak

REM Install dependencies
echo.
echo 4. Installing dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed

echo.
echo ==================================
echo Setup Complete!
echo ==================================
echo.
echo Next steps:
echo.
echo 1. Make sure you have OPENAI_API_KEY in .env
echo.
echo 2. Start the API server (Terminal 1):
echo    python -m uvicorn src.main:app --reload --port 8000
echo.
echo 3. Start the Streamlit dashboard (Terminal 2):
echo    streamlit run dashboard/app.py
echo.
echo 4. Then visit http://localhost:8501 to use the dashboard
echo.
echo Sample documents are in: sample_docs/
echo.
pause
