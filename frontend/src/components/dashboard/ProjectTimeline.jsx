import React from 'react';
import { Paper, Typography } from '@mui/material';

export default function ProjectTimeline({ data }) {
  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6">Project Timeline</Typography>
      <Typography>{data ? JSON.stringify(data) : 'No timeline data'}</Typography>
    </Paper>
  );
}
