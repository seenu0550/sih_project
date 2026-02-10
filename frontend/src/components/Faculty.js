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
  Autocomplete,
  Alert,
  IconButton
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import UploadIcon from '@mui/icons-material/Upload';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import Layout from './Layout';
import { facultyAPI, subjectsAPI } from '../services/api';

function Faculty() {
  const [faculty, setFaculty] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [open, setOpen] = useState(false);
  const [csvOpen, setCsvOpen] = useState(false);
  const [csvFile, setCsvFile] = useState(null);
  const [csvResult, setCsvResult] = useState(null);
  const [editingFaculty, setEditingFaculty] = useState(null);
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
      const facultyData = {
        ...formData,
        max_hours_per_day: parseInt(formData.max_hours_per_day),
        avg_leaves_per_month: parseInt(formData.avg_leaves_per_month)
      };
      
      if (editingFaculty) {
        await facultyAPI.update(editingFaculty._id, facultyData);
      } else {
        await facultyAPI.create(facultyData);
      }
      
      setOpen(false);
      setEditingFaculty(null);
      setFormData({
        name: '',
        email: '',
        subjects: [],
        max_hours_per_day: '6',
        avg_leaves_per_month: '2'
      });
      fetchFaculty();
    } catch (error) {
      console.error('Error saving faculty:', error);
    }
  };

  const handleEdit = (member) => {
    setEditingFaculty(member);
    setFormData({
      name: member.name,
      email: member.email,
      subjects: member.subjects || [],
      max_hours_per_day: member.max_hours_per_day.toString(),
      avg_leaves_per_month: member.avg_leaves_per_month.toString()
    });
    setOpen(true);
  };

  const handleAdd = () => {
    setEditingFaculty(null);
    setFormData({
      name: '',
      email: '',
      subjects: [],
      max_hours_per_day: '6',
      avg_leaves_per_month: '2'
    });
    setOpen(true);
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

  const handleCsvUpload = async () => {
    if (!csvFile) return;
    const formData = new FormData();
    formData.append('file', csvFile);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/faculty/upload-csv', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });
      const result = await response.json();
      setCsvResult(result);
      if (response.ok) {
        await fetchFaculty(); // Refresh data immediately
        setCsvFile(null);
      }
    } catch (error) {
      setCsvResult({ message: 'Upload failed', errors: [error.message] });
    }
  };

  const downloadTemplate = () => {
    const csvContent = "name,email,subjects,max_hours_per_day,avg_leaves_per_month\nExample Faculty,faculty@example.edu,SUBJ001;SUBJ002,6,2";
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'faculty_template.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <Layout>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Faculty</Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button variant="outlined" startIcon={<UploadIcon />} onClick={() => setCsvOpen(true)}>Upload CSV</Button>
          <Button variant="contained" startIcon={<AddIcon />} onClick={handleAdd}>Add Faculty</Button>
        </Box>
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
                  <IconButton 
                    color="primary" 
                    size="small"
                    onClick={() => handleEdit(member)}
                    sx={{ mr: 1 }}
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton 
                    color="error" 
                    size="small"
                    onClick={() => handleDelete(member._id)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <form onSubmit={handleSubmit}>
          <DialogTitle>{editingFaculty ? 'Edit Faculty' : 'Add New Faculty'}</DialogTitle>
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
            <Button onClick={() => { setOpen(false); setEditingFaculty(null); }}>Cancel</Button>
            <Button type="submit" variant="contained">{editingFaculty ? 'Update' : 'Add'}</Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* CSV Upload Dialog */}
      <Dialog open={csvOpen} onClose={() => setCsvOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Upload Faculty CSV</DialogTitle>
        <DialogContent>
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              CSV Format: name,email,subjects,max_hours_per_day,avg_leaves_per_month
            </Typography>
            <Button variant="outlined" size="small" onClick={downloadTemplate}>Download Template</Button>
          </Box>
          <input type="file" accept=".csv" onChange={(e) => setCsvFile(e.target.files[0])} />
          {csvResult && (
            <Alert severity={csvResult.errors?.length > 0 ? "warning" : "success"} sx={{ mt: 2 }}>
              <Typography variant="body2">{csvResult.message}</Typography>
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => { setCsvOpen(false); setCsvResult(null); setCsvFile(null); }}>Cancel</Button>
          <Button onClick={handleCsvUpload} variant="contained" disabled={!csvFile}>Upload</Button>
        </DialogActions>
      </Dialog>
    </Layout>
  );
}

export default Faculty;