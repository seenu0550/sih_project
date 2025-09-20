import React, { useState, useEffect } from 'react';
import {
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import Layout from './Layout';
import { subjectsAPI } from '../services/api';

function Subjects() {
  const [subjects, setSubjects] = useState([]);
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    code: '',
    credits: '',
    type: 'theory',
    classes_per_week: '',
    duration: '60'
  });

  useEffect(() => {
    fetchSubjects();
  }, []);

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
      await subjectsAPI.create({
        ...formData,
        credits: parseInt(formData.credits),
        classes_per_week: parseInt(formData.classes_per_week),
        duration: parseInt(formData.duration)
      });
      setOpen(false);
      setFormData({
        name: '',
        code: '',
        credits: '',
        type: 'theory',
        classes_per_week: '',
        duration: '60'
      });
      fetchSubjects();
    } catch (error) {
      console.error('Error creating subject:', error);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this subject?')) {
      try {
        await subjectsAPI.delete(id);
        fetchSubjects();
      } catch (error) {
        console.error('Error deleting subject:', error);
      }
    }
  };

  return (
    <Layout>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Subjects</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpen(true)}
        >
          Add Subject
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Subject Code</TableCell>
              <TableCell>Subject Name</TableCell>
              <TableCell>Credits</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Classes/Week</TableCell>
              <TableCell>Duration (min)</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {subjects.map((subject) => (
              <TableRow key={subject._id}>
                <TableCell>{subject.code}</TableCell>
                <TableCell>{subject.name}</TableCell>
                <TableCell>{subject.credits}</TableCell>
                <TableCell>{subject.type}</TableCell>
                <TableCell>{subject.classes_per_week}</TableCell>
                <TableCell>{subject.duration}</TableCell>
                <TableCell>
                  <Button 
                    color="error" 
                    size="small"
                    onClick={() => handleDelete(subject._id)}
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
          <DialogTitle>Add New Subject</DialogTitle>
          <DialogContent>
            <TextField
              fullWidth
              label="Subject Code"
              margin="normal"
              value={formData.code}
              onChange={(e) => setFormData({ ...formData, code: e.target.value })}
              required
            />
            <TextField
              fullWidth
              label="Subject Name"
              margin="normal"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
            <TextField
              fullWidth
              label="Credits"
              type="number"
              margin="normal"
              value={formData.credits}
              onChange={(e) => setFormData({ ...formData, credits: e.target.value })}
              required
            />
            <FormControl fullWidth margin="normal">
              <InputLabel>Type</InputLabel>
              <Select
                value={formData.type}
                onChange={(e) => setFormData({ ...formData, type: e.target.value })}
              >
                <MenuItem value="theory">Theory</MenuItem>
                <MenuItem value="practical">Practical</MenuItem>
                <MenuItem value="elective">Elective</MenuItem>
              </Select>
            </FormControl>
            <TextField
              fullWidth
              label="Classes per Week"
              type="number"
              margin="normal"
              value={formData.classes_per_week}
              onChange={(e) => setFormData({ ...formData, classes_per_week: e.target.value })}
              required
            />
            <TextField
              fullWidth
              label="Duration (minutes)"
              type="number"
              margin="normal"
              value={formData.duration}
              onChange={(e) => setFormData({ ...formData, duration: e.target.value })}
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

export default Subjects;