# backend/app/models/detection.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime

class BoundingBoxSchema(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float
    
    def to_dict(self):
        return {
            "x1": self.x1,
            "y1": self.y1,
            "x2": self.x2,
            "y2": self.y2,
            "confidence": self.confidence
        }

class ObjectDetectionSchema(BaseModel):
    class_name: str
    class_id: int
    bbox: BoundingBoxSchema
    confidence: float
    attributes: Optional[Dict[str, Any]] = {}

class LicensePlateDetectionSchema(BaseModel):
    plate_text: str
    bbox: BoundingBoxSchema
    confidence: float
    country: Optional[str] = None
    region: Optional[str] = None

class FaceDetectionSchema(BaseModel):
    face_id: Optional[int] = None
    bbox: BoundingBoxSchema
    confidence: float
    emotions: Optional[Dict[str, float]] = None
    age: Optional[float] = None
    gender: Optional[str] = None

class MotionDetectionSchema(BaseModel):
    points: List[List[float]]
    velocity: float
    direction: str
    area: float
    bbox: BoundingBoxSchema

class DetectionSchema(BaseModel):
    frame_id: str
    timestamp: datetime = datetime.now()
    camera_id: str
    objects: List[ObjectDetectionSchema] = []
    license_plates: List[LicensePlateDetectionSchema] = []
    faces: List[FaceDetectionSchema] = []
    motions: List[MotionDetectionSchema] = []
    total_objects: int = 0
    total_plates: int = 0
    total_faces: int = 0
    processing_time: float = 0.0
    
    class Config:
        json_schema_extra = {
            "example": {
                "frame_id": "frame_123",
                "camera_id": "cam1",
                "total_objects": 5,
                "objects": []
            }
        }