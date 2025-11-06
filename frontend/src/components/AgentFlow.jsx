import React from 'react';
import { Paper, Typography } from '@mui/material';

export default function AgentFlow({ agents }) {
  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6">Agent Flow</Typography>
      <Typography>{agents ? JSON.stringify(agents) : 'No agent data'}</Typography>
    </Paper>
  );
}
