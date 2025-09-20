@echo off
echo Starting Smart Classroom & Timetable Scheduler...

echo Starting Backend Server...
start "Backend Server" cmd /k "cd backend && venv\Scripts\activate && python run.py"

timeout /t 3 /nobreak > nul

echo Starting Frontend Server...
start "Frontend Server" cmd /k "cd frontend && npm start"

echo.
echo Both servers are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
pause