import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Paper,
  Avatar,
  Button,
  Chip
} from '@mui/material';
import SchoolIcon from '@mui/icons-material/School';
import PersonIcon from '@mui/icons-material/Person';
import RoomIcon from '@mui/icons-material/Room';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import GroupsIcon from '@mui/icons-material/Groups';
import AddIcon from '@mui/icons-material/Add';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import Layout from './Layout';
import { classroomsAPI, subjectsAPI, facultyAPI, batchesAPI, timetablesAPI } from '../services/api';

function StatCard({ title, value, icon, gradient, emoji, onClick }) {
  return (
    <Card sx={{ 
      height: '100%',
      width: '100%',
      background: gradient,
      color: 'white',
      transform: 'translateY(0)',
      transition: 'all 0.3s ease',
      cursor: onClick ? 'pointer' : 'default',
      boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
      '&:hover': { 
        transform: 'translateY(-8px)',
        boxShadow: '0 15px 35px rgba(0,0,0,0.2)'
      }
    }}
    onClick={onClick}
    >
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box>
            <Typography variant="h2" sx={{ fontWeight: 'bold', mb: 0.5 }}>{value}</Typography>
            <Typography variant="h6" sx={{ opacity: 0.9, fontWeight: 500 }}>{title}</Typography>
          </Box>
          <Box sx={{ fontSize: '48px', opacity: 0.8 }}>{emoji}</Box>
        </Box>
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center',
          justifyContent: 'space-between',
          mt: 2,
          pt: 2,
          borderTop: '1px solid rgba(255,255,255,0.2)'
        }}>
          <Typography variant="body2" sx={{ opacity: 0.8 }}>
            {onClick ? 'Click to manage' : 'Total count'}
          </Typography>
          <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', width: 40, height: 40 }}>
            {icon}
          </Avatar>
        </Box>
      </CardContent>
    </Card>
  );
}

function Dashboard() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [stats, setStats] = useState({
    classrooms: 0,
    subjects: 0,
    faculty: 0,
    batches: 0,
    timetables: 0
  });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          console.log('No token found, user needs to login');
          navigate('/login');
          return;
        }
        
        const [classrooms, subjects, faculty, batches, timetables] = await Promise.all([
          classroomsAPI.getAll(),
          subjectsAPI.getAll(),
          facultyAPI.getAll(),
          batchesAPI.getAll(),
          timetablesAPI.getAll()
        ]);

        setStats({
          classrooms: classrooms.data.length,
          subjects: subjects.data.length,
          faculty: faculty.data.length,
          batches: batches.data.length,
          timetables: timetables.data.length
        });
      } catch (error) {
        console.error('Error fetching stats:', error);
        if (error.response?.status === 401) {
          console.log('Token expired or invalid, redirecting to login');
          localStorage.removeItem('token');
          navigate('/login');
        }
      }
    };

    fetchStats();
  }, [navigate]);

  return (
    <Layout>
      {/* Hero Section */}
      <Box sx={{ 
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        borderRadius: 0,
        p: { xs: 3, md: 5 },
        pl: { xs: 4, md: 6 },
        mb: 0,
        color: 'white',
        position: 'relative',
        overflow: 'hidden',
        boxShadow: '0 20px 40px rgba(102, 126, 234, 0.3)'
      }}>
        <Box sx={{ position: 'relative', zIndex: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Typography variant="h3" sx={{ fontWeight: 'bold', mr: 2 }}>
              🎓 Smart Classroom Scheduler
            </Typography>
            <Chip 
              label="v2.0" 
              sx={{ 
                bgcolor: 'rgba(255,255,255,0.2)', 
                color: 'white',
                fontWeight: 'bold'
              }} 
            />
          </Box>
          <Typography variant="h6" sx={{ opacity: 0.9, mb: 3, maxWidth: '600px' }}>
            Intelligent Timetable Management System for Educational Excellence
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            {(!user || user.role === 'admin') ? (
              <>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => navigate('/generate-timetable')}
                  sx={{
                    bgcolor: 'rgba(255,255,255,0.2)',
                    '&:hover': { bgcolor: 'rgba(255,255,255,0.3)' },
                    backdropFilter: 'blur(10px)',
                    borderRadius: 2,
                    px: 3
                  }}
                >
                  Generate New Timetable
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<PlayArrowIcon />}
                  onClick={() => navigate('/timetables')}
                  sx={{
                    borderColor: 'rgba(255,255,255,0.5)',
                    color: 'white',
                    '&:hover': { 
                      borderColor: 'white',
                      bgcolor: 'rgba(255,255,255,0.1)'
                    },
                    borderRadius: 2,
                    px: 3
                  }}
                >
                  View Timetables
                </Button>
              </>
            ) : (
              <>
                <Button
                  variant="contained"
                  startIcon={<PlayArrowIcon />}
                  onClick={() => navigate('/timetables')}
                  sx={{
                    bgcolor: 'rgba(255,255,255,0.2)',
                    '&:hover': { bgcolor: 'rgba(255,255,255,0.3)' },
                    backdropFilter: 'blur(10px)',
                    borderRadius: 2,
                    px: 3
                  }}
                >
                  View My Timetables
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<AddIcon />}
                  onClick={() => navigate('/batch-timetable')}
                  sx={{
                    borderColor: 'rgba(255,255,255,0.5)',
                    color: 'white',
                    '&:hover': { 
                      borderColor: 'white',
                      bgcolor: 'rgba(255,255,255,0.1)'
                    },
                    borderRadius: 2,
                    px: 3
                  }}
                >
                  Check Class Schedule
                </Button>
              </>
            )}
          </Box>
        </Box>
        <Box sx={{
          position: 'absolute',
          top: -30,
          right: -30,
          fontSize: '150px',
          opacity: 0.1,
          transform: 'rotate(15deg)'
        }}>
          📚
        </Box>
      </Box>

      {/* Stats Cards */}
      <Box sx={{ p: 0, pt: 3, pl: 3 }}>
      <Grid container spacing={0} sx={{ mb: 5 }}>
        <Grid item xs={3}>
          <StatCard
            title="Classrooms"
            value={stats.classrooms}
            icon={<RoomIcon sx={{ fontSize: 24 }} />}
            gradient="linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%)"
            emoji="🏫"
            onClick={() => navigate('/classrooms')}
          />
        </Grid>
        <Grid item xs={3}>
          <StatCard
            title="Subjects"
            value={stats.subjects}
            icon={<SchoolIcon sx={{ fontSize: 24 }} />}
            gradient="linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%)"
            emoji="📖"
            onClick={() => navigate('/subjects')}
          />
        </Grid>
        <Grid item xs={3}>
          <StatCard
            title="Faculty"
            value={stats.faculty}
            icon={<PersonIcon sx={{ fontSize: 24 }} />}
            gradient="linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)"
            emoji="👨🏫"
            onClick={() => navigate('/faculty')}
          />
        </Grid>
        <Grid item xs={3}>
          <StatCard
            title="Batches"
            value={stats.batches}
            icon={<GroupsIcon sx={{ fontSize: 24 }} />}
            gradient="linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)"
            emoji="👥"
            onClick={() => navigate('/batches')}
          />
        </Grid>
      </Grid>

      {/* Feature Cards */}
      <Box sx={{ p: 3, pt: 5, pl: 3 }}>
      <Grid container spacing={4} sx={{ mb: 4 }}>
        {(!user || user.role === 'admin') ? (
          <>
            <Grid item xs={12} md={6}>
              <Card sx={{ 
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                height: '100%',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                boxShadow: '0 10px 30px rgba(102, 126, 234, 0.3)',
                '&:hover': {
                  transform: 'translateY(-5px)',
                  boxShadow: '0 20px 40px rgba(102, 126, 234, 0.4)'
                }
              }}
              onClick={() => navigate('/generate-timetable')}
              >
                <CardContent sx={{ p: 4 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                    <CalendarTodayIcon sx={{ fontSize: 40, mr: 2 }} />
                    <Typography variant="h5" sx={{ fontWeight: 'bold' }}>📅 Smart Scheduling</Typography>
                  </Box>
                  <Typography variant="body1" sx={{ opacity: 0.9, lineHeight: 1.7, mb: 3 }}>
                    Generate optimized timetables automatically with our intelligent algorithm. 
                    Consider faculty availability, classroom capacity, and student requirements 
                    to create conflict-free schedules.
                  </Typography>
                  <Button
                    variant="contained"
                    sx={{
                      bgcolor: 'rgba(255,255,255,0.2)',
                      '&:hover': { bgcolor: 'rgba(255,255,255,0.3)' },
                      borderRadius: 2
                    }}
                  >
                    Start Scheduling ⚡
                  </Button>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card sx={{ 
                background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                color: 'white',
                height: '100%',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                boxShadow: '0 10px 30px rgba(240, 147, 251, 0.3)',
                '&:hover': {
                  transform: 'translateY(-5px)',
                  boxShadow: '0 20px 40px rgba(240, 147, 251, 0.4)'
                }
              }}
              onClick={() => navigate('/timetables')}
              >
                <CardContent sx={{ p: 4 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                    <TrendingUpIcon sx={{ fontSize: 40, mr: 2 }} />
                    <Typography variant="h5" sx={{ fontWeight: 'bold' }}>📊 Analytics & Reports</Typography>
                  </Box>
                  <Typography variant="body1" sx={{ opacity: 0.9, lineHeight: 1.7, mb: 3 }}>
                    Track resource utilization, faculty workload distribution, and classroom 
                    occupancy rates. Make data-driven decisions to optimize your institution's 
                    scheduling efficiency.
                  </Typography>
                  <Button
                    variant="contained"
                    sx={{
                      bgcolor: 'rgba(255,255,255,0.2)',
                      '&:hover': { bgcolor: 'rgba(255,255,255,0.3)' },
                      borderRadius: 2
                    }}
                  >
                    View Reports 📈
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          </>
        ) : (
          <>
            <Grid item xs={12} md={6}>
              <Card sx={{ 
                background: 'linear-gradient(135deg, #4CAF50 0%, #45a049 100%)',
                color: 'white',
                height: '100%',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                boxShadow: '0 10px 30px rgba(76, 175, 80, 0.3)',
                '&:hover': {
                  transform: 'translateY(-5px)',
                  boxShadow: '0 20px 40px rgba(76, 175, 80, 0.4)'
                }
              }}
              onClick={() => navigate('/timetables')}
              >
                <CardContent sx={{ p: 4 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                    <CalendarTodayIcon sx={{ fontSize: 40, mr: 2 }} />
                    <Typography variant="h5" sx={{ fontWeight: 'bold' }}>📅 My Class Schedule</Typography>
                  </Box>
                  <Typography variant="body1" sx={{ opacity: 0.9, lineHeight: 1.7, mb: 3 }}>
                    View your personalized class timetable, upcoming lectures, and important 
                    academic schedules. Stay organized and never miss a class!
                  </Typography>
                  <Button
                    variant="contained"
                    sx={{
                      bgcolor: 'rgba(255,255,255,0.2)',
                      '&:hover': { bgcolor: 'rgba(255,255,255,0.3)' },
                      borderRadius: 2
                    }}
                  >
                    View Schedule 📚
                  </Button>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card sx={{ 
                background: 'linear-gradient(135deg, #FF9800 0%, #F57C00 100%)',
                color: 'white',
                height: '100%',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                boxShadow: '0 10px 30px rgba(255, 152, 0, 0.3)',
                '&:hover': {
                  transform: 'translateY(-5px)',
                  boxShadow: '0 20px 40px rgba(255, 152, 0, 0.4)'
                }
              }}
              onClick={() => navigate('/batch-timetable')}
              >
                <CardContent sx={{ p: 4 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                    <TrendingUpIcon sx={{ fontSize: 40, mr: 2 }} />
                    <Typography variant="h5" sx={{ fontWeight: 'bold' }}>👥 Batch Timetable</Typography>
                  </Box>
                  <Typography variant="body1" sx={{ opacity: 0.9, lineHeight: 1.7, mb: 3 }}>
                    Check your batch's complete timetable, find classmates' schedules, 
                    and coordinate study groups. Perfect for collaborative learning!
                  </Typography>
                  <Button
                    variant="contained"
                    sx={{
                      bgcolor: 'rgba(255,255,255,0.2)',
                      '&:hover': { bgcolor: 'rgba(255,255,255,0.3)' },
                      borderRadius: 2
                    }}
                  >
                    Check Batch 👨🎓
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          </>
        )}
      </Grid>

      {/* Quick Actions */}
      <Paper sx={{ 
        p: 4,
        ml: 3,
        mr: 3,
        background: 'linear-gradient(135deg, #e3ffe7 0%, #d9e7ff 100%)',
        borderRadius: 4,
        boxShadow: '0 8px 25px rgba(0,0,0,0.1)'
      }}>
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Typography variant="h4" gutterBottom sx={{ color: '#2c3e50', fontWeight: 'bold' }}>
            🌟 Quick Actions
          </Typography>
          <Typography variant="body1" sx={{ color: '#64748b', fontSize: '1.1rem', maxWidth: '600px', mx: 'auto' }}>
            Get started quickly with these common tasks
          </Typography>
        </Box>
        
        <Grid container spacing={3} justifyContent="center">
          {(!user || user.role === 'admin') ? (
            <>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  fullWidth
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => navigate('/classrooms')}
                  sx={{
                    py: 2,
                    background: 'linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%)',
                    borderRadius: 3,
                    fontSize: '1rem',
                    fontWeight: 600
                  }}
                >
                  Add Classroom 🏫
                </Button>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  fullWidth
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => navigate('/subjects')}
                  sx={{
                    py: 2,
                    background: 'linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%)',
                    borderRadius: 3,
                    fontSize: '1rem',
                    fontWeight: 600
                  }}
                >
                  Add Subject 📖
                </Button>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  fullWidth
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => navigate('/faculty')}
                  sx={{
                    py: 2,
                    background: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
                    borderRadius: 3,
                    fontSize: '1rem',
                    fontWeight: 600,
                    color: '#2c3e50'
                  }}
                >
                  Add Faculty 👨🏫
                </Button>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  fullWidth
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => navigate('/batches')}
                  sx={{
                    py: 2,
                    background: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
                    borderRadius: 3,
                    fontSize: '1rem',
                    fontWeight: 600,
                    color: '#2c3e50'
                  }}
                >
                  Add Batch 👥
                </Button>
              </Grid>
            </>
          ) : (
            <>
              <Grid item xs={12} sm={6} md={4}>
                <Button
                  fullWidth
                  variant="contained"
                  startIcon={<PlayArrowIcon />}
                  onClick={() => navigate('/timetables')}
                  sx={{
                    py: 2,
                    background: 'linear-gradient(135deg, #4CAF50 0%, #45a049 100%)',
                    borderRadius: 3,
                    fontSize: '1rem',
                    fontWeight: 600
                  }}
                >
                  View My Schedule 📅
                </Button>
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <Button
                  fullWidth
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => navigate('/batch-timetable')}
                  sx={{
                    py: 2,
                    background: 'linear-gradient(135deg, #FF9800 0%, #F57C00 100%)',
                    borderRadius: 3,
                    fontSize: '1rem',
                    fontWeight: 600
                  }}
                >
                  Batch Timetable 👥
                </Button>
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <Button
                  fullWidth
                  variant="contained"
                  startIcon={<PersonIcon />}
                  onClick={() => navigate('/profile')}
                  sx={{
                    py: 2,
                    background: 'linear-gradient(135deg, #9C27B0 0%, #7B1FA2 100%)',
                    borderRadius: 3,
                    fontSize: '1rem',
                    fontWeight: 600
                  }}
                >
                  My Profile 👤
                </Button>
              </Grid>
            </>
          )}
        </Grid>
      </Paper>
      </Box>
      </Box>
    </Layout>
  );
}

export default Dashboard;