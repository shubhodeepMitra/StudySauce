import React, { useState, useEffect } from 'react';
import { Box, Paper, Typography, Button, CircularProgress, Alert, Container, Grid } from '@mui/material';
import { CheckCircle as CheckCircleIcon } from '@mui/icons-material';

interface AITutorProps {
  subject: string;
  grade: number;
}

interface ConversationState {
  id: string;
  joinUrl: string;
  status: 'pending' | 'active' | 'ended' | 'completed';
}

interface TeachingPlan {
  topics: string[];
  difficulty: string;
  duration: string;
}

interface Video {
  id: string;
  title: string;
  url: string;
  duration: string;
}

const AITutor: React.FC<AITutorProps> = ({ subject, grade }) => {
  const [conversationState, setConversationState] = useState<ConversationState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected');
  const [iframeKey, setIframeKey] = useState(0);

  // Connection status listener
  useEffect(() => {
    const checkConnection = async () => {
      try {
        const response = await fetch('http://localhost:8002/');
        if (response.ok) {
          setConnectionStatus('connected');
        } else {
          setConnectionStatus('disconnected');
        }
      } catch (error) {
        console.error('Connection check failed:', error);
        setConnectionStatus('disconnected');
      }
    };

    checkConnection();
    const interval = setInterval(checkConnection, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (conversationState?.joinUrl) {
      navigator.mediaDevices.getUserMedia({ audio: true, video: true })
        .then(() => {
          setIframeKey(Date.now());
        })
        .catch((error) => {
          console.error('Error requesting permissions:', error);
          setError('Please allow microphone and camera access to use the AI tutor.');
        });
    }
  }, [conversationState?.joinUrl]);

  const startConversation = async () => {
    try {
      setIsLoading(true);
      setError(null);
      setConnectionStatus('connecting');

      const response = await fetch('http://localhost:8002/api/chat/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          subject,
          grade,
        }),
        credentials: 'include',
      });

      if (!response.ok) {
        const errorData = await response.json();
        if (errorData.message) {
          throw new Error(errorData.message);
        } else {
          throw new Error('Unable to start the learning session. Please try again later.');
        }
      }

      const data = await response.json();
      console.log('Backend response:', data); // Debug log

      // Update conversation state with the correct response format
      setConversationState({
        id: data.conversation_id,
        joinUrl: data.join_url,
        status: data.status
      });
      
      setConnectionStatus('connected');
    } catch (error) {
      console.error('Error starting conversation:', error);
      setError(error instanceof Error ? error.message : 'Unable to start the learning session. Please try again later.');
      setConnectionStatus('disconnected');
    } finally {
      setIsLoading(false);
    }
  };

  const endConversation = async () => {
    if (!conversationState?.id) return;

    try {
      const response = await fetch(`http://localhost:8002/api/chat/end/${conversationState.id}`, {
        method: 'POST',
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error('Unable to end the learning session. Please try again later.');
      }

      setConversationState(null);
    } catch (error) {
      console.error('Error ending conversation:', error);
      setError('Unable to end the learning session. Please try again later.');
    }
  };

  return (
    <Box
      sx={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'auto'
      }}
    >
      <Container 
        maxWidth={false}
        sx={{
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          p: 4
        }}
      >
        <Grid 
          container 
          justifyContent="center" 
          alignItems="center"
        >
          <Grid item xs={12} md={10} lg={8} xl={6}>
            {conversationState?.joinUrl ? (
              <Paper elevation={3} sx={{ 
                display: 'flex', 
                flexDirection: 'column', 
                overflow: 'hidden',
                height: '90vh'
              }}>
                <Box sx={{ 
                  p: 2, 
                  borderBottom: 1, 
                  borderColor: 'divider', 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  background: 'linear-gradient(90deg, #2196f3 0%, #1976d2 100%)',
                  color: 'white'
                }}>
                  <Typography variant="h6">
                    AI Tutor Session - {subject} Grade {grade}
                  </Typography>
                  <Button
                    variant="contained"
                    color="error"
                    onClick={endConversation}
                    startIcon={<CheckCircleIcon />}
                  >
                    End Learning Session
                  </Button>
                </Box>
                <Box sx={{ flex: 1, position: 'relative', overflow: 'hidden' }}>
                  <iframe
                    key={iframeKey}
                    src={conversationState.joinUrl}
                    style={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      width: '100%',
                      height: '100%',
                      border: 'none',
                    }}
                    allow="microphone; camera; display-capture"
                  />
                </Box>
              </Paper>
            ) : (
              <Paper 
                elevation={3} 
                sx={{ 
                  p: 6,
                  display: 'flex', 
                  flexDirection: 'column', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  minHeight: '500px',
                  width: '100%',
                  background: 'white',
                  borderRadius: '16px',
                  position: 'relative',
                  overflow: 'hidden',
                  '&::before': {
                    content: '""',
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    height: '8px',
                    background: 'linear-gradient(90deg, #2196f3 0%, #1976d2 100%)',
                  }
                }}
              >
                <Typography 
                  variant="h3" 
                  gutterBottom 
                  align="center"
                  sx={{
                    fontWeight: 700,
                    background: 'linear-gradient(45deg, #2196f3 30%, #21cbf3 90%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    mb: 4
                  }}
                >
                  Welcome to Your AI Learning Partner
                </Typography>
                <Typography 
                  variant="h5" 
                  color="primary" 
                  gutterBottom 
                  align="center"
                  sx={{ fontWeight: 600 }}
                >
                  Subject: {subject}
                </Typography>
                <Typography 
                  variant="h5" 
                  color="primary" 
                  gutterBottom 
                  align="center"
                  sx={{ fontWeight: 600 }}
                >
                  Grade: {grade}
                </Typography>
                <Typography 
                  variant="body1" 
                  color="text.secondary" 
                  sx={{ 
                    mb: 6, 
                    textAlign: 'center', 
                    maxWidth: '600px',
                    fontSize: '1.1rem',
                    lineHeight: 1.6
                  }}
                >
                  Ready to start your personalized learning journey? Your AI tutor will help you understand {subject} better.
                </Typography>
                <Button
                  variant="contained"
                  color="primary"
                  size="large"
                  onClick={startConversation}
                  disabled={isLoading || connectionStatus !== 'connected'}
                  sx={{ 
                    mt: 2, 
                    minWidth: '200px',
                    py: 1.5,
                    px: 4,
                    borderRadius: '30px',
                    fontSize: '1.1rem',
                    fontWeight: 600,
                    background: 'linear-gradient(45deg, #2196f3 30%, #21cbf3 90%)',
                    boxShadow: '0 3px 5px 2px rgba(33, 203, 243, .3)',
                    '&:hover': {
                      background: 'linear-gradient(45deg, #1976d2 30%, #2196f3 90%)',
                    }
                  }}
                >
                  {isLoading ? (
                    <>
                      <CircularProgress size={24} sx={{ mr: 1 }} />
                      Starting Learning Session...
                    </>
                  ) : (
                    'Start Learning'
                  )}
                </Button>
              </Paper>
            )}
          </Grid>
        </Grid>
      </Container>

      {/* Debug Status Indicator */}
      <Box
        sx={{
          position: 'fixed',
          bottom: 16,
          right: 16,
          zIndex: 1000,
          backgroundColor: error ? 'error.main' :
                          connectionStatus === 'connected' ? 'success.main' : 
                          connectionStatus === 'connecting' ? 'warning.main' : 'error.main',
          color: 'white',
          padding: '8px 16px',
          borderRadius: '20px',
          boxShadow: '0 3px 5px 2px rgba(0, 0, 0, .1)',
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          maxWidth: '300px',
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          fontSize: '0.75rem'
        }}
      >
        {connectionStatus === 'connecting' && <CircularProgress size={16} sx={{ color: 'white' }} />}
        <Typography variant="body2" sx={{ fontSize: '0.75rem' }}>
          {error ? error :
           connectionStatus === 'connected' ? 'Connected' :
           connectionStatus === 'connecting' ? 'Connecting...' : 'Disconnected'}
        </Typography>
      </Box>
    </Box>
  );
};

export default AITutor; 