@echo off
echo Starting Multi-Agent System...

REM Start the API server in background
echo Starting API server...
start /B python main.py

REM Wait a moment for the API to start
timeout /t 3 /nobreak >nul

REM Start Streamlit
echo Starting Streamlit UI...
streamlit run app.py

echo Application stopped.
pause
