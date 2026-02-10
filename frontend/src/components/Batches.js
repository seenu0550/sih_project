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
import { batchesAPI, subjectsAPI } from '../services/api';

function Batches() {
  const [batches, setBatches] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [open, setOpen] = useState(false);
  const [csvOpen, setCsvOpen] = useState(false);
  const [csvFile, setCsvFile] = useState(null);
  const [csvResult, setCsvResult] = useState(null);
  const [editingBatch, setEditingBatch] = useState(null);
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
      const batchData = {
        ...formData,
        semester: parseInt(formData.semester),
        student_count: parseInt(formData.student_count)
      };
      
      if (editingBatch) {
        await batchesAPI.update(editingBatch._id, batchData);
      } else {
        await batchesAPI.create(batchData);
      }
      
      setOpen(false);
      setEditingBatch(null);
      setFormData({
        name: '',
        semester: '',
        department: '',
        student_count: '',
        subjects: []
      });
      fetchBatches();
    } catch (error) {
      console.error('Error saving batch:', error);
    }
  };

  const handleEdit = (batch) => {
    setEditingBatch(batch);
    setFormData({
      name: batch.name,
      semester: batch.semester.toString(),
      department: batch.department,
      student_count: batch.student_count.toString(),
      subjects: batch.subjects || []
    });
    setOpen(true);
  };

  const handleAdd = () => {
    setEditingBatch(null);
    setFormData({
      name: '',
      semester: '',
      department: '',
      student_count: '',
      subjects: []
    });
    setOpen(true);
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

  const handleCsvUpload = async () => {
    if (!csvFile) return;
    const formData = new FormData();
    formData.append('file', csvFile);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/batches/upload-csv', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });
      const result = await response.json();
      setCsvResult(result);
      if (response.ok) {
        await fetchBatches(); // Refresh data immediately
        setCsvFile(null);
      }
    } catch (error) {
      setCsvResult({ message: 'Upload failed', errors: [error.message] });
    }
  };

  const downloadTemplate = () => {
    const csvContent = "name,semester,department,student_count,subjects\nExample Batch,1,Computer Science,30,SUBJ001;SUBJ002";
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'batches_template.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <Layout>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Student Batches</Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button variant="outlined" startIcon={<UploadIcon />} onClick={() => setCsvOpen(true)}>Upload CSV</Button>
          <Button variant="contained" startIcon={<AddIcon />} onClick={handleAdd}>Add Batch</Button>
        </Box>
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
                  <IconButton 
                    color="primary" 
                    size="small"
                    onClick={() => handleEdit(batch)}
                    sx={{ mr: 1 }}
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton 
                    color="error" 
                    size="small"
                    onClick={() => handleDelete(batch._id)}
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
          <DialogTitle>{editingBatch ? 'Edit Batch' : 'Add New Batch'}</DialogTitle>
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
            <Button onClick={() => { setOpen(false); setEditingBatch(null); }}>Cancel</Button>
            <Button type="submit" variant="contained">{editingBatch ? 'Update' : 'Add'}</Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* CSV Upload Dialog */}
      <Dialog open={csvOpen} onClose={() => setCsvOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Upload Batches CSV</DialogTitle>
        <DialogContent>
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              CSV Format: name,semester,department,student_count,subjects
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

export default Batches;