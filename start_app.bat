@echo off
REM Clear CLAUDECODE environment variable
set CLAUDECODE=
REM Kill any existing Python processes
taskkill /F /IM python.exe 2>nul
taskkill /F /IM python3.exe 2>nul
REM Wait a moment
timeout /t 2 /nobreak >nul
REM Start Streamlit
cd /d "c:\Users\Tertiary\Downloads\wsq-casl-cp-generator-main\wsq-casl-cp-generator-main"
start /b python -m streamlit run streamlit_app.py
echo Streamlit started! Check http://localhost:8501
pause
