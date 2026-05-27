@echo off
setlocal

cd /d "%~dp0it_backend"

if exist ".\venv\Scripts\python.exe" (
  ".\venv\Scripts\python.exe" manage.py ai_auto_review --loop --interval 20
) else (
  python manage.py ai_auto_review --loop --interval 20
)

endlocal
