import React from 'react';
import { Paper, Typography } from '@mui/material';

export default function RiskScoreCard({ data }) {
  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6">Risk Score</Typography>
      <Typography>{data ? JSON.stringify(data) : 'No data'}</Typography>
    </Paper>
  );
}
