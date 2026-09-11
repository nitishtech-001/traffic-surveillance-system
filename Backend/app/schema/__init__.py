# backend/app/models/__init__.py
from .schema_camera import CameraSchema, CameraStatusSchema
from .schema_frame import FrameSchema, FrameMetadataSchema
from .schema_agent import AgentSchema, AgentTypeSchema, AgentStatusSchema
from .schema_detection import (
    DetectionSchema, 
    BoundingBoxSchema, 
    ObjectDetectionSchema,
    LicensePlateDetectionSchema,
    FaceDetectionSchema,
    MotionDetectionSchema
)

__all__ = [
    "CameraSchema", 
    "CameraStatusSchema",
    "FrameSchema", 
    "FrameMetadataSchema",
    "AgentSchema", 
    "AgentTypeSchema", 
    "AgentStatusSchema",
    "DetectionSchema", 
    "BoundingBoxSchema",
    "ObjectDetectionSchema", 
    "LicensePlateDetectionSchema",
    "FaceDetectionSchema",
    "MotionDetectionSchema"
]