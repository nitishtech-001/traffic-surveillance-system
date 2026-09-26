# backend/app/core/config.py
from dotenv import load_dotenv
import os

load_dotenv()
class Settings:
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
    AGENT_MODEL_PATH: str = os.path.join(os.getcwd()+"/ai_models")
    AGENT_MODEL_OBJECT_DETECTION: str = "object_detection.pt"
    # add other agent_model_names
    CONFIDENCE_THRESHOLD: float = 0.5
    
    # Streaming
    WEBRTC_DURATION: int = 1
    MAX_STREAMS: int = 10
    
    
    # WebSocket
    WS_MAX_SIZE: int = 1048576
    WS_PING_INTERVAL: int = 20
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()