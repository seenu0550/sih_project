@echo off
echo Stopping existing backend processes...
taskkill /F /IM python.exe /T 2>nul
timeout /t 3 >nul

echo Starting backend...
cd backend
python main.py