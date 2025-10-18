import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import Classrooms from './components/Classrooms';
import Subjects from './components/Subjects';
import Faculty from './components/Faculty';
import Batches from './components/Batches';
import TimetableGenerator from './components/TimetableGenerator';
import TimetableView from './components/TimetableView';
import BatchTimetable from './components/BatchTimetable';
import Profile from './components/Profile';
import { AuthProvider, useAuth } from './context/AuthContext';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function ProtectedRoute({ children, adminOnly = false }) {
  const { token, user } = useAuth();
  
  if (!token) {
    return <Navigate to="/login" />;
  }
  
  if (adminOnly && user?.role !== 'admin') {
    return <Navigate to="/" />;
  }
  
  return children;
}

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
            <Route path="/classrooms" element={
              <ProtectedRoute adminOnly={true}>
                <Classrooms />
              </ProtectedRoute>
            } />
            <Route path="/subjects" element={
              <ProtectedRoute adminOnly={true}>
                <Subjects />
              </ProtectedRoute>
            } />
            <Route path="/faculty" element={
              <ProtectedRoute adminOnly={true}>
                <Faculty />
              </ProtectedRoute>
            } />
            <Route path="/batches" element={
              <ProtectedRoute adminOnly={true}>
                <Batches />
              </ProtectedRoute>
            } />
            <Route path="/generate-timetable" element={
              <ProtectedRoute adminOnly={true}>
                <TimetableGenerator />
              </ProtectedRoute>
            } />
            <Route path="/timetables" element={
              <ProtectedRoute>
                <TimetableView />
              </ProtectedRoute>
            } />
            <Route path="/batch-timetable" element={
              <ProtectedRoute>
                <BatchTimetable />
              </ProtectedRoute>
            } />
            <Route path="/profile" element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            } />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;