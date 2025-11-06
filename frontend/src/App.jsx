import React from 'react';
import { Box, Container } from '@mui/material';
import Dashboard from './components/Dashboard';

function App() {
  return (
    <Container maxWidth="xl">
      <Box sx={{ my: 4 }}>
        <Dashboard />
      </Box>
    </Container>
  );
}

export default App;