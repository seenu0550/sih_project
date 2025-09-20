@echo off
echo Setting up Smart Classroom & Timetable Scheduler...

echo.
echo Setting up Backend...
cd backend
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
cd ..

echo.
echo Setting up Frontend...
cd frontend
call npm install
cd ..

echo.
echo Setup complete!
echo.
echo To start the application:
echo 1. Start MongoDB service
echo 2. Run backend: cd backend && python run.py
echo 3. Run frontend: cd frontend && npm start
echo.
pause