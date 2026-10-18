@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel% neq 0 (
  echo Install Python 3.11 or newer from python.org, then try again.
  pause
  exit /b 1
)
if not exist .venv\Scripts\python.exe py -3 -m venv .venv
.venv\Scripts\python.exe -c "import numpy" >nul 2>nul
if %errorlevel% neq 0 .venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe app.py
pause
