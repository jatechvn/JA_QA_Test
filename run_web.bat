@echo off
chcp 65001 >nul
title CESBG Vietnam - Web Mobile QA Server 2026
echo ======================================================================
echo    DANG KHOI DONG WEB SERVER ON THI TO TRUONG CESBG 2026 (MOBILE)
echo ======================================================================
echo.
python -X utf8 web_server.py
if errorlevel 1 (
    echo.
    echo Co loi xay ra khi khoi dong Web Server.
    pause
)
