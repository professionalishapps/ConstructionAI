import React from 'react';
import { Box, Container } from '@mui/material';
import Dashboard from './components/dashboard/Dashboard';
import { ProjectProvider } from './contexts/ProjectContext';

function App() {
  return (
    <ProjectProvider>
      <Container maxWidth="xl">
        <Box sx={{ my: 4 }}>
          <Dashboard />
        </Box>
      </Container>
    </ProjectProvider>
  );
}

export default App;