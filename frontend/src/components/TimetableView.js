import React, { useState, useEffect } from 'react';
import {
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Box,
  Card,
  CardContent,
  CardActions,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import Layout from './Layout';
import { timetablesAPI } from '../services/api';

function TimetableView() {
  const [timetables, setTimetables] = useState([]);
  const [selectedTimetable, setSelectedTimetable] = useState(null);
  const [viewDialog, setViewDialog] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTimetables();
  }, []);

  const fetchTimetables = async () => {
    try {
      const response = await timetablesAPI.getAll();
      setTimetables(response.data);
    } catch (error) {
      console.error('Error fetching timetables:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id) => {
    try {
      await timetablesAPI.approve(id);
      fetchTimetables();
      alert('Timetable approved successfully!');
    } catch (error) {
      console.error('Error approving timetable:', error);
      alert('Error approving timetable.');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this timetable?')) {
      try {
        await timetablesAPI.delete(id);
        fetchTimetables();
        alert('Timetable deleted successfully!');
      } catch (error) {
        console.error('Error deleting timetable:', error);
        alert('Error deleting timetable.');
      }
    }
  };

  const renderTimetableGrid = (slots) => {
    const groupedSlots = {};
    slots.forEach(slot => {
      if (!groupedSlots[slot.day]) {
        groupedSlots[slot.day] = {};
      }
      groupedSlots[slot.day][slot.time] = slot;
    });

    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const timeSlots = ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00'];

    return (
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Day</TableCell>
              {timeSlots.map(time => (
                <TableCell key={time} sx={{ width: time === '13:00' ? '55px' : 'auto', minWidth: time === '13:00' ? '55px' : '100px' }}>
                  {time === '13:00' ? 'LUNCH' : time}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {days.map(day => (
              <TableRow key={day}>
                <TableCell>{day}</TableCell>
                {timeSlots.map(time => (
                  <TableCell key={`${day}-${time}`}>
                    {time === '13:00' ? (
                      <Box sx={{ bgcolor: 'warning.light', p: 0.3, borderRadius: 1, width: '50px', textAlign: 'center' }}>
                        <Typography variant="caption" sx={{ fontSize: '0.55rem' }}>LUNCH</Typography>
                      </Box>
                    ) : groupedSlots[day] && groupedSlots[day][time] ? (
                      <Box sx={{ p: 0.5, minWidth: '80px' }}>
                        <Typography variant="caption" display="block" sx={{ fontWeight: 'bold', fontSize: '0.7rem', mb: 0.2 }}>
                          {groupedSlots[day][time].subject_code}
                        </Typography>
                        <Typography variant="caption" display="block" sx={{ fontSize: '0.65rem', mb: 0.1 }}>
                          {groupedSlots[day][time].faculty_name}
                        </Typography>
                        <Typography variant="caption" display="block" sx={{ fontSize: '0.65rem', mb: 0.1 }}>
                          {groupedSlots[day][time].classroom_name}
                        </Typography>
                        <Typography variant="caption" display="block" sx={{ fontSize: '0.6rem', color: 'text.secondary' }}>
                          {groupedSlots[day][time].batch_name}
                        </Typography>
                      </Box>
                    ) : '-'}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  if (loading) {
    return (
      <Layout>
        <Typography>Loading timetables...</Typography>
      </Layout>
    );
  }

  return (
    <Layout>
      <Typography variant="h4" gutterBottom>
        Saved Timetables
      </Typography>

      {timetables.length === 0 ? (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary">
            No timetables found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Generate and save timetables to view them here.
          </Typography>
        </Paper>
      ) : (
        <Box>
          {timetables.map((timetable) => (
            <Card key={timetable._id} sx={{ mb: 2 }}>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Typography variant="h6">
                    {timetable.name}
                  </Typography>
                  <Chip 
                    label={timetable.status} 
                    color={timetable.status === 'approved' ? 'success' : 'default'}
                    variant={timetable.status === 'approved' ? 'filled' : 'outlined'}
                  />
                </Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Department: {timetable.department} | Semester: {timetable.semester}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Created: {new Date(timetable.created_at).toLocaleDateString()}
                </Typography>
                <Typography variant="body2">
                  Total Classes: {timetable.slots.length}
                </Typography>
              </CardContent>
              <CardActions>
                <Button
                  size="small"
                  onClick={() => {
                    setSelectedTimetable(timetable);
                    setViewDialog(true);
                  }}
                >
                  View Details
                </Button>
                {timetable.status !== 'approved' && (
                  <Button
                    size="small"
                    startIcon={<CheckCircleIcon />}
                    onClick={() => handleApprove(timetable._id)}
                    color="success"
                  >
                    Approve
                  </Button>
                )}
                <Button
                  size="small"
                  startIcon={<DeleteIcon />}
                  onClick={() => handleDelete(timetable._id)}
                  color="error"
                >
                  Delete
                </Button>
              </CardActions>
            </Card>
          ))}
        </Box>
      )}

      <Dialog open={viewDialog} onClose={() => setViewDialog(false)} maxWidth="lg" fullWidth>
        <DialogTitle>
          {selectedTimetable?.name}
          <Typography variant="subtitle2" color="text.secondary">
            {selectedTimetable?.department} - Semester {selectedTimetable?.semester}
          </Typography>
        </DialogTitle>
        <DialogContent>
          {selectedTimetable && renderTimetableGrid(selectedTimetable.slots)}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Layout>
  );
}

export default TimetableView;