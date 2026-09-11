# backend/app/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Video Analysis System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = "nitish@"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security
    JWT_SECRET_KEY: str = "nitish@8789"
    JWT_ALGORITHM: str = "algorithm"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Camera
    CAMERA_USERNAME: str = "admin"
    CAMERA_PASSWORD: str = "password"
    RTSP_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    
    # AI Models
    MODELS_PATH: str = "./ai_models"
    YOLO_MODEL: str = "nightvision.pt"
    CONFIDENCE_THRESHOLD: float = 0.5
    
    # Streaming
    HLS_SEGMENT_DURATION: int = 1
    HLS_SEGMENT_COUNT: int = 3
    MAX_STREAMS: int = 10
    
    # Redis
    REDIS_URL: Optional[str] = None
    
    # WebSocket
    WS_MAX_SIZE: int = 1048576
    WS_PING_INTERVAL: int = 20
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()