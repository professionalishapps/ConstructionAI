import React from 'react';
import { Paper, Typography } from '@mui/material';

export default function BudgetTracker({ data }) {
  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6">Budget Tracker</Typography>
      <Typography>{data ? JSON.stringify(data) : 'No budget data'}</Typography>
    </Paper>
  );
}
