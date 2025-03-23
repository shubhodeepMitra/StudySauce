from typing import Dict, List, Any
from datetime import datetime
from app.services.tavus_service import TavusService

class AssessmentService:
    def __init__(self):
        self.assessment_data = {}  # In production, use a database
        self.tavus_service = TavusService()

    async def create_assessment(self, subject: str, grade: int, student_id: str) -> Dict[str, Any]:
        """
        Create a new assessment and generate initial assessment video
        """
        assessment_id = f"{student_id}_{subject}_{grade}_{datetime.now().timestamp()}"
        self.assessment_data[assessment_id] = {
            "id": assessment_id,
            "subject": subject,
            "grade": grade,
            "student_id": student_id,
            "created_at": datetime.now().isoformat(),
            "current_level": None,
            "checkpoints": [],
            "progress": 0,
            "assessment_videos": []
        }

        # Generate initial assessment video
        initial_script = self._generate_assessment_script(subject, grade)
        video_response = await self.tavus_service.create_video(
            script=initial_script,
            avatar_id="default_teacher"  # You'll need to set up a default teacher avatar
        )
        
        self.assessment_data[assessment_id]["assessment_videos"].append({
            "id": video_response["id"],
            "url": video_response["video_url"],
            "type": "initial_assessment",
            "created_at": datetime.now().isoformat()
        })

        return self.assessment_data[assessment_id]

    def _generate_assessment_script(self, subject: str, grade: int) -> str:
        """
        Generate a conversational script for initial assessment
        """
        return f"""Hello! I'm your AI tutor for {subject} at grade {grade}. 
        I'll help you assess your current understanding of the subject through a friendly conversation.
        
        Let's start with some basic questions:
        1. What topics in {subject} do you feel most comfortable with?
        2. Are there any specific areas where you think you need more help?
        3. How do you usually learn best - through examples, practice problems, or visual explanations?
        
        Please share your thoughts, and I'll help create a personalized learning path for you."""

    async def update_assessment_level(self, assessment_id: str, level: int, feedback: str) -> Dict[str, Any]:
        """
        Update the student's current level and generate feedback video
        """
        if assessment_id not in self.assessment_data:
            raise ValueError("Assessment not found")
        
        self.assessment_data[assessment_id]["current_level"] = level
        
        # Generate feedback video
        feedback_script = self._generate_feedback_script(level, feedback)
        video_response = await self.tavus_service.create_video(
            script=feedback_script,
            avatar_id="default_teacher"
        )
        
        self.assessment_data[assessment_id]["assessment_videos"].append({
            "id": video_response["id"],
            "url": video_response["video_url"],
            "type": "feedback",
            "created_at": datetime.now().isoformat()
        })
        
        return self.assessment_data[assessment_id]

    def _generate_feedback_script(self, level: int, feedback: str) -> str:
        """
        Generate a feedback script based on assessment results
        """
        return f"""Based on our conversation, I understand your current level is around {level}.
        {feedback}
        
        Let me create a personalized learning path for you. We'll focus on building your understanding step by step.
        Would you like to start with the first topic?"""

    async def add_checkpoint(self, assessment_id: str, checkpoint_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a new checkpoint and generate checkpoint video
        """
        if assessment_id not in self.assessment_data:
            raise ValueError("Assessment not found")
        
        checkpoint_id = f"checkpoint_{len(self.assessment_data[assessment_id]['checkpoints'])}"
        checkpoint_data["id"] = checkpoint_id
        checkpoint_data["created_at"] = datetime.now().isoformat()
        
        self.assessment_data[assessment_id]["checkpoints"].append(checkpoint_data)
        
        # Generate checkpoint video
        checkpoint_script = self._generate_checkpoint_script(checkpoint_data)
        video_response = await self.tavus_service.create_video(
            script=checkpoint_script,
            avatar_id="default_teacher"
        )
        
        checkpoint_data["video"] = {
            "id": video_response["id"],
            "url": video_response["video_url"],
            "created_at": datetime.now().isoformat()
        }
        
        return checkpoint_data

    def _generate_checkpoint_script(self, checkpoint_data: Dict[str, Any]) -> str:
        """
        Generate a script for checkpoint videos
        """
        return f"""Great progress! Let's review what we've covered:
        {checkpoint_data.get('summary', '')}
        
        Here are some key points to remember:
        {checkpoint_data.get('key_points', '')}
        
        Would you like to practice some exercises or move on to the next topic?"""

    async def get_roadmap(self, assessment_id: str) -> Dict[str, Any]:
        """
        Generate a learning roadmap based on current level
        """
        if assessment_id not in self.assessment_data:
            raise ValueError("Assessment not found")
        
        assessment = self.assessment_data[assessment_id]
        current_level = assessment["current_level"] or 0
        
        # Generate roadmap video
        roadmap_script = self._generate_roadmap_script(assessment)
        video_response = await self.tavus_service.create_video(
            script=roadmap_script,
            avatar_id="default_teacher"
        )
        
        roadmap = {
            "current_level": current_level,
            "next_steps": [
                {
                    "level": current_level + 1,
                    "topics": self._get_topics_for_level(assessment["subject"], current_level + 1),
                    "estimated_time": "2-3 hours"
                },
                {
                    "level": current_level + 2,
                    "topics": self._get_topics_for_level(assessment["subject"], current_level + 2),
                    "estimated_time": "3-4 hours"
                }
            ],
            "video": {
                "id": video_response["id"],
                "url": video_response["video_url"],
                "created_at": datetime.now().isoformat()
            }
        }
        
        return roadmap

    def _generate_roadmap_script(self, assessment: Dict[str, Any]) -> str:
        """
        Generate a script for the roadmap video
        """
        return f"""Based on our assessment, I've created a personalized learning path for you in {assessment['subject']}.
        We'll start at level {assessment['current_level']} and work our way up.
        
        Here's what we'll cover:
        {self._format_topics_for_script(assessment['subject'], assessment['current_level'])}
        
        Let's begin with the first topic. Are you ready?"""

    def _format_topics_for_script(self, subject: str, level: int) -> str:
        """
        Format topics for the roadmap video script
        """
        topics = self._get_topics_for_level(subject, level)
        return "\n".join([f"- {topic}" for topic in topics])

    def _get_topics_for_level(self, subject: str, level: int) -> List[str]:
        """
        Get topics for a specific subject and level
        """
        topics = {
            "physics": {
                7: ["Forces and Motion", "Energy", "Waves", "Electricity"],
                8: ["Newton's Laws", "Work and Energy", "Sound and Light", "Magnetism"]
            },
            "mathematics": {
                7: ["Algebra Basics", "Geometry", "Statistics", "Number Theory"],
                8: ["Linear Equations", "Pythagorean Theorem", "Probability", "Functions"]
            }
        }
        
        return topics.get(subject, {}).get(level, []) 