@echo off
setlocal
title SIGDEI - Inicializador local

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

start "SIGDEI - BACKEND" cmd /k ""%PYTHON%" "%BASE%backend\manage.py" runserver 0.0.0.0:8000"
start "SIGDEI - FRONTEND" cmd /k ""%PYTHON%" -m http.server 5500 --bind 0.0.0.0 --directory "%BASE%frontend""
timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:5500/index.html"
