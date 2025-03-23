from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.services.tavus_service import TavusService
from app.services.assessment_service import AssessmentService

router = APIRouter()
tavus_service = TavusService()
assessment_service = AssessmentService()

@router.post("/assessment/create")
async def create_assessment(subject: str, grade: int, student_id: str) -> Dict[str, Any]:
    """
    Create a new assessment for a student
    """
    try:
        return assessment_service.create_assessment(subject, grade, student_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/assessment/{assessment_id}/level")
async def update_level(assessment_id: str, level: int) -> Dict[str, Any]:
    """
    Update student's current level
    """
    try:
        return assessment_service.update_assessment_level(assessment_id, level)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/assessment/{assessment_id}/checkpoint")
async def add_checkpoint(assessment_id: str, checkpoint_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add a new checkpoint to track progress
    """
    try:
        return assessment_service.add_checkpoint(assessment_id, checkpoint_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/assessment/{assessment_id}/roadmap")
async def get_roadmap(assessment_id: str) -> Dict[str, Any]:
    """
    Get learning roadmap based on current level
    """
    try:
        return assessment_service.get_roadmap(assessment_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/video/create")
async def create_video(script: str, avatar_id: str) -> Dict[str, Any]:
    """
    Create a new video using Tavus API
    """
    try:
        return await tavus_service.create_video(script, avatar_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/video/{video_id}/status")
async def get_video_status(video_id: str) -> Dict[str, Any]:
    """
    Get video generation status
    """
    try:
        return await tavus_service.get_video_status(video_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/avatars")
async def get_avatars() -> Dict[str, Any]:
    """
    Get available avatars
    """
    try:
        return await tavus_service.get_avatars()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 