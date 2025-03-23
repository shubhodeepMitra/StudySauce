import React from 'react';
import { Container, CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import AITutor from './components/Tutor/AITutor';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container>
        <AITutor subject="physics" grade={7} />
      </Container>
    </ThemeProvider>
  );
}

export default App;
