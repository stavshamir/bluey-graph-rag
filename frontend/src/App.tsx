import './App.css';
import { ThemeProvider } from '@emotion/react';
import { createTheme, CssBaseline } from '@mui/material';
import ThemeExplorer from './ThemeExplorer';

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
      <ThemeExplorer></ThemeExplorer>
    </ThemeProvider>
  );
}

export default App;
