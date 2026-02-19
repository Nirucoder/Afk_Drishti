@echo off
title AFK-Ultron Surveillance System
color 0A

echo ========================================================
echo        STARTING AFK-ULTRON SURVEILLANCE SYSTEM
echo ========================================================
echo.

:: 1. Start the Command Panel Server (in background)
echo [1/3] Launching Command Panel Server...
start "Command Panel Server" /min cmd /k "cd CommandPanel && python server.py"

:: Wait 3 seconds for server to initialize
timeout /t 3 /nobreak >nul

:: 2. Open the Dashboard in Default Browser
echo [2/3] Opening Dashboard interface...
start http://localhost:5000

:: 3. Start the Drone Vision (Ultron)
echo [3/3] Initializing Drone Vision AI...
cd Ultron
python app.py

:: If the app closes, pause to see errors
pause
