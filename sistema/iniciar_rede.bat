@echo off
setlocal EnableDelayedExpansion
title SIGDEI - Inicializador na Rede Local

set "BASE=%~dp0"
set "PYTHON=%BASE%..\.venv\Scripts\python.exe"

if not exist "%PYTHON%" (
    if exist "%LOCALAPPDATA%\Python\bin\python.exe" (
        set "PYTHON=%LOCALAPPDATA%\Python\bin\python.exe"
    ) else (
        where py >nul 2>&1
        if not errorlevel 1 (
            set "PYTHON=py"
        ) else (
            set "PYTHON=python"
        )
    )
)

for /f "usebackq tokens=*" %%i in (`powershell -NoProfile -Command "(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike '169.254*' -and $_.IPAddress -notlike '127.*' } | Select-Object -ExpandProperty IPAddress -First 1)"`) do set "LOCAL_IP=%%i"

if "%LOCAL_IP%"=="" set "LOCAL_IP=127.0.0.1"

echo ========================================================
echo   Iniciando SIGDEI na Rede Local (0.0.0.0)
echo   Acesse no seu computador: http://127.0.0.1:5500/index.html
echo   Ou pela rede atual:       http://%LOCAL_IP%:5500/index.html
echo ========================================================

start "SIGDEI - BACKEND (REDE)" cmd /k ""%PYTHON%" "%BASE%backend\manage.py" runserver 0.0.0.0:8000"
start "SIGDEI - FRONTEND (REDE)" cmd /k ""%PYTHON%" -m http.server 5500 --bind 0.0.0.0 --directory "%BASE%frontend""
timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:5500/index.html"
