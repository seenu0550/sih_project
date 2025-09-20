@echo off
echo Starting Smart Classroom & Timetable Scheduler...

echo.
echo Setting up sample data...
cd backend
python setup_complete_data.py

echo.
echo Starting backend server...
start "Backend Server" cmd /k "python main.py"

echo.
echo Waiting for backend to start...
timeout /t 3 /nobreak > nul

echo.
echo Starting frontend...
cd ..\frontend
start "Frontend Server" cmd /k "npm start"

echo.
echo ✅ Both servers are starting!
echo 🌐 Frontend: http://localhost:3000
echo 🔧 Backend API: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo 👤 Login: admin / admin123
echo.
pause