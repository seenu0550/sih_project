import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid
} from '@mui/material';
import Layout from './Layout';
import { batchesAPI, timetablesAPI } from '../services/api';

function BatchTimetable() {
  const [batches, setBatches] = useState([]);
  const [selectedBatch, setSelectedBatch] = useState('');
  const [timetable, setTimetable] = useState(null);

  useEffect(() => {
    fetchBatches();
  }, []);

  const fetchBatches = async () => {
    try {
      const response = await batchesAPI.getAll();
      console.log('Batches loaded:', response.data);
      setBatches(response.data);
    } catch (error) {
      console.error('Error fetching batches:', error);
    }
  };

  const handleBatchChange = async (batchName) => {
    setSelectedBatch(batchName);
    
    try {
      const response = await timetablesAPI.getAll();
      const batchTimetable = response.data.find(t => 
        t.slots.some(slot => slot.batch_name === batchName)
      );
      setTimetable(batchTimetable);
    } catch (error) {
      console.error('Error fetching timetable:', error);
    }
  };

  const renderBatchTimetable = () => {
    if (!timetable) return null;

    const workingDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const timeSlots = ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00'];
    
    const groupedSlots = {};
    timetable.slots.forEach(slot => {
      if (slot.batch_name === selectedBatch) {
        if (!groupedSlots[slot.day]) {
          groupedSlots[slot.day] = {};
        }
        groupedSlots[slot.day][slot.time] = slot;
      }
    });

    return (
      <TableContainer component={Paper} sx={{ mt: 2 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Day</TableCell>
              {timeSlots.map(time => (
                <TableCell key={time} align="center" sx={{ width: time === '13:00' ? '55px' : 'auto', minWidth: time === '13:00' ? '55px' : '100px' }}>
                  {time === '13:00' ? 'LUNCH' : time}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {workingDays.map(day => (
              <TableRow key={day}>
                <TableCell component="th" scope="row">
                  <strong>{day}</strong>
                </TableCell>
                {timeSlots.map(time => (
                  <TableCell key={`${day}-${time}`} align="center">
                    {time === '13:00' ? (
                      <Box sx={{ p: 0.3, bgcolor: 'warning.light', borderRadius: 1, color: 'white', width: '50px', textAlign: 'center' }}>
                        <Typography variant="caption" sx={{ fontSize: '0.55rem' }}>LUNCH</Typography>
                      </Box>
                    ) : groupedSlots[day] && groupedSlots[day][time] ? (
                      <Box sx={{ p: 0.5, bgcolor: 'primary.light', borderRadius: 1, color: 'white', minWidth: '80px' }}>
                        <Typography variant="caption" display="block" sx={{ fontWeight: 'bold', fontSize: '0.7rem', mb: 0.2 }}>
                          {groupedSlots[day][time].subject_code}
                        </Typography>
                        <Typography variant="caption" display="block" sx={{ fontSize: '0.65rem', mb: 0.1 }}>
                          {groupedSlots[day][time].faculty_name}
                        </Typography>
                        <Typography variant="caption" display="block" sx={{ fontSize: '0.65rem' }}>
                          {groupedSlots[day][time].classroom_name}
                        </Typography>
                      </Box>
                    ) : (
                      <Box sx={{ p: 1, color: 'text.secondary' }}>-</Box>
                    )}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  return (
    <Layout>
      <Typography variant="h4" gutterBottom>
        Batch-wise Timetable
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <FormControl fullWidth>
            <InputLabel>Select Batch</InputLabel>
            <Select
              value={selectedBatch}
              onChange={(e) => handleBatchChange(e.target.value)}
              displayEmpty
            >
              <MenuItem value="">
                <em>Choose a batch</em>
              </MenuItem>
              {batches.map((batch) => (
                <MenuItem key={batch._id || batch.name} value={batch.name}>
                  {batch.name} - {batch.department} (Sem {batch.semester})
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
      </Grid>

      {selectedBatch && (
        <Box sx={{ mt: 3 }}>
          <Typography variant="h5" gutterBottom>
            Timetable for {selectedBatch}
          </Typography>
          {timetable ? renderBatchTimetable() : (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="h6" color="textSecondary">
                No timetable found for this batch
              </Typography>
            </Paper>
          )}
        </Box>
      )}
    </Layout>
  );
}

export default BatchTimetable;