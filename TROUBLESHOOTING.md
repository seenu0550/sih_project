# 🔧 Troubleshooting Guide

## Registration Failed Error

If you see "Registration failed" error, follow these steps:

### 1. Check MongoDB
```bash
# Make sure MongoDB is running
# Download from: https://www.mongodb.com/try/download/community
# Start MongoDB service
```

### 2. Run Fix Script
```bash
# Run this to fix all issues
fix_and_start.bat
```

### 3. Manual Steps
```bash
# Backend
cd backend
python test_connection.py
python main.py

# Frontend (new terminal)
cd frontend
npm start
```

### 4. Use Existing Account
- Username: `admin`
- Password: `admin123`

## Common Issues

### Port Already in Use
- Kill processes on ports 3000 and 8000
- Or change ports in the code

### MongoDB Not Running
- Install MongoDB Community Edition
- Start MongoDB service
- Default connection: mongodb://localhost:27017

### Dependencies Missing
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### CORS Errors
- Backend CORS is set to allow all origins
- Check if backend is running on port 8000

## Quick Fix Commands

```bash
# Kill processes on ports
netstat -ano | findstr :8000
taskkill /PID <PID> /F

netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Restart everything
fix_and_start.bat
```

## Success Indicators

✅ Backend running: http://localhost:8000 shows API message
✅ Frontend running: http://localhost:3000 shows login page
✅ Database connected: No connection errors in backend console
✅ Registration works: Can create new accounts
✅ Login works: Can access dashboard

## Contact
If issues persist, check the console logs for specific error messages.