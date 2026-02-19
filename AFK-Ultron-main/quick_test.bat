@echo off
REM Quick Test Script for AFK-Ultron System
echo ======================================================================
echo AFK-ULTRON QUICK TEST
echo ======================================================================
echo.

cd /d "%~dp0CommandPanel"

echo [1/3] Checking JSON file...
if exist "data\live_feed.json" (
    echo     ✅ JSON file exists
    for %%A in (data\live_feed.json) do echo     Size: %%~zA bytes, Modified: %%~tA
) else (
    echo     ❌ JSON file not found
    echo     Run app.py first to create detections
    goto :end
)

echo.
echo [2/3] Checking image annotations...
python compare_frames.py 2>nul
if errorlevel 1 (
    echo     ⚠️  Could not verify image
) else (
    echo     ✅ Image verification complete
)

echo.
echo [3/3] Running full sync check...
python verify_sync.py

echo.
echo ======================================================================
echo TEST COMPLETE
echo ======================================================================

:end
pause
