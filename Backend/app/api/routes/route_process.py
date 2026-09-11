# backend/app/api/routes/process.py
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any
import cv2
import numpy as np
import base64

from app.services.camera_manager import CameraManager
from app.services.agent_orchestrator import AgentOrchestrator
from app.api.dependencies.authenticate import get_current_user

router = APIRouter()

agent_orchestrator = AgentOrchestrator()
camera_manager = CameraManager()

@router.post("/frame/{camera_id}")
async def process_frame(
    camera_id: str,
    background_tasks: BackgroundTasks,
    # current_user: Dict = Depends(get_current_user)
):
    """
    Process a single frame from a camera
    """
    try:
        # Get frame from camera
        frame = await camera_manager.get_frame(camera_id)
        if frame is None:
            raise HTTPException(status_code=404, detail="No frame available")
        
        # Process frame through agents
        
        result = await agent_orchestrator.process_frame(frame, camera_id)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/queue/{camera_id}")
async def queue_frame_processing(
    camera_id: str,
    background_tasks: BackgroundTasks,
    # current_user: Dict = Depends(get_current_user)
):
    """
    Queue a frame for background processing
    """
    try:
        # Get frame from camera
        frame = await camera_manager.get_frame(camera_id)
        if frame is None:
            raise HTTPException(status_code=404, detail="No frame available")
        
        # Queue for processing
        await agent_orchestrator.queue_frame(frame, camera_id)
        
        return {
            "message": "Frame queued for processing",
            "camera_id": camera_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results/{camera_id}")
async def get_results(
    camera_id: str,
    limit: int = 10,
    # current_user: Dict = Depends(get_current_user)
):
    """
    Get processing results for a camera
    """
    try:
        results = await agent_orchestrator.get_results(camera_id, limit)
        return {
            "camera_id": camera_id,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results/{camera_id}/latest")
async def get_latest_result(
    camera_id: str,
    # current_user: Dict = Depends(get_current_user)
):
    """
    Get the latest processing result for a camera
    """
    try:
        result = await agent_orchestrator.get_last_result(camera_id)
        if not result:
            raise HTTPException(status_code=404, detail="No results found")
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))