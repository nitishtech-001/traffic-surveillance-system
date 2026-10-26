from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import uvicorn
import logging
from contextlib import asynccontextmanager

# Routes
from app.api.routes import route_agents, route_camera, route_stream, route_websocket

# Configuration
from app.core.config import settings


# Services
from app.services.stream_manager import StreamManager
from app.services.agent_orchestrator import AgentOrchestrator
from app.services.camera_manager import CameraManager


# Setup logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
# TODO : removing the logs of aiortc for better debuging
logging.getLogger("aioice").setLevel(logging.WARNING)
logging.getLogger("aiortc").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.CRITICAL)
logging.getLogger("matplotlib").setLevel(logging.WARNING)
logging.getLogger("matplotlib.font_manager").setLevel(logging.WARNING)
logging.getLogger("watchfiles.main").setLevel(logging.WARNING)
# Initialize global services
camera_manager = CameraManager()
stream_manager = StreamManager()
agent_orchestrator = AgentOrchestrator()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager for startup and shutdown events"""
    # Startup
    camera_manager.initialize()
    stream_manager.initialize()
    logger.info("Starting Traffic Analysis System...")
    await agent_orchestrator.initialize()

    logger.info(f"Number of Register Agents are ::::  {len(agent_orchestrator.agent_registry)} .")

    yield
    

    # Shutdown
    logger.info("Shutting down...")
    await camera_manager.disconnect_all()
    await stream_manager.stop_all_streams()
    await agent_orchestrator.cleanup_all()

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

# app.include_router(route_auth.router, prefix="/api/auth", tags=["Register"]) NOT USED BECAUSE RUNNING LOCALY

app.include_router(route_agents.router, prefix="/api/agents", tags=["Agents"])

app.include_router(route_websocket.router, prefix="/api/ws", tags=["WebSocket"])


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
        reload=settings.DEBUG,
        reload_excludes=["uploads/*", "uploads/**/*"]
    )