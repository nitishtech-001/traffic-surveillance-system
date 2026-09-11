# backend/app/api/routes/camera.py
from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Dict, Any
from datetime import datetime

from app.schema.schema_camera import CameraSchema, CameraStatusSchema
from app.services.camera_manager import CameraManager
from app.api.dependencies.authenticate import get_current_user

router = APIRouter()

camera_manager = CameraManager()

@router.post("/add", response_model=Dict[str, Any])
async def add_camera(
    camera: CameraSchema,
    # current_user: Dict = Depends(get_current_user)
):
    """
    Add a new camera to the system
    """
    try:
        # Check if camera already exists
        print(camera)
        existing = camera_manager.active_cameras.get(camera.id)
        if existing:
            raise HTTPException(status_code=400, detail="Camera already exists")
        
        # Add camera
        success = await camera_manager.add_camera(camera)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to add camera")
        
        return {
            "message": f"Camera with id {camera.id} added successfully",
            "status": CameraStatusSchema.CONNECTING
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list", response_model=List[Dict[str, Any]])
async def list_cameras(
    # current_user: Dict = Depends(get_current_user)
):
    """
    List all cameras with their status
    """
    try:
        cameras = await camera_manager.list_cameras()
        return cameras
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{camera_id}/info", response_model=Dict[str, Any])
async def get_camera_info(
    camera_id: str,
    # current_user: Dict = Depends(get_current_user)
):
    """
    Get detailed information about a specific camera
    """
    try:
        print("Inside camera info route camers_id :::: ", camera_id)
        info = await camera_manager.get_camera_info(camera_id)
        if not info:
            print("Again check the info")
            raise HTTPException(status_code=404, detail="Camera not found")
        return info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{camera_id}/disconnect", response_model=Dict[str, Any])
async def disconnect_camera(
    camera_id: str,
    # current_user: Dict = Depends(get_current_user)
):
    """
    Disconnect a camera
    """
    try:
        success = await camera_manager.disconnect_camera(camera_id)
        if not success:
            raise HTTPException(status_code=404, detail="Camera not found")
        
        return {
            "message": "Camera disconnected successfully",
            "camera_id": camera_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{camera_id}/update", response_model=Dict[str, Any])
async def update_camera_settings(
    camera_id: str,
    settings: Dict[str, Any] = Body(...),
    # current_user: Dict = Depends(get_current_user)
):
    """
    Update camera settings
    """
    try:
        success = await camera_manager.update_camera_settings(camera_id, settings)
        if not success:
            raise HTTPException(status_code=404, detail="Camera not found")
        
        return {
            "message": "Camera settings updated successfully",
            "camera_id": camera_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
