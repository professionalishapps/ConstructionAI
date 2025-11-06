import React from 'react';
import { Paper, Typography } from '@mui/material';

export default function WeatherImpact({ data }) {
  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6">Weather Impact</Typography>
      <Typography>{data ? JSON.stringify(data) : 'No weather data'}</Typography>
    </Paper>
  );
}
