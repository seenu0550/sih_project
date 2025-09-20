import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Divider
} from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import SchoolIcon from '@mui/icons-material/School';
import PersonIcon from '@mui/icons-material/Person';
import RoomIcon from '@mui/icons-material/Room';
import ScheduleIcon from '@mui/icons-material/Schedule';
import ViewListIcon from '@mui/icons-material/ViewList';
import LogoutIcon from '@mui/icons-material/Logout';
import GroupsIcon from '@mui/icons-material/Groups';
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth';
import { useAuth } from '../context/AuthContext';

const drawerWidth = 260;

const getMenuItems = (userRole) => {
  const studentItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/', emoji: '🏠' },
    { text: 'View Timetables', icon: <ViewListIcon />, path: '/timetables', emoji: '📋' },
    { text: 'Batch Timetable', icon: <CalendarMonthIcon />, path: '/batch-timetable', emoji: '📅' },
    { text: 'Profile', icon: <PersonIcon />, path: '/profile', emoji: '👤' },
  ];
  
  const adminItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/', emoji: '🏠' },
    { text: 'Classrooms', icon: <RoomIcon />, path: '/classrooms', emoji: '🏫' },
    { text: 'Subjects', icon: <SchoolIcon />, path: '/subjects', emoji: '📚' },
    { text: 'Faculty', icon: <PersonIcon />, path: '/faculty', emoji: '👨🏫' },
    { text: 'Batches', icon: <GroupsIcon />, path: '/batches', emoji: '👥' },
    { text: 'Generate Timetable', icon: <ScheduleIcon />, path: '/generate-timetable', emoji: '⚡' },
    { text: 'View Timetables', icon: <ViewListIcon />, path: '/timetables', emoji: '📋' },
    { text: 'Batch Timetable', icon: <CalendarMonthIcon />, path: '/batch-timetable', emoji: '📅' },
    { text: 'Profile', icon: <PersonIcon />, path: '/profile', emoji: '👤' },
  ];
  
  return userRole === 'admin' ? adminItems : studentItems;
};

function Layout({ children }) {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout, user } = useAuth();
  const menuItems = getMenuItems(user?.role || 'student');

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: '#f8fafc' }}>
      <AppBar 
        position="fixed" 
        sx={{ 
          zIndex: (theme) => theme.zIndex.drawer + 1,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          boxShadow: '0 4px 20px rgba(0,0,0,0.1)'
        }}
      >
        <Toolbar sx={{ px: 3, minHeight: 200 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
            <Typography variant="h3" noWrap component="div" sx={{ fontWeight: 'bold', mr: 1, fontSize: '2.5rem' }}>
              🎓 Smart Classroom Scheduler
            </Typography>
          </Box>
          <Button 
            color="inherit" 
            onClick={handleLogout} 
            startIcon={<LogoutIcon />}
            sx={{ 
              bgcolor: 'rgba(255,255,255,0.1)',
              '&:hover': { bgcolor: 'rgba(255,255,255,0.2)' },
              borderRadius: 2,
              px: 3,
              py: 1,
              fontSize: '1rem',
              fontWeight: 600
            }}
          >
            LOGOUT
          </Button>
        </Toolbar>
      </AppBar>

      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
            bgcolor: '#ffffff',
            borderRight: '1px solid #e2e8f0',
            boxShadow: '4px 0 10px rgba(0,0,0,0.05)'
          },
        }}
      >
        <Box sx={{ height: 100 }} />
        <Box sx={{ overflow: 'auto', p: 1 }}>
          <List sx={{ px: 1 }}>
            {menuItems.map((item, index) => (
              <React.Fragment key={item.text}>
                <ListItem disablePadding sx={{ mb: 0.5 }}>
                  <ListItemButton
                    selected={location.pathname === item.path}
                    onClick={() => navigate(item.path)}
                    sx={{
                      borderRadius: 2,
                      py: 1.5,
                      px: 2,
                      '&.Mui-selected': {
                        bgcolor: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        color: 'white',
                        '&:hover': {
                          background: 'linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%)'
                        }
                      },
                      '&:hover': {
                        bgcolor: '#f1f5f9'
                      }
                    }}
                  >
                    <ListItemIcon sx={{ 
                      color: location.pathname === item.path ? 'white' : '#64748b',
                      minWidth: 40
                    }}>
                      <Box sx={{ fontSize: '20px', mr: 1 }}>{item.emoji}</Box>
                      {item.icon}
                    </ListItemIcon>
                    <ListItemText 
                      primary={item.text} 
                      sx={{ 
                        '& .MuiListItemText-primary': {
                          fontWeight: location.pathname === item.path ? 600 : 500,
                          fontSize: '0.95rem'
                        }
                      }}
                    />
                  </ListItemButton>
                </ListItem>
                {(index === 0 || index === 4) && <Divider sx={{ my: 1, mx: 2 }} />}
              </React.Fragment>
            ))}
          </List>
        </Box>
      </Drawer>

      <Box component="main" sx={{ flexGrow: 1, bgcolor: '#f8fafc' }}>
        <Box sx={{ height: 100 }} />
        <Box sx={{ p: 0 }}>
          {children}
        </Box>
      </Box>
    </Box>
  );
}

export default Layout;