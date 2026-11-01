@echo off
setlocal
cd /d "%~dp0"
title Drama Downloader Studio

python run_app.py
if errorlevel 1 (
    echo.
    echo [ERROR] Application exited with error code %errorlevel%.
    pause
)
endlocal
