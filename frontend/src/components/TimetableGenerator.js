import React, { useState, useEffect } from 'react';
import {
  Typography,
  Button,
  TextField,
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import SaveIcon from '@mui/icons-material/Save';
import Layout from './Layout';
import { timetablesAPI, batchesAPI } from '../services/api';

function TimetableGenerator() {
  const [formData, setFormData] = useState({
    name: '',
    semester: '',
    department: '',
    max_classes_per_day: '8',
    working_days: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
    time_slots: ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00']
  });
  const [batches, setBatches] = useState([]);
  const [options, setOptions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedOption, setSelectedOption] = useState(null);
  const [saveDialog, setSaveDialog] = useState(false);
  const [saveName, setSaveName] = useState('');

  useEffect(() => {
    fetchBatches();
  }, []);

  const fetchBatches = async () => {
    try {
      const response = await batchesAPI.getAll();
      setBatches(response.data);
    } catch (error) {
      console.error('Error fetching batches:', error);
    }
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const requestData = {
        ...formData,
        semester: parseInt(formData.semester),
        max_classes_per_day: parseInt(formData.max_classes_per_day)
      };
      const response = await timetablesAPI.generate(requestData);
      setOptions(response.data.options);
    } catch (error) {
      console.error('Error generating timetable:', error);
      alert('Error generating timetable. Please check your data.');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!selectedOption || !saveName) return;
    
    try {
      const timetableData = {
        name: saveName,
        semester: parseInt(formData.semester),
        department: formData.department,
        slots: selectedOption,
        status: 'draft'
      };
      
      await timetablesAPI.save(timetableData);
      setSaveDialog(false);
      setSaveName('');
      setSelectedOption(null);
      alert('Timetable saved successfully!');
    } catch (error) {
      console.error('Error saving timetable:', error);
      alert('Error saving timetable.');
    }
  };

  const renderTimetableOption = (option, index) => {
    const groupedSlots = {};
    option.forEach(slot => {
      if (!groupedSlots[slot.day]) {
        groupedSlots[slot.day] = {};
      }
      groupedSlots[slot.day][slot.time] = slot;
    });

    return (
      <Card key={index} sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Option {index + 1}
          </Typography>
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Day</TableCell>
                  {formData.time_slots.map(time => (
                    <TableCell key={time} sx={{ width: time === '13:00' ? '55px' : 'auto', minWidth: time === '13:00' ? '55px' : '100px' }}>
                      {time === '13:00' ? 'LUNCH' : time}
                    </TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {formData.working_days.map(day => (
                  <TableRow key={day}>
                    <TableCell>{day}</TableCell>
                    {formData.time_slots.map(time => (
                      <TableCell key={`${day}-${time}`}>
                        {time === '13:00' ? (
                          <Box sx={{ bgcolor: 'warning.light', p: 0.3, borderRadius: 1, width: '50px', textAlign: 'center' }}>
                            <Typography variant="caption" sx={{ fontSize: '0.55rem' }}>LUNCH</Typography>
                          </Box>
                        ) : groupedSlots[day] && groupedSlots[day][time] ? (
                          <Box sx={{ p: 0.5, minWidth: '80px' }}>
                            <Typography variant="caption" display="block" sx={{ fontWeight: 'bold', fontSize: '0.7rem' }}>
                              {groupedSlots[day][time].subject_code}
                            </Typography>
                            <Typography variant="caption" display="block" sx={{ fontSize: '0.65rem' }}>
                              {groupedSlots[day][time].faculty_name}
                            </Typography>
                            <Typography variant="caption" display="block" sx={{ fontSize: '0.65rem' }}>
                              {groupedSlots[day][time].classroom_name}
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
        </CardContent>
        <CardActions>
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={() => {
              setSelectedOption(option);
              setSaveDialog(true);
            }}
          >
            Select & Save
          </Button>
        </CardActions>
      </Card>
    );
  };

  return (
    <Layout>
      <Typography variant="h4" gutterBottom>
        Generate Timetable
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <form onSubmit={handleGenerate}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth required>
                <InputLabel>Batch Name</InputLabel>
                <Select
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  label="Batch Name"
                >
                  <MenuItem value="">
                    <em>Select a batch</em>
                  </MenuItem>
                  {batches.map((batch) => (
                    <MenuItem key={batch._id || batch.name} value={batch.name}>
                      {batch.name} - {batch.department} (Sem {batch.semester})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                label="Semester"
                type="number"
                value={formData.semester}
                onChange={(e) => setFormData({ ...formData, semester: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                label="Department"
                value={formData.department}
                onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Max Classes per Day"
                type="number"
                value={formData.max_classes_per_day}
                onChange={(e) => setFormData({ ...formData, max_classes_per_day: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <Button
                type="submit"
                variant="contained"
                size="large"
                startIcon={<AutoAwesomeIcon />}
                disabled={loading}
              >
                {loading ? 'Generating...' : 'Generate Timetable Options'}
              </Button>
            </Grid>
          </Grid>
        </form>
      </Paper>

      {options.length > 0 && (
        <Box>
          <Typography variant="h5" gutterBottom>
            Generated Options ({options.length})
          </Typography>
          {options.map((option, index) => renderTimetableOption(option, index))}
        </Box>
      )}

      <Dialog open={saveDialog} onClose={() => setSaveDialog(false)}>
        <DialogTitle>Save Timetable</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Timetable Name"
            value={saveName}
            onChange={(e) => setSaveName(e.target.value)}
            margin="normal"
            required
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSaveDialog(false)}>Cancel</Button>
          <Button onClick={handleSave} variant="contained">Save</Button>
        </DialogActions>
      </Dialog>
    </Layout>
  );
}

export default TimetableGenerator;