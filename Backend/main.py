# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import logging
from contextlib import asynccontextmanager
import os

# Routes
from app.api.routes import route_agents, route_auth, route_camera, route_stream, route_websocket, route_process

# Configuration
from app.core.config import settings


# Services
from app.services.stream_manager import StreamManager
from app.services.agent_orchestrator import AgentOrchestrator
from app.services.camera_manager import CameraManager

# Schema
from app.schema.schema_agent import AgentTypeSchema

# Setup logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize global services
camera_manager = CameraManager()
stream_manager = StreamManager()
agent_orchestrator = AgentOrchestrator()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager for startup and shutdown events"""
    # Startup
    logger.info("Starting Video Analysis System...")
    
    # adding default agents
    await agent_orchestrator.initialize()
    await agent_orchestrator.add_agent(AgentTypeSchema.OBJECT_DETECTION, {"confidence": 0.5})
    await agent_orchestrator.add_agent(AgentTypeSchema.LICENSE_PLATE, {"languages": ["en"]})
    await agent_orchestrator.add_agent(AgentTypeSchema.OBJECT_DETECTION)

    logger.info(f"Initialized {len(agent_orchestrator.agents)} agents.")

    yield
    

    # Shutdown
    logger.info("Shutting down...")
    await camera_manager.disconnect_all()
    await stream_manager.stop_all_streams()
    # await agent_orchestrator.cleanup_all()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(route_camera.router, prefix="/api/cameras", tags=["Cameras"])

app.include_router(route_stream.router, prefix="/api/streams", tags=["Streams"])

app.include_router(route_auth.router, prefix="/api/auth", tags=["Register"])

app.include_router(route_agents.router, prefix="/api/agents", tags=["Agents"])

app.include_router(route_websocket.router, prefix="/api/ws", tags=["WebSocket"])

app.include_router(route_process.router, prefix="/api/process", tags=["processing"])

# Health check
@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "active_cameras": len(camera_manager.active_cameras),
        "active_agents" : len(agent_orchestrator.agents),
        "streams": len(stream_manager.active_streams),
        "queue_size": agent_orchestrator.processing_queue.qsize()
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )