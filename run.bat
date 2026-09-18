@echo off
setlocal
if /i "%~1"=="--in-terminal" goto launch
if defined WT_SESSION goto launch
where wt.exe >nul 2>&1
if errorlevel 1 goto powershell
wt.exe -w new -d "%~dp0." cmd.exe /d /c ""%~f0" --in-terminal"
if not errorlevel 1 exit /b 0

:powershell
where powershell.exe >nul 2>&1
if errorlevel 1 goto launch
set "JA_QA_LAUNCHER=%~f0"
start "" powershell.exe -NoLogo -NoProfile -Command "& $env:JA_QA_LAUNCHER '--in-terminal'"
if not errorlevel 1 exit /b 0

:launch
cd /d "%~dp0"
chcp 65001 >nul
title CESBG Vietnam - On Thi To Truong 2026
echo Dang khoi dong chuong trinh On Thi To Truong CESBG 2026...
python -X utf8 app.py
if errorlevel 1 (
    echo.
    echo Co loi xay ra khi chay chuong trinh.
    pause
)
