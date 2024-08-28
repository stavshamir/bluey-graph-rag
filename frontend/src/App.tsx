import './App.css';
import { ThemeProvider } from '@emotion/react';
import { createTheme, CssBaseline, Box, IconButton } from '@mui/material';
import ThemeExplorer from './ThemeExplorer';
import GitHubIcon from '@mui/icons-material/GitHub';
import LinkedInIcon from '@mui/icons-material/LinkedIn';

const blueyTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#3498db', // Primary blue
    },
    secondary: {
      main: '#5dade2', // Secondary blue
    },
    background: {
      default: '#aed6f1', // Light blue background
      paper: '#d6eaf8', // Lighter blue for paper elements
    },
    text: {
      primary: '#2874a6', // Dark blue for primary text
      secondary: '#3498db', // Primary blue for secondary text
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={blueyTheme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
        <Box
          component="header"
          sx={{
            py: 1,
            px: 2,
            backgroundColor: '#2874a6', 
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <Box sx={{ height: '40px', flexGrow: 1 }}>
            <img src="/Bluey_Icon.png" alt="Bluey Icon" style={{ height: '100%' }} />
          </Box>
          <Box sx={{ display: 'flex' }}>
            <IconButton
              sx={{ color: 'white' }}
              href="https://github.com/stavshamir/bluey-graph-rag"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="GitHub"
            >
              <GitHubIcon fontSize="large" />
            </IconButton>
            <IconButton
              sx={{ color: 'white' }}
              href="https://www.linkedin.com/in/stavshamir/"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="LinkedIn"
            >
              <LinkedInIcon fontSize="large" />
            </IconButton>
          </Box>
        </Box>
        <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
          <ThemeExplorer />
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;
