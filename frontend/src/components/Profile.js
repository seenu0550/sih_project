import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Avatar,
  Grid,
  Card,
  CardContent,
  Chip,
  Divider,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField
} from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import EmailIcon from '@mui/icons-material/Email';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import EditIcon from '@mui/icons-material/Edit';
import Layout from './Layout';
import { profileAPI } from '../services/api';

function Profile() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editDialog, setEditDialog] = useState(false);
  const [editData, setEditData] = useState({
    email: ''
  });

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await profileAPI.get();
      setUser(response.data);
      setEditData({ email: response.data.email });
    } catch (error) {
      console.error('Error fetching profile:', error);
      // Fallback to user data from AuthContext
      const userData = JSON.parse(localStorage.getItem('user') || '{}');
      if (userData.username) {
        setUser({
          username: userData.username,
          email: userData.email || 'user@example.com',
          role: userData.role || 'student',
          is_active: true,
          _id: 'temp-id'
        });
        setEditData({ email: userData.email || 'user@example.com' });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleEditSave = async () => {
    try {
      await profileAPI.update(editData);
      setUser({ ...user, email: editData.email });
      setEditDialog(false);
      alert('Profile updated successfully!');
    } catch (error) {
      console.error('Error updating profile:', error);
      // Fallback - just update locally
      setUser({ ...user, email: editData.email });
      setEditDialog(false);
      alert('Profile updated locally (backend update failed).');
    }
  };

  const getInitials = (name) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase();
  };

  const getPermissions = (role) => {
    if (role === 'admin') {
      return ['Manage Classrooms', 'Manage Subjects', 'Manage Faculty', 'Manage Batches', 'Generate Timetables'];
    } else {
      return ['View Timetables', 'View Batch Schedule', 'Access Profile'];
    }
  };

  if (loading) {
    return (
      <Layout>
        <Typography>Loading profile...</Typography>
      </Layout>
    );
  }

  if (!user) {
    return (
      <Layout>
        <Typography>Error loading profile.</Typography>
      </Layout>
    );
  }

  return (
    <Layout>
      <Typography variant="h4" gutterBottom>
        👤 Profile
      </Typography>

      <Grid container spacing={3}>
        {/* Profile Card */}
        <Grid item xs={12} md={4}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            textAlign: 'center'
          }}>
            <CardContent sx={{ p: 4 }}>
              <Avatar
                sx={{ 
                  width: 100, 
                  height: 100, 
                  mx: 'auto', 
                  mb: 2,
                  bgcolor: 'rgba(255,255,255,0.2)',
                  fontSize: '2rem'
                }}
              >
                {getInitials(user.username)}
              </Avatar>
              <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold' }}>
                {user.username}
              </Typography>
              <Chip 
                label={user.role === 'admin' ? 'Administrator' : 'Student'}
                sx={{ 
                  bgcolor: 'rgba(255,255,255,0.2)', 
                  color: 'white',
                  fontWeight: 'bold'
                }}
              />
              <Box sx={{ mt: 3 }}>
                <Button
                  variant="outlined"
                  startIcon={<EditIcon />}
                  onClick={() => setEditDialog(true)}
                  sx={{ 
                    color: 'white', 
                    borderColor: 'white',
                    '&:hover': { 
                      borderColor: 'white', 
                      bgcolor: 'rgba(255,255,255,0.1)' 
                    }
                  }}
                >
                  Edit Profile
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Details Card */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent sx={{ p: 4 }}>
              <Typography variant="h5" gutterBottom sx={{ color: '#2c3e50', fontWeight: 'bold' }}>
                📋 Account Details
              </Typography>
              
              <Box sx={{ mt: 3 }}>
                <Grid container spacing={3}>
                  <Grid item xs={12} sm={6}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <PersonIcon sx={{ mr: 2, color: '#3498db' }} />
                      <Box>
                        <Typography variant="body2" color="textSecondary">
                          Username
                        </Typography>
                        <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                          {user.username}
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <EmailIcon sx={{ mr: 2, color: '#e74c3c' }} />
                      <Box>
                        <Typography variant="body2" color="textSecondary">
                          Email
                        </Typography>
                        <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                          {user.email}
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <AdminPanelSettingsIcon sx={{ mr: 2, color: '#f39c12' }} />
                      <Box>
                        <Typography variant="body2" color="textSecondary">
                          Role
                        </Typography>
                        <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                          {user.role === 'admin' ? 'Administrator' : 'Student'}
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Box sx={{ mr: 2, color: '#27ae60', fontSize: '24px' }}>📅</Box>
                      <Box>
                        <Typography variant="body2" color="textSecondary">
                          Account Status
                        </Typography>
                        <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                          {user.is_active ? '🟢 Active' : '🔴 Inactive'}
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                  
                  {user.role === 'student' && user.batch_name && (
                    <>
                      <Grid item xs={12} sm={6}>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                          <Box sx={{ mr: 2, color: '#9b59b6', fontSize: '24px' }}>👥</Box>
                          <Box>
                            <Typography variant="body2" color="textSecondary">
                              Batch
                            </Typography>
                            <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                              {user.batch_name}
                            </Typography>
                          </Box>
                        </Box>
                      </Grid>
                      
                      <Grid item xs={12} sm={6}>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                          <Box sx={{ mr: 2, color: '#e67e22', fontSize: '24px' }}>🏫</Box>
                          <Box>
                            <Typography variant="body2" color="textSecondary">
                              Department
                            </Typography>
                            <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                              {user.batch_department}
                            </Typography>
                          </Box>
                        </Box>
                      </Grid>
                      
                      <Grid item xs={12} sm={6}>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                          <Box sx={{ mr: 2, color: '#3498db', fontSize: '24px' }}>📚</Box>
                          <Box>
                            <Typography variant="body2" color="textSecondary">
                              Semester
                            </Typography>
                            <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                              Semester {user.batch_semester}
                            </Typography>
                          </Box>
                        </Box>
                      </Grid>
                    </>
                  )}
                </Grid>
              </Box>

              <Divider sx={{ my: 3 }} />

              <Typography variant="h6" gutterBottom sx={{ color: '#2c3e50', fontWeight: 'bold' }}>
                🔐 Permissions
              </Typography>
              <Box sx={{ mt: 2 }}>
                {getPermissions(user.role).map((permission, index) => (
                  <Chip
                    key={index}
                    label={permission}
                    sx={{ 
                      mr: 1, 
                      mb: 1,
                      bgcolor: '#e8f5e8',
                      color: '#2e7d32'
                    }}
                  />
                ))}
              </Box>

              <Divider sx={{ my: 3 }} />

              <Typography variant="h6" gutterBottom sx={{ color: '#2c3e50', fontWeight: 'bold' }}>
                📊 Activity
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="textSecondary">
                  User ID: {user._id}
                </Typography>
                <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                  Session Status: 🟢 Active
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Edit Dialog */}
      <Dialog open={editDialog} onClose={() => setEditDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>✏️ Edit Profile</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Email"
            type="email"
            margin="normal"
            value={editData.email}
            onChange={(e) => setEditData({ ...editData, email: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialog(false)}>Cancel</Button>
          <Button onClick={handleEditSave} variant="contained">Save</Button>
        </DialogActions>
      </Dialog>
    </Layout>
  );
}

export default Profile;