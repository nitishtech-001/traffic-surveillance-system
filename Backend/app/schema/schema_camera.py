# backend/app/models/camera.py
from pydantic import BaseModel
from enum import Enum
from typing import Optional
from datetime import datetime

class CameraStatusSchema(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    CONNECTING = "connecting"
    ERROR = "error"
    STREAMING = "streaming"

class CameraSchema(BaseModel):
    id: str
    name: str
    ip_address: str
    port: int = 554
    username: Optional[str] = None
    password: Optional[str] = None
    protocol: str = "rtsp"
    model: Optional[str] = None
    status: CameraStatusSchema = CameraStatusSchema.OFFLINE
    stream_url: Optional[str] = None
    last_connected: Optional[datetime] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "cam1",
                "name": "Front gate camera",
                "username": "nk",
                "password": "nk001",
                "ip_address": "192.168.29.2",
                "port": 8080,
                "protocol": "http",
                "status": "offline"
            }
        }