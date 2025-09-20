import React, { useState, useEffect } from 'react';
import {
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Chip,
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Autocomplete
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import Layout from './Layout';
import { facultyAPI, subjectsAPI } from '../services/api';

function Faculty() {
  const [faculty, setFaculty] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subjects: [],
    max_hours_per_day: '6',
    avg_leaves_per_month: '2'
  });

  useEffect(() => {
    fetchFaculty();
    fetchSubjects();
  }, []);

  const fetchFaculty = async () => {
    try {
      const response = await facultyAPI.getAll();
      setFaculty(response.data);
    } catch (error) {
      console.error('Error fetching faculty:', error);
    }
  };

  const fetchSubjects = async () => {
    try {
      const response = await subjectsAPI.getAll();
      setSubjects(response.data);
    } catch (error) {
      console.error('Error fetching subjects:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await facultyAPI.create({
        ...formData,
        max_hours_per_day: parseInt(formData.max_hours_per_day),
        avg_leaves_per_month: parseInt(formData.avg_leaves_per_month)
      });
      setOpen(false);
      setFormData({
        name: '',
        email: '',
        subjects: [],
        max_hours_per_day: '6',
        avg_leaves_per_month: '2'
      });
      fetchFaculty();
    } catch (error) {
      console.error('Error creating faculty:', error);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this faculty member?')) {
      try {
        await facultyAPI.delete(id);
        fetchFaculty();
      } catch (error) {
        console.error('Error deleting faculty:', error);
      }
    }
  };

  return (
    <Layout>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Faculty</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpen(true)}
        >
          Add Faculty
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Subjects</TableCell>
              <TableCell>Max Hours/Day</TableCell>
              <TableCell>Avg Leaves/Month</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {faculty.map((member) => (
              <TableRow key={member._id}>
                <TableCell>{member.name}</TableCell>
                <TableCell>{member.email}</TableCell>
                <TableCell>
                  {member.subjects.map((subject) => (
                    <Chip key={subject} label={subject} size="small" sx={{ mr: 0.5 }} />
                  ))}
                </TableCell>
                <TableCell>{member.max_hours_per_day}</TableCell>
                <TableCell>{member.avg_leaves_per_month}</TableCell>
                <TableCell>
                  <Button 
                    color="error" 
                    size="small"
                    onClick={() => handleDelete(member._id)}
                  >
                    Delete
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <form onSubmit={handleSubmit}>
          <DialogTitle>Add New Faculty</DialogTitle>
          <DialogContent>
            <TextField
              fullWidth
              label="Faculty Name"
              margin="normal"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
            <TextField
              fullWidth
              label="Email"
              type="email"
              margin="normal"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              required
            />
            <Autocomplete
              multiple
              options={subjects.map(s => s.code)}
              value={formData.subjects}
              onChange={(e, newValue) => setFormData({ ...formData, subjects: newValue })}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Subjects"
                  margin="normal"
                  placeholder="Select subjects"
                />
              )}
              renderTags={(value, getTagProps) =>
                value.map((option, index) => (
                  <Chip variant="outlined" label={option} {...getTagProps({ index })} />
                ))
              }
            />
            <TextField
              fullWidth
              label="Max Hours per Day"
              type="number"
              margin="normal"
              value={formData.max_hours_per_day}
              onChange={(e) => setFormData({ ...formData, max_hours_per_day: e.target.value })}
              required
            />
            <TextField
              fullWidth
              label="Average Leaves per Month"
              type="number"
              margin="normal"
              value={formData.avg_leaves_per_month}
              onChange={(e) => setFormData({ ...formData, avg_leaves_per_month: e.target.value })}
              required
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpen(false)}>Cancel</Button>
            <Button type="submit" variant="contained">Add</Button>
          </DialogActions>
        </form>
      </Dialog>
    </Layout>
  );
}

export default Faculty;