@echo off
REM ============================================================================
REM LeniGuide Complete Startup Script
REM Starts both API and UI in separate windows
REM ============================================================================

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║          STARTING LENIGUIDE PROJECT                          ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

echo [1/2] Starting FastAPI Backend...
start "LeniGuide API" cmd /k ".\.venv\Scripts\activate && set LLM_PROVIDER=fake && uvicorn app.main:app --host 127.0.0.1 --port 8000"

echo [2/2] Waiting 5 seconds...
timeout /t 5 /nobreak >nul

echo [2/2] Starting Streamlit UI...
start "LeniGuide UI" cmd /k ".\.venv\Scripts\activate && set API_BASE_URL=http://localhost:8000 && streamlit run ui/app.py"

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                   STARTUP COMPLETE!                          ║
echo ╠══════════════════════════════════════════════════════════════╣
echo ║                                                              ║
echo ║  Wait 20-30 seconds, then open:                             ║
echo ║                                                              ║
echo ║  UI:  http://localhost:8501                                 ║
echo ║  API: http://localhost:8000/docs                            ║
echo ║                                                              ║
echo ║  Two new windows will open with logs.                       ║
echo ║  Keep both windows open while using the app.                ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

pause
