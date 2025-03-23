import React, { useState, useEffect } from 'react';
import { Box, Paper, Typography, Button, CircularProgress, Stepper, Step, StepLabel, List, ListItem, ListItemText, ListItemIcon, Alert } from '@mui/material';
import { CheckCircle as CheckCircleIcon } from '@mui/icons-material';

interface AITutorProps {
  subject: string;
  grade: number;
}

interface ConversationState {
  id: string;
  joinUrl: string;
  status: string;
}

interface TeachingPlan {
  understanding_level: string;
  topics: Array<{
    name: string;
    priority: number;
    objectives: string[];
    script: string;
  }>;
}

interface Video {
  topic: string;
  video_url: string;
  status: string;
}

const AITutor: React.FC<AITutorProps> = ({ subject, grade }) => {
  const [conversationState, setConversationState] = useState<ConversationState | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeStep, setActiveStep] = useState(0);
  const [teachingPlan, setTeachingPlan] = useState<TeachingPlan | null>(null);
  const [videos, setVideos] = useState<Video[]>([]);
  const [iframeKey, setIframeKey] = useState(0);
  const [selectedSubject, setSelectedSubject] = useState('');
  const [selectedGrade, setSelectedGrade] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    startConversation();
  }, []);

  useEffect(() => {
    if (conversationState?.joinUrl) {
      // Request permissions before loading iframe
      navigator.mediaDevices.getUserMedia({ audio: true, video: true })
        .then(() => {
          // Permissions granted, load iframe
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
      setLoading(true);
      setError(null);
      
      const response = await fetch('http://localhost:8002/api/chat/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          subject,
          grade
        })
      });

      if (!response.ok) {
        throw new Error('Failed to start conversation');
      }

      const data = await response.json();
      console.log('Backend response:', data);
      
      if (!data.join_url) {
        throw new Error('No join URL received from backend');
      }

      setConversationState({
        id: data.conversation_id,
        joinUrl: data.join_url,
        status: 'active'
      });
    } catch (err) {
      console.error('Error starting conversation:', err);
      setError(err instanceof Error ? err.message : 'Failed to start conversation');
    } finally {
      setLoading(false);
    }
  };

  const endConversation = async () => {
    if (!conversationState?.id) return;

    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`http://localhost:8002/api/chat/end/${conversationState.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error('Failed to end conversation');
      }

      const data = await response.json();
      setConversationState(prev => prev ? { ...prev, status: 'completed' } : null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to end conversation');
    } finally {
      setLoading(false);
    }
  };

  const steps = ['Initial Assessment', 'Learning Videos'];

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Paper elevation={3} sx={{ p: 4, maxWidth: 800, mx: 'auto', mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        AI Tutor Session - {subject} Grade {grade}
      </Typography>

      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      <Box sx={{ mt: 3 }}>
        {activeStep === 0 && conversationState ? (
          <Box>
            <Typography variant="h6" gutterBottom>
              Initial Assessment
            </Typography>
            <Typography paragraph>
              Please join the conversation with our AI tutor to assess your current understanding of {subject}.
            </Typography>
            
            <Box
              sx={{
                position: 'relative',
                paddingTop: '56.25%', // 16:9 aspect ratio
                width: '100%',
                mb: 3,
              }}
            >
              {conversationState?.joinUrl ? (
                <iframe
                  key={iframeKey}
                  src={conversationState.joinUrl}
                  className="w-full h-full border-0"
                  allow="microphone; camera; display-capture"
                  style={{ minHeight: '600px', border: 'none' }}
                />
              ) : (
                <div className="flex-1 flex items-center justify-center">
                  <div className="text-center">
                    <h2 className="text-2xl font-bold mb-4">Welcome to AI Tutor</h2>
                    <p className="mb-4">Select a subject and grade to start your assessment</p>
                    <div className="flex gap-4 justify-center">
                      <select
                        value={selectedSubject}
                        onChange={(e) => setSelectedSubject(e.target.value)}
                        className="p-2 border rounded"
                      >
                        <option value="">Select Subject</option>
                        <option value="physics">Physics</option>
                        <option value="chemistry">Chemistry</option>
                        <option value="biology">Biology</option>
                        <option value="mathematics">Mathematics</option>
                      </select>
                      <select
                        value={selectedGrade}
                        onChange={(e) => setSelectedGrade(e.target.value)}
                        className="p-2 border rounded"
                      >
                        <option value="">Select Grade</option>
                        {[7, 8, 9, 10, 11, 12].map((grade) => (
                          <option key={grade} value={grade}>
                            Grade {grade}
                          </option>
                        ))}
                      </select>
                    </div>
                    <button
                      onClick={startConversation}
                      disabled={!selectedSubject || !selectedGrade || isLoading}
                      className={`mt-4 px-4 py-2 rounded ${
                        !selectedSubject || !selectedGrade || isLoading
                          ? 'bg-gray-300 cursor-not-allowed'
                          : 'bg-blue-500 hover:bg-blue-600 text-white'
                      }`}
                    >
                      {isLoading ? 'Starting...' : 'Start Assessment'}
                    </button>
                  </div>
                </div>
              )}
            </Box>

            <Button
              variant="contained"
              color="primary"
              onClick={endConversation}
              disabled={conversationState.status === 'completed'}
              fullWidth
            >
              End Assessment
            </Button>
          </Box>
        ) : activeStep === 1 && teachingPlan ? (
          <Box>
            <Typography variant="h6" gutterBottom>
              Your Personalized Learning Plan
            </Typography>
            <Typography variant="subtitle1" gutterBottom>
              Understanding Level: {teachingPlan.understanding_level}
            </Typography>

            <Typography variant="subtitle1" gutterBottom>
              Topics to Learn:
            </Typography>
            <List>
              {teachingPlan.topics.map((topic, index) => (
                <ListItem key={index}>
                  <ListItemText
                    primary={topic.name}
                    secondary={
                      <>
                        <Typography component="span" variant="body2">
                          Priority: {topic.priority}/5
                        </Typography>
                        <br />
                        <Typography component="span" variant="body2">
                          Objectives: {topic.objectives.join(', ')}
                        </Typography>
                      </>
                    }
                  />
                </ListItem>
              ))}
            </List>

            <Typography variant="subtitle1" gutterBottom sx={{ mt: 3 }}>
              Learning Videos:
            </Typography>
            <List>
              {videos.map((video, index) => (
                <ListItem key={index}>
                  <ListItemText
                    primary={video.topic}
                    secondary={
                      <Button
                        variant="outlined"
                        href={video.video_url}
                        target="_blank"
                        disabled={video.status !== 'completed'}
                      >
                        {video.status === 'completed' ? 'Watch Video' : 'Processing...'}
                      </Button>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        ) : (
          <Typography>
            Starting assessment...
          </Typography>
        )}
      </Box>
    </Paper>
  );
};

export default AITutor; 