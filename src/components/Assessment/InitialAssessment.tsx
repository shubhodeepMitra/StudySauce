import React, { useState } from 'react';
import { Box, Button, FormControl, InputLabel, MenuItem, Select, TextField, Typography, Paper } from '@mui/material';

interface InitialAssessmentProps {
  onSubmit: (data: { subject: string; grade: number; studentId: string }) => void;
}

const InitialAssessment: React.FC<InitialAssessmentProps> = ({ onSubmit }) => {
  const [subject, setSubject] = useState('');
  const [grade, setGrade] = useState('');
  const [studentId, setStudentId] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      subject,
      grade: parseInt(grade),
      studentId
    });
  };

  return (
    <Paper elevation={3} sx={{ p: 4, maxWidth: 600, mx: 'auto', mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        Initial Assessment
      </Typography>
      <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel>Subject</InputLabel>
          <Select
            value={subject}
            label="Subject"
            onChange={(e) => setSubject(e.target.value)}
            required
          >
            <MenuItem value="physics">Physics</MenuItem>
            <MenuItem value="mathematics">Mathematics</MenuItem>
            <MenuItem value="chemistry">Chemistry</MenuItem>
            <MenuItem value="biology">Biology</MenuItem>
          </Select>
        </FormControl>

        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel>Grade Level</InputLabel>
          <Select
            value={grade}
            label="Grade Level"
            onChange={(e) => setGrade(e.target.value)}
            required
          >
            <MenuItem value="7">Grade 7</MenuItem>
            <MenuItem value="8">Grade 8</MenuItem>
            <MenuItem value="9">Grade 9</MenuItem>
            <MenuItem value="10">Grade 10</MenuItem>
          </Select>
        </FormControl>

        <TextField
          fullWidth
          label="Student ID"
          value={studentId}
          onChange={(e) => setStudentId(e.target.value)}
          required
          sx={{ mb: 3 }}
        />

        <Button
          type="submit"
          variant="contained"
          color="primary"
          fullWidth
          size="large"
        >
          Start Assessment
        </Button>
      </Box>
    </Paper>
  );
};

export default InitialAssessment; 