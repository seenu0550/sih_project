import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  Tab,
  Tabs,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import { useAuth } from '../context/AuthContext';
import { authAPI } from '../services/api';

function TabPanel({ children, value, index }) {
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function Login() {
  const [tab, setTab] = useState(0);
  const [loginData, setLoginData] = useState({ username: '', password: '' });
  const [registerData, setRegisterData] = useState({
    username: '',
    email: '',
    password: '',
    role: 'student'
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    // Create floating particles
    const createParticles = () => {
      const particlesContainer = document.querySelector('.particles');
      if (particlesContainer) {
        const particleCount = 30;
        for (let i = 0; i < particleCount; i++) {
          const particle = document.createElement('div');
          particle.style.cssText = `
            position: absolute;
            width: 4px;
            height: 4px;
            background: rgba(255, 255, 255, 0.6);
            border-radius: 50%;
            left: ${Math.random() * 100}%;
            animation: float-up ${Math.random() * 8 + 8}s infinite linear;
            animation-delay: ${Math.random() * 8}s;
          `;
          particlesContainer.appendChild(particle);
        }
      }
    };
    createParticles();
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Retry login up to 2 times if it fails
    for (let attempt = 1; attempt <= 2; attempt++) {
      try {
        const response = await authAPI.login(loginData);
        const userRole = loginData.username === 'admin' ? 'admin' : 'student';
        login(response.data.access_token, { username: loginData.username, role: userRole });
        navigate('/');
        return;
      } catch (err) {
        console.error(`Login attempt ${attempt} error:`, err);
        
        if (attempt === 2) {
          // Final attempt failed
          if (err.code === 'ERR_NETWORK') {
            setError('Cannot connect to server. Please make sure the backend is running on port 8000.');
          } else {
            setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
          }
        } else {
          // Wait before retry
          await new Promise(resolve => setTimeout(resolve, 1000));
        }
      }
    }
    
    setLoading(false);
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await authAPI.register(registerData);
      setTab(0);
      setError('');
      alert('Registration successful! Please login.');
    } catch (err) {
      console.error('Registration error:', err);
      if (err.code === 'ERR_NETWORK') {
        setError('Cannot connect to server. Please make sure the backend is running on port 8000.');
      } else {
        setError(err.response?.data?.detail || 'Registration failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        position: 'relative',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 2,
        overflow: 'hidden'
      }}
    >
      <style>
        {`
          @keyframes float-up {
            0% { transform: translateY(100vh) rotate(0deg); opacity: 0; }
            10% { opacity: 1; }
            90% { opacity: 1; }
            100% { transform: translateY(-100px) rotate(360deg); opacity: 0; }
          }
          .particles {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            z-index: 1;
          }
        `}
      </style>
      
      <div className="particles"></div>
      
      <Box sx={{
        background: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(20px)',
        borderRadius: '30px',
        p: { xs: 4, sm: 6 },
        width: '35vw',
        maxWidth: '35vw',
        textAlign: 'center',
        boxShadow: '0 30px 80px rgba(0, 0, 0, 0.3)',
        border: '2px solid rgba(255, 255, 255, 0.3)',
        position: 'relative',
        zIndex: 2
      }}>
        <Box sx={{ mb: 4 }}>
          <Box sx={{
            width: 120,
            height: 80,
            margin: '0 auto 20px',
            background: 'linear-gradient(145deg, #667eea, #764ba2)',
            borderRadius: '20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '3rem',
            boxShadow: '0 15px 35px rgba(0, 0, 0, 0.2)'
          }}>
            🏛️
          </Box>
          <Typography variant="h3" sx={{
            fontWeight: 800,
            background: 'linear-gradient(45deg, #667eea, #764ba2)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            mb: 2,
            fontSize: { xs: '2rem', sm: '2.5rem' }
          }}>
            Smart Classroom Scheduler
          </Typography>
          <Typography variant="subtitle1" sx={{ color: '#555', mb: 3 }}>
            Transform your academic scheduling with intelligent automation
          </Typography>
        </Box>
        
        <Tabs value={tab} onChange={(e, newValue) => setTab(newValue)} centered sx={{
          mb: 3,
          '& .MuiTab-root': { 
            fontWeight: 'bold',
            fontSize: '1.1rem',
            textTransform: 'none'
          },
          '& .MuiTabs-indicator': { 
            background: 'linear-gradient(45deg, #667eea, #764ba2)',
            height: 3
          }
        }}>
          <Tab label="🔐 Login" />
          <Tab label="📝 Register" />
        </Tabs>

        {error && <Alert severity="error" sx={{ mt: 2, mb: 2 }}>{error}</Alert>}

        <TabPanel value={tab} index={0}>
          <form onSubmit={handleLogin}>
            <TextField
              fullWidth
              label="Username"
              margin="normal"
              value={loginData.username}
              onChange={(e) => setLoginData({ ...loginData, username: e.target.value })}

              required
              sx={{
                '& .MuiOutlinedInput-root': {
                  backgroundColor: 'rgba(255, 255, 255, 0.9)',
                  borderRadius: 2
                }
              }}
            />
            <TextField
              fullWidth
              label="Password"
              type="password"
              margin="normal"
              value={loginData.password}
              onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}

              required
              sx={{
                '& .MuiOutlinedInput-root': {
                  backgroundColor: 'rgba(255, 255, 255, 0.9)',
                  borderRadius: 2
                }
              }}
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ 
                mt: 3, 
                py: 1.5,
                borderRadius: '25px',
                background: 'linear-gradient(135deg, #4CAF50, #45a049)',
                fontSize: '1.1rem',
                fontWeight: 'bold',
                textTransform: 'none',
                boxShadow: '0 8px 25px rgba(76, 175, 80, 0.4)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #388E3C, #2E7D32)',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 12px 35px rgba(76, 175, 80, 0.6)'
                }
              }}
              disabled={loading}
            >
              {loading ? 'Connecting...' : '🚀 Login'}
            </Button>
          </form>
        </TabPanel>

        <TabPanel value={tab} index={1}>
          <form onSubmit={handleRegister}>
            <TextField
              fullWidth
              label="Username"
              margin="normal"
              value={registerData.username}
              onChange={(e) => setRegisterData({ ...registerData, username: e.target.value })}
              required
              sx={{
                '& .MuiOutlinedInput-root': {
                  backgroundColor: 'rgba(255, 255, 255, 0.8)',
                  borderRadius: 2
                }
              }}
            />
            <TextField
              fullWidth
              label="Email"
              type="email"
              margin="normal"
              value={registerData.email}
              onChange={(e) => setRegisterData({ ...registerData, email: e.target.value })}
              required
              sx={{
                '& .MuiOutlinedInput-root': {
                  backgroundColor: 'rgba(255, 255, 255, 0.8)',
                  borderRadius: 2
                }
              }}
            />
            <TextField
              fullWidth
              label="Password"
              type="password"
              margin="normal"
              value={registerData.password}
              onChange={(e) => setRegisterData({ ...registerData, password: e.target.value })}
              required
              sx={{
                '& .MuiOutlinedInput-root': {
                  backgroundColor: 'rgba(255, 255, 255, 0.8)',
                  borderRadius: 2
                }
              }}
            />
            <FormControl fullWidth margin="normal">
              <InputLabel>Role</InputLabel>
              <Select
                value={registerData.role}
                onChange={(e) => setRegisterData({ ...registerData, role: e.target.value })}
                sx={{
                  backgroundColor: 'rgba(255, 255, 255, 0.8)',
                  borderRadius: 2
                }}
              >
                <MenuItem value="student">Student</MenuItem>
                <MenuItem value="admin">Admin</MenuItem>
              </Select>
            </FormControl>
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ 
                mt: 3, 
                py: 1.5,
                borderRadius: '25px',
                background: 'linear-gradient(135deg, #2196F3, #1976D2)',
                fontSize: '1.1rem',
                fontWeight: 'bold',
                textTransform: 'none',
                boxShadow: '0 8px 25px rgba(33, 150, 243, 0.4)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #1976D2, #1565C0)',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 12px 35px rgba(33, 150, 243, 0.6)'
                }
              }}
              disabled={loading}
            >
              {loading ? 'Registering...' : '✨ Register'}
            </Button>
          </form>
        </TabPanel>
      </Box>
    </Box>
  );
}

export default Login;