import React from 'react';
import { Box, Container } from '@mui/material';
import DashboardInput from './components/DashboardInput';

function App() {
  return (
    <Container maxWidth="xl">
      <Box sx={{ my: 4 }}>
        <DashboardInput />
      </Box>
    </Container>
  );
}

export default App;