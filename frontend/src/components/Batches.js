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
import { batchesAPI, subjectsAPI } from '../services/api';

function Batches() {
  const [batches, setBatches] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    semester: '',
    department: '',
    student_count: '',
    subjects: []
  });

  useEffect(() => {
    fetchBatches();
    fetchSubjects();
  }, []);

  const fetchBatches = async () => {
    try {
      const response = await batchesAPI.getAll();
      setBatches(response.data);
    } catch (error) {
      console.error('Error fetching batches:', error);
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
      await batchesAPI.create({
        ...formData,
        semester: parseInt(formData.semester),
        student_count: parseInt(formData.student_count)
      });
      setOpen(false);
      setFormData({
        name: '',
        semester: '',
        department: '',
        student_count: '',
        subjects: []
      });
      fetchBatches();
    } catch (error) {
      console.error('Error creating batch:', error);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this batch?')) {
      try {
        await batchesAPI.delete(id);
        fetchBatches();
      } catch (error) {
        console.error('Error deleting batch:', error);
      }
    }
  };

  return (
    <Layout>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Student Batches</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpen(true)}
        >
          Add Batch
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Batch Name</TableCell>
              <TableCell>Semester</TableCell>
              <TableCell>Department</TableCell>
              <TableCell>Student Count</TableCell>
              <TableCell>Subjects</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {batches.map((batch) => (
              <TableRow key={batch._id}>
                <TableCell>{batch.name}</TableCell>
                <TableCell>{batch.semester}</TableCell>
                <TableCell>{batch.department}</TableCell>
                <TableCell>{batch.student_count}</TableCell>
                <TableCell>
                  {batch.subjects.map((subject) => (
                    <Chip key={subject} label={subject} size="small" sx={{ mr: 0.5 }} />
                  ))}
                </TableCell>
                <TableCell>
                  <Button 
                    color="error" 
                    size="small"
                    onClick={() => handleDelete(batch._id)}
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
          <DialogTitle>Add New Batch</DialogTitle>
          <DialogContent>
            <TextField
              fullWidth
              label="Batch Name"
              margin="normal"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
            <TextField
              fullWidth
              label="Semester"
              type="number"
              margin="normal"
              value={formData.semester}
              onChange={(e) => setFormData({ ...formData, semester: e.target.value })}
              required
            />
            <TextField
              fullWidth
              label="Department"
              margin="normal"
              value={formData.department}
              onChange={(e) => setFormData({ ...formData, department: e.target.value })}
              required
            />
            <TextField
              fullWidth
              label="Student Count"
              type="number"
              margin="normal"
              value={formData.student_count}
              onChange={(e) => setFormData({ ...formData, student_count: e.target.value })}
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

export default Batches;