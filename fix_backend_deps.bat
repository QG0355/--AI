@echo off
setlocal

cd /d "%~dp0it_backend"

if exist ".\venv\Scripts\python.exe" (
  ".\venv\Scripts\python.exe" -m pip install -U pip
  ".\venv\Scripts\python.exe" -m pip install -U cryptography pymysql
) else (
  python -m pip install -U pip
  python -m pip install -U cryptography pymysql
)

endlocal
