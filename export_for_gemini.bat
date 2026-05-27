@echo off
setlocal

set ROOT=%~dp0
set OUT=%ROOT%gemini_upload

echo [1/3] Preparing output folder: %OUT%
if exist "%OUT%" rmdir /s /q "%OUT%"
mkdir "%OUT%"

echo [2/3] Copying backend (excluding venv/media/cache)...
robocopy "%ROOT%it_backend" "%OUT%\it_backend" /E /XD "venv" "media" "__pycache__" ".idea" /XF "*.pyc" >nul

echo [3/3] Copying frontend (excluding node_modules/dist)...
robocopy "%ROOT%vite-project" "%OUT%\vite-project" /E /XD "node_modules" "dist" ".vscode" "__pycache__" /XF "*.map" >nul

if exist "%ROOT%.gitignore" copy "%ROOT%.gitignore" "%OUT%\.gitignore" >nul
if exist "%ROOT%run_backend.bat" copy "%ROOT%run_backend.bat" "%OUT%\run_backend.bat" >nul
if exist "%ROOT%run_ai_auto_review_loop.bat" copy "%ROOT%run_ai_auto_review_loop.bat" "%OUT%\run_ai_auto_review_loop.bat" >nul

echo.
echo Done. Upload this folder to GitHub: %OUT%
pause

