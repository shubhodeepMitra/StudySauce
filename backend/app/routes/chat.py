from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any
from app.services.chat_service import ChatService
import json
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()
chat_service = ChatService()

class StartConversationRequest(BaseModel):
    subject: str
    grade: int

class EndConversationRequest(BaseModel):
    conversation_id: str

class MessageRequest(BaseModel):
    message: str
    subject: str
    grade: int

@router.post("/start")
async def start_conversation(request: Request) -> Dict[str, Any]:
    """
    Start a new conversation with the AI tutor
    """
    try:
        body = await request.json()
        logger.info(f"Received start conversation request with body: {body}")
        
        subject = body.get("subject")
        grade = body.get("grade")
        
        if not subject or not grade:
            logger.error(f"Missing required fields. Subject: {subject}, Grade: {grade}")
            raise HTTPException(status_code=400, detail="Subject and grade are required")
        
        logger.info(f"Starting conversation for subject: {subject}, grade: {grade}")
        result = await chat_service.start_conversation(subject, grade)
        logger.info(f"Conversation started successfully: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in start_conversation endpoint: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/end/{conversation_id}")
async def end_conversation(conversation_id: str) -> Dict[str, Any]:
    """
    End a conversation and generate personalized teaching videos
    """
    try:
        logger.info(f"Ending conversation: {conversation_id}")
        result = await chat_service.end_conversation(conversation_id)
        logger.info(f"Conversation ended successfully: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in end_conversation endpoint: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{conversation_id}")
async def get_conversation_status(conversation_id: str) -> Dict[str, Any]:
    """
    Get the status of a conversation
    """
    try:
        logger.info(f"Getting status for conversation: {conversation_id}")
        status = await chat_service.get_conversation_status(conversation_id)
        logger.info(f"Conversation status: {status}")
        return status
    except Exception as e:
        logger.error(f"Error in get_conversation_status endpoint: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/callback")
async def handle_callback(request: Request) -> Dict[str, Any]:
    """
    Handle callbacks from Tavus CVI
    """
    try:
        body = await request.json()
        logger.info(f"Received callback with body: {json.dumps(body, indent=2)}")
        
        event_type = body.get("event_type")
        conversation_id = body.get("conversation_id")
        
        if not event_type or not conversation_id:
            logger.error(f"Missing required fields in callback. Event type: {event_type}, Conversation ID: {conversation_id}")
            raise HTTPException(status_code=400, detail="Event type and conversation ID are required")
        
        logger.info(f"Processing callback for conversation {conversation_id}, event type: {event_type}")
        result = await chat_service.process_callback(conversation_id, event_type, body)
        logger.info(f"Callback processed successfully: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in handle_callback endpoint: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/message")
async def process_message(request: MessageRequest):
    """
    Process a user message and return AI response with video
    """
    try:
        response = await chat_service.process_message(
            request.message,
            request.subject,
            request.grade
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 