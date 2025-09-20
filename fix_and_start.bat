@echo off
echo 🔧 Fixing and Starting Smart Classroom Scheduler...

echo.
echo 📋 Checking MongoDB connection...
cd backend
python test_connection.py

echo.
echo 🗃️ Setting up sample data...
python setup_complete_data.py

echo.
echo 🚀 Starting backend server on port 8000...
start "Backend Server" cmd /k "python main.py"

echo.
echo ⏳ Waiting for backend to initialize...
timeout /t 5 /nobreak > nul

echo.
echo 🌐 Starting frontend on port 3000...
cd ..\frontend
start "Frontend Server" cmd /k "npm start"

echo.
echo ✅ Setup Complete!
echo.
echo 🌐 Frontend: http://localhost:3000
echo 🔧 Backend: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo 👤 Default Login:
echo    Username: admin
echo    Password: admin123
echo.
echo 📝 Or register a new account!
echo.
pause