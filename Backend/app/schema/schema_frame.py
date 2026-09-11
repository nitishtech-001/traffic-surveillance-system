# backend/app/models/frame.py
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import numpy as np

class FrameMetadataSchema(BaseModel):
    """Metadata for a video frame"""
    width: int
    height: int
    channels: int = 3
    fps: float = 30.0
    timestamp: datetime = datetime.now()
    frame_id: str
    camera_id: str
    # TODO : REMOVE these this is for only fastapi calling simplicity
    class Config:
        json_schema_extra = {
            "example": {
                "width": 1920,
                "height": 1080,
                "channels": 3,
                "fps": 30.0,
                "frame_id": "frame_123456",
                "camera_id": "cam1"
            }
        }

class FrameSchema(BaseModel):
    """Video frame with metadata and optional processed data"""
    frame_id: str
    camera_id: str
    timestamp: datetime = datetime.now()
    metadata: Optional[FrameMetadataSchema] = None
    processed_data: Optional[Dict[str, Any]] = None
    annotations: Optional[Dict[str, Any]] = None
    
    class Config:
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "frame_id": "frame_123456",
                "camera_id": "cam1",
                "timestamp": "2024-01-01T10:00:00",
                "metadata": {
                    "width": 1920,
                    "height": 1080,
                    "channels": 3
                }
            }
        }