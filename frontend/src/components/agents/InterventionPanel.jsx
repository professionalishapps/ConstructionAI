import React from 'react';
import { Paper, Typography } from '@mui/material';

export default function InterventionPanel({ data }) {
  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6">Interventions</Typography>
      <Typography>{data ? JSON.stringify(data) : 'No interventions'}</Typography>
    </Paper>
  );
}
