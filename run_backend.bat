@echo off
setlocal

cd /d "%~dp0it_backend"

if exist ".\venv\Scripts\python.exe" (
  ".\venv\Scripts\python.exe" manage.py runserver
) else (
  python manage.py runserver
)

endlocal
