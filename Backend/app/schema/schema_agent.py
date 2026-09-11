# backend/app/models/agent.py
from pydantic import BaseModel
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime

class AgentTypeSchema(str, Enum):
    OBJECT_DETECTION = "object-detection"
    FACE_DETECTION = "face-detection"
    LICENSE_PLATE = "license-plate"
    MOTION_TRACKING = "motion-tracking"
    TEXT_RECOGNITION = "text-recognition"
    SCENE_CLASSIFICATION = "scene-classification"

class AgentStatusSchema(str, Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"

class AgentSchema(BaseModel):
    id: str
    name: str
    type: AgentTypeSchema
    status: AgentStatusSchema = AgentStatusSchema.IDLE
    active: bool = False
    config: Dict[str, Any] = {}
    performance: Dict[str, Any] = {}
    last_processed: Optional[datetime] = None
    created_at: datetime = datetime.now()
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "agent1",
                "name": "Object Detection Agent",
                "type": "object-detection",
                "active": True,
                "config": {
                    "confidence": 0.5,
                    "model": "nightvision"
                }
            }
        }