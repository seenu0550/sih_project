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
  Chip,
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
import { classroomsAPI } from '../services/api';

function Classrooms() {
  const [classrooms, setClassrooms] = useState([]);
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    capacity: '',
    type: 'lecture',
    equipment: []
  });
  const [equipmentInput, setEquipmentInput] = useState('');

  useEffect(() => {
    fetchClassrooms();
  }, []);

  const fetchClassrooms = async () => {
    try {
      const response = await classroomsAPI.getAll();
      setClassrooms(response.data);
    } catch (error) {
      console.error('Error fetching classrooms:', error);
      if (error.response?.status === 401) {
        alert('Please login first');
        window.location.href = '/login';
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await classroomsAPI.create({
        ...formData,
        capacity: parseInt(formData.capacity)
      });
      setOpen(false);
      setFormData({ name: '', capacity: '', type: 'lecture', equipment: [] });
      fetchClassrooms();
      alert('Classroom added successfully!');
    } catch (error) {
      console.error('Error creating classroom:', error);
      if (error.response?.status === 401) {
        alert('Please login first');
        window.location.href = '/login';
      } else {
        alert('Error adding classroom: ' + (error.response?.data?.detail || error.message));
      }
    }
  };

  const addEquipment = () => {
    if (equipmentInput.trim() && !formData.equipment.includes(equipmentInput.trim())) {
      setFormData({
        ...formData,
        equipment: [...formData.equipment, equipmentInput.trim()]
      });
      setEquipmentInput('');
    }
  };

  const removeEquipment = (equipment) => {
    setFormData({
      ...formData,
      equipment: formData.equipment.filter(e => e !== equipment)
    });
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this classroom?')) {
      try {
        await classroomsAPI.delete(id);
        fetchClassrooms();
      } catch (error) {
        console.error('Error deleting classroom:', error);
      }
    }
  };

  return (
    <Layout>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Classrooms</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpen(true)}
        >
          Add Classroom
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Capacity</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Equipment</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {classrooms.map((classroom) => (
              <TableRow key={classroom._id}>
                <TableCell>{classroom.name}</TableCell>
                <TableCell>{classroom.capacity}</TableCell>
                <TableCell>{classroom.type}</TableCell>
                <TableCell>
                  {classroom.equipment.map((eq) => (
                    <Chip key={eq} label={eq} size="small" sx={{ mr: 0.5 }} />
                  ))}
                </TableCell>
                <TableCell>
                  <Button 
                    color="error" 
                    size="small"
                    onClick={() => handleDelete(classroom._id)}
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
          <DialogTitle>Add New Classroom</DialogTitle>
          <DialogContent>
            <TextField
              fullWidth
              label="Classroom Name"
              margin="normal"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
            <TextField
              fullWidth
              label="Capacity"
              type="number"
              margin="normal"
              value={formData.capacity}
              onChange={(e) => setFormData({ ...formData, capacity: e.target.value })}
              required
            />
            <FormControl fullWidth margin="normal">
              <InputLabel>Type</InputLabel>
              <Select
                value={formData.type}
                onChange={(e) => setFormData({ ...formData, type: e.target.value })}
              >
                <MenuItem value="lecture">Lecture Hall</MenuItem>
                <MenuItem value="lab">Laboratory</MenuItem>
                <MenuItem value="seminar">Seminar Room</MenuItem>
              </Select>
            </FormControl>
            
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle1">Equipment</Typography>
              <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                <TextField
                  size="small"
                  placeholder="Add equipment"
                  value={equipmentInput}
                  onChange={(e) => setEquipmentInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addEquipment())}
                />
                <Button onClick={addEquipment}>Add</Button>
              </Box>
              <Box sx={{ mt: 1 }}>
                {formData.equipment.map((eq) => (
                  <Chip
                    key={eq}
                    label={eq}
                    onDelete={() => removeEquipment(eq)}
                    sx={{ mr: 0.5, mb: 0.5 }}
                  />
                ))}
              </Box>
            </Box>
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

export default Classrooms;