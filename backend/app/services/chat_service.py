from typing import Dict, Any, List
from app.services.tavus_service import TavusService
from app.services.knowledge_base_service import KnowledgeBaseService
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import requests

load_dotenv()

class ChatService:
    def __init__(self):
        self.tavus_service = TavusService()
        self.knowledge_base = KnowledgeBaseService()
        self.conversations: Dict[str, Dict[str, Any]] = {}
        self.tavus_api_key = os.getenv("TAVUS_API_KEY")
        self.tavus_replica_id = os.getenv("TAVUS_REPLICA_ID")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        # Initialize Gemini
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        print("ChatService initialized with:")
        print(f"TAVUS_API_KEY: {'Set' if self.tavus_api_key else 'Not set'}")
        print(f"TAVUS_REPLICA_ID: {'Set' if self.tavus_replica_id else 'Not set'}")
        print(f"GEMINI_API_KEY: {'Set' if self.gemini_api_key else 'Not set'}")

    async def start_conversation(self, subject: str, grade: str) -> Dict[str, Any]:
        """
        Start a new conversation with the AI tutor
        """
        try:
            # Check if required environment variables are set
            if not os.getenv("TAVUS_REPLICA_ID"):
                raise ValueError("TAVUS_REPLICA_ID environment variable is not set")
            if not os.getenv("GEMINI_API_KEY"):
                raise ValueError("GEMINI_API_KEY environment variable is not set")

            # Generate assessment context
            context = self._generate_assessment_context(subject, grade)
            
            print(f"Creating conversation with replica_id: {os.getenv('TAVUS_REPLICA_ID')}")  # Debug log
            
            # Create conversation with Tavus
            conversation = await self.tavus_service.create_conversation(
                replica_id=os.getenv("TAVUS_REPLICA_ID"),
                callback_url="http://localhost:8002/api/chat/callback",
                conversation_name=f"Assessment - {subject} Grade {grade}",
                conversational_context=context,
                custom_greeting=f"Hello! I'm your AI tutor for {subject}. I'll help assess your understanding of the subject.",
                max_call_duration=3600,
                participant_left_timeout=60,
                participant_absent_timeout=300,
                enable_recording=True,
                enable_transcription=True,
                apply_greenscreen=True,
                language="english"
            )
            
            print(f"Tavus response: {json.dumps(conversation, indent=2)}")  # Debug log
            
            if not conversation.get("conversation_id"):
                raise ValueError("No conversation ID received from Tavus")
            if not conversation.get("conversation_url"):
                raise ValueError("No conversation URL received from Tavus")
            
            # Store conversation ID for later use
            self.current_conversation_id = conversation.get("conversation_id")
            
            # Store conversation details
            self.conversations[self.current_conversation_id] = {
                "subject": subject,
                "grade": grade,
                "status": "active",
                "transcription": [],
                "teaching_plan": None,
                "videos": []
            }
            
            return {
                "conversation_id": self.current_conversation_id,
                "join_url": conversation.get("conversation_url"),
                "status": "started"
            }
        except Exception as e:
            print(f"Error in start_conversation: {str(e)}")
            # If there's an error, try to clean up any existing conversations
            try:
                await self.tavus_service.delete_all_conversations()
            except Exception as cleanup_error:
                print(f"Error cleaning up conversations: {str(cleanup_error)}")
            raise

    async def end_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        End a conversation and generate personalized teaching videos
        """
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        conversation_data = self.conversations[conversation_id]
        
        # End conversation with Tavus
        result = await self.tavus_service.end_conversation(conversation_id)
        
        # Generate personalized teaching plan using Gemini
        teaching_plan = await self._generate_teaching_plan(
            conversation_data["subject"],
            conversation_data["grade"],
            conversation_data["transcription"]
        )
        
        # Generate teaching videos for each topic
        videos = []
        for topic in teaching_plan["topics"]:
            video = await self.tavus_service.create_video(
                script=topic["script"],
                replica_id=os.getenv("TAVUS_REPLICA_ID")
            )
            videos.append({
                "topic": topic["name"],
                "video_url": video["hosted_url"],
                "status": video["status"]
            })
        
        # Update conversation status
        conversation_data["status"] = "completed"
        conversation_data["teaching_plan"] = teaching_plan
        conversation_data["videos"] = videos
        
        return {
            "status": "completed",
            "teaching_plan": teaching_plan,
            "videos": videos
        }

    async def _generate_teaching_plan(self, subject: str, grade: int, transcription: List[str]) -> Dict[str, Any]:
        """
        Generate personalized teaching plan using Gemini
        """
        # Create prompt for Gemini
        prompt = f"""Based on the following conversation with a student about {subject} at grade {grade}, 
        create a personalized teaching plan. The student's responses are:
        
        {' '.join(transcription)}
        
        Create a teaching plan that:
        1. Identifies the student's current understanding level
        2. Lists topics they need to learn, in order of priority
        3. Provides specific learning objectives for each topic
        4. Includes example problems or concepts to practice
        
        Format the response as JSON with the following structure:
        {{
            "understanding_level": "beginner/intermediate/advanced",
            "topics": [
                {{
                    "name": "Topic name",
                    "priority": 1-5,
                    "objectives": ["objective 1", "objective 2"],
                    "script": "Detailed teaching script for video"
                }}
            ]
        }}
        """
        
        response = await self.model.generate_content(prompt)
        return response.json()

    def _generate_assessment_context(self, subject: str, grade: str) -> str:
        """
        Generate context for the assessment conversation
        """
        return f"""You are an AI tutor conducting a comprehensive assessment for {subject} at grade {grade}.
        Your role is to thoroughly understand the student's current knowledge level through an extended conversation.
        
        Assessment Structure:
        1. Introduction (2-3 minutes)
           - Introduce yourself as an AI tutor
           - Explain that this is a comprehensive assessment
           - Ask about their overall experience with {subject}
        
        2. Core Concepts Assessment (5-7 minutes)
           - Ask about fundamental concepts in {subject}
           - Use specific examples and scenarios
           - Ask follow-up questions to clarify understanding
        
        3. Problem-Solving Assessment (5-7 minutes)
           - Present simple problems or scenarios
           - Ask how they would approach solving them
           - Listen to their reasoning process
        
        4. Knowledge Gaps (3-4 minutes)
           - Identify areas where they need improvement
           - Ask about specific topics they find challenging
           - Understand their learning preferences
        
        5. Wrap-up (2-3 minutes)
           - Summarize your understanding of their current level
           - Ask if they have any questions
           - Explain that you'll create a personalized learning plan
        
        Important Guidelines:
        - Keep the conversation natural and engaging
        - Don't rush through topics
        - Give students time to think and respond
        - Ask follow-up questions to clarify understanding
        - Only end the assessment after completing all sections
        - Minimum assessment duration should be 15-20 minutes
        
        Remember: This is a comprehensive assessment. Take your time to understand the student's knowledge level thoroughly."""

    async def handle_transcription(self, conversation_id: str, transcription: str):
        """
        Handle transcription updates from the conversation
        """
        if conversation_id in self.conversations:
            self.conversations[conversation_id]["transcription"].append(transcription)

    async def get_conversation_status(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get the status of a conversation
        """
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        return await self.tavus_service.get_conversation(conversation_id)

    def _generate_conversation_context(self, subject: str, grade: int, knowledge_base: Dict[str, Any]) -> str:
        """
        Generate the conversation context for the AI tutor
        """
        topics = [topic["name"] for topic in knowledge_base["topics"]]
        objectives = knowledge_base["learning_objectives"]
        
        return f"""You are an AI tutor for {subject} at grade {grade}. 
        Your role is to help students learn and understand {subject} through interactive conversation.
        
        Topics to cover: {', '.join(topics)}
        Learning objectives: {', '.join(objectives)}
        
        Start by introducing yourself and asking the student about their current understanding of {subject}.
        Then, based on their response, assess their knowledge level and adapt your teaching accordingly.
        Use the knowledge base to provide accurate information and examples.
        Keep the conversation engaging and interactive."""

    async def process_message(self, message: str, subject: str, grade: int) -> Dict[str, Any]:
        """
        Process user message and generate AI response with video
        """
        # Get subject knowledge base
        knowledge_base = await self.knowledge_base.get_subject_knowledge(subject, grade)
        
        # Generate response based on conversation history and knowledge base
        response_script = await self._generate_response(message, subject, grade, knowledge_base)
        
        # Create video response
        video_response = await self.tavus_service.create_video(
            script=response_script,
            avatar_id="default_teacher"
        )

        # Update conversation history
        conversation_id = f"{subject}_{grade}_{len(self.conversation_history) - 1}"
        self.conversation_history[conversation_id].extend([
            {"role": "user", "content": message},
            {"role": "assistant", "content": response_script}
        ])

        # Check if assessment is complete
        assessment_complete = self._check_assessment_complete(conversation_id)

        return {
            "message": response_script,
            "video_url": video_response["video_url"],
            "assessment_complete": assessment_complete
        }

    def _generate_initial_script(self, subject: str, grade: int) -> str:
        """
        Generate initial greeting and assessment setup script
        """
        return f"""Hello! I'm your AI tutor for {subject} at grade {grade}. 
        I'll help you learn and understand {subject} better through interactive conversations.
        
        Let's start with a quick assessment of your current understanding. 
        Could you tell me what you know about {subject} so far? 
        Feel free to share any specific topics you're familiar with or areas you'd like to improve."""

    async def _generate_response(self, message: str, subject: str, grade: int, knowledge_base: Dict[str, Any]) -> str:
        """
        Generate AI response based on user message and knowledge base
        """
        # In a real implementation, this would use a more sophisticated language model
        # to generate contextual responses based on the conversation history and knowledge base
        
        # For now, we'll use a simple response generation
        if "don't know" in message.lower() or "not sure" in message.lower():
            return f"I understand you're not sure about {subject}. Let's start with the basics. " \
                   f"Would you like me to explain some fundamental concepts in {subject}?"
        else:
            return f"Thank you for sharing that about {subject}. " \
                   f"Based on your response, I can help you learn more about specific topics. " \
                   f"What would you like to focus on first?"

    def _check_assessment_complete(self, conversation_id: str) -> bool:
        """
        Check if the initial assessment is complete based on conversation history
        """
        # In a real implementation, this would use more sophisticated logic
        # to determine if enough information has been gathered for assessment
        return len(self.conversation_history[conversation_id]) >= 4  # Simple example 