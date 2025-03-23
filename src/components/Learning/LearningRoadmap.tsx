import React from 'react';
import { Box, Paper, Typography, Stepper, Step, StepLabel, Card, CardContent, Grid } from '@mui/material';

interface Topic {
  level: number;
  topics: string[];
  estimated_time: string;
}

interface LearningRoadmapProps {
  currentLevel: number;
  nextSteps: Topic[];
}

const LearningRoadmap: React.FC<LearningRoadmapProps> = ({ currentLevel, nextSteps }) => {
  return (
    <Paper elevation={3} sx={{ p: 4, maxWidth: 800, mx: 'auto', mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        Your Learning Journey
      </Typography>
      
      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" gutterBottom>
          Current Level: {currentLevel}
        </Typography>
        
        <Stepper activeStep={0} alternativeLabel sx={{ mt: 4 }}>
          {nextSteps.map((step, index) => (
            <Step key={index}>
              <StepLabel>
                Level {step.level}
              </StepLabel>
            </Step>
          ))}
        </Stepper>

        <Grid container spacing={3} sx={{ mt: 2 }}>
          {nextSteps.map((step, index) => (
            <Grid item xs={12} md={6} key={index}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Level {step.level}
                  </Typography>
                  <Typography variant="subtitle1" color="text.secondary" gutterBottom>
                    Estimated Time: {step.estimated_time}
                  </Typography>
                  <Typography variant="body1">
                    Topics to Cover:
                  </Typography>
                  <ul>
                    {step.topics.map((topic, topicIndex) => (
                      <li key={topicIndex}>
                        <Typography variant="body2">{topic}</Typography>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    </Paper>
  );
};

export default LearningRoadmap; 