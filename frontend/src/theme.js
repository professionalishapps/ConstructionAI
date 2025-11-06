import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    success: {
      main: '#10b981', // Green - low risk
    },
    warning: {
      main: '#f59e0b', // Yellow - medium risk
    },
    error: {
      main: '#ef4444', // Red - high risk
    },
    primary: {
      main: '#6366f1', // Indigo - primary actions
    },
    grey: {
      main: '#64748b', // Gray - neutral
    },
  },
});

export default theme;