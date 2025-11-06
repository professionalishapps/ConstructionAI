import React from 'react';
import { Paper, Typography } from '@mui/material';

export default function SubcontractorScore({ data }) {
  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6">Subcontractor Scores</Typography>
      <Typography>{data ? JSON.stringify(data) : 'No subcontractor data'}</Typography>
    </Paper>
  );
}
