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
  TableRow,
  Alert,
  IconButton
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import UploadIcon from '@mui/icons-material/Upload';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import Layout from './Layout';
import { subjectsAPI } from '../services/api';

function Subjects() {
  const [subjects, setSubjects] = useState([]);
  const [open, setOpen] = useState(false);
  const [csvOpen, setCsvOpen] = useState(false);
  const [csvFile, setCsvFile] = useState(null);
  const [csvResult, setCsvResult] = useState(null);
  const [editingSubject, setEditingSubject] = useState(null);
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
      const subjectData = {
        ...formData,
        credits: parseInt(formData.credits),
        classes_per_week: parseInt(formData.classes_per_week),
        duration: parseInt(formData.duration)
      };
      
      if (editingSubject) {
        await subjectsAPI.update(editingSubject._id, subjectData);
      } else {
        await subjectsAPI.create(subjectData);
      }
      
      setOpen(false);
      setEditingSubject(null);
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
      console.error('Error saving subject:', error);
    }
  };

  const handleEdit = (subject) => {
    setEditingSubject(subject);
    setFormData({
      name: subject.name,
      code: subject.code,
      credits: subject.credits.toString(),
      type: subject.type,
      classes_per_week: subject.classes_per_week.toString(),
      duration: subject.duration.toString()
    });
    setOpen(true);
  };

  const handleAdd = () => {
    setEditingSubject(null);
    setFormData({
      name: '',
      code: '',
      credits: '',
      type: 'theory',
      classes_per_week: '',
      duration: '60'
    });
    setOpen(true);
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

  const handleCsvUpload = async () => {
    if (!csvFile) return;
    const formData = new FormData();
    formData.append('file', csvFile);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/subjects/upload-csv', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });
      const result = await response.json();
      setCsvResult(result);
      if (response.ok) {
        await fetchSubjects(); // Refresh data immediately
        setCsvFile(null);
      }
    } catch (error) {
      setCsvResult({ message: 'Upload failed', errors: [error.message] });
    }
  };

  const downloadTemplate = () => {
    const csvContent = "name,code,credits,type,classes_per_week,duration\nExample Subject,SUBJ001,3,theory,4,60\nExample Lab,LAB001,1,practical,2,120";
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'subjects_template.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <Layout>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Subjects</Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button variant="outlined" startIcon={<UploadIcon />} onClick={() => setCsvOpen(true)}>Upload CSV</Button>
          <Button variant="contained" startIcon={<AddIcon />} onClick={handleAdd}>Add Subject</Button>
        </Box>
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
                  <IconButton 
                    color="primary" 
                    size="small"
                    onClick={() => handleEdit(subject)}
                    sx={{ mr: 1 }}
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton 
                    color="error" 
                    size="small"
                    onClick={() => handleDelete(subject._id)}
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
          <DialogTitle>{editingSubject ? 'Edit Subject' : 'Add New Subject'}</DialogTitle>
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
              <InputLabel id="type-label">Type</InputLabel>
              <Select
                labelId="type-label"
                label="Type"
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
            <Button onClick={() => { setOpen(false); setEditingSubject(null); }}>Cancel</Button>
            <Button type="submit" variant="contained">{editingSubject ? 'Update' : 'Add'}</Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* CSV Upload Dialog */}
      <Dialog open={csvOpen} onClose={() => setCsvOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Upload Subjects CSV</DialogTitle>
        <DialogContent>
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              CSV Format: name,code,credits,type,classes_per_week,duration
            </Typography>
            <Button variant="outlined" size="small" onClick={downloadTemplate}>Download Template</Button>
          </Box>
          <input type="file" accept=".csv" onChange={(e) => setCsvFile(e.target.files[0])} />
          {csvResult && (
            <Alert severity={csvResult.errors?.length > 0 ? "warning" : "success"} sx={{ mt: 2 }}>
              <Typography variant="body2">{csvResult.message}</Typography>
              {csvResult.errors?.length > 0 && (
                <Box sx={{ mt: 1 }}>
                  {csvResult.errors.map((error, index) => (
                    <Typography key={index} variant="caption" display="block">{error}</Typography>
                  ))}
                </Box>
              )}
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

export default Subjects;