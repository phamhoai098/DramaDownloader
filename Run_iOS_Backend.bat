@echo off
title DramaDownloader - API Server cho iOS PWA
color 0B
chcp 65001 >nul

echo ========================================================
echo    DramaDownloader Studio - API Backend Server iOS
echo ========================================================
echo.
echo IP may tinh trong mang Wi-Fi cua ban: 192.168.1.38
echo Cong ket noi (Port): 8000
echo.
echo URL ket noi cho dien thoai iPhone:
echo http://192.168.1.38:8000
echo.
echo Hay giu cua so nay mo khi dung Web App tren iPhone...
echo ========================================================
echo.

python ios_project/backend_server.py
pause
