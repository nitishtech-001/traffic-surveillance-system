# backend/app/services/agent_orchestrator.py
import asyncio
import logging
from typing import Dict, List, Optional, Any, Type
from datetime import datetime
import numpy as np

from app.schema.schema_agent import AgentTypeSchema, AgentStatusSchema
from app.agents.agent_base import BaseAgent
from app.agents.agent_object_detection import ObjectDetectionAgent
from app.agents.agent_license_plate import LicensePlateAgent

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """
    Orchestrates multiple AI agents for video frame processing
    """
    
    agents: Dict[str, BaseAgent] = {}

    def __init__(self):
        self.agent_metadata: Dict[str, Dict[str, Any]] = {}
        self.processing_queue: asyncio.Queue = asyncio.Queue()
        self.is_running: bool = False
        self.worker_task: Optional[asyncio.Task] = None
        
        # AgentSchema registry - maps agent types to their classes
        self.agent_registry = {
            AgentTypeSchema.OBJECT_DETECTION: ObjectDetectionAgent,
            AgentTypeSchema.LICENSE_PLATE: LicensePlateAgent,
            # Add more agents here as you create them
            # AgentTypeSchema.FACE_DETECTION: FaceDetectionAgent,
            # AgentTypeSchema.MOTION_TRACKING: MotionTrackingAgent,
        }
        
        # Active agent configurations
        self.active_agents: List[str] = []
        
        # Results storage
        self.processing_results: Dict[str, List[Dict]] = {}
        self.last_results: Dict[str, Dict] = {}
        
    async def initialize(self):
        """
        Initialize the orchestrator
        """
        logger.info("Initializing Agent Orchestrator")
        self.is_running = True
        
        # Start the processing worker
        self.worker_task = asyncio.create_task(self._processing_worker())
        
        logger.info("Agent Orchestrator initialized successfully")
        
    async def add_agent(self, agent_type: AgentTypeSchema, config: Dict[str, Any] = None) -> bool:
        """
        Add and initialize a new agent
        """
        try:
            agent_class = self.agent_registry.get(agent_type)
            if not agent_class:
                logger.error(f"Agent type {agent_type} not registered")
                return False
            
            # Create agent instance
            agent_id = agent_type.value
            agent = agent_class(agent_id=agent_id, config=config or {})
            
            # Initialize agent
            success = await agent.initialize()
            if not success:
                logger.error(f"Failed to initialize agent {agent_type}")
                return False
            
            # Store agent
            self.agents[agent_id] = agent
            self.agent_metadata[agent_id] = {
                "type": agent_type,
                "name": agent.name,
                "added_at": datetime.now(),
                "status": AgentStatusSchema.READY,
                "config": config or {}
            }
            
            logger.info(f"Agent {agent_type} added and initialized")
            return True
            
        except Exception as e:
            logger.error(f"Error adding agent {agent_type}: {str(e)}")
            return False
    
    async def activate_agent(self, agent_id: str) -> bool:
        """
        Activate an agent for processing
        """
        if agent_id not in self.agents:
            logger.error(f"Agent {agent_id} not found")
            return False
        
        if agent_id not in self.active_agents:
            self.active_agents.append(agent_id)
            self.agent_metadata[agent_id]["status"] = AgentTypeSchema.READY
            logger.info(f"Agent {agent_id} activated")
            return True
        
        return False
    
    async def deactivate_agent(self, agent_id: str) -> bool:
        """
        Deactivate an agent from processing
        """
        if agent_id in self.active_agents:
            self.active_agents.remove(agent_id)
            self.agent_metadata[agent_id]["status"] = AgentTypeSchema.IDLE
            logger.info(f"Agent {agent_id} deactivated")
            return True
        
        return False
    
    async def process_frame(self, frame: np.ndarray, camera_id: str) -> Dict[str, Any]:
        """
        Process a single frame through all active agents
        """
        if not self.active_agents:
            return {
                "camera_id": camera_id,
                "success": True,
                "results": {},
                "message": "No active agents"
            }
        
        start_time = datetime.now()
        results = {}
        processing_times = {}
        
        # Process frame through each active agent
        for agent_id in self.active_agents:
            agent = self.agents.get(agent_id)
            if not agent:
                continue
            
            try:
                # Update status
                self.agent_metadata[agent_id]["status"] = AgentTypeSchema.PROCESSING
                
                # Process frame
                agent_start = datetime.now()
                result = await agent.process_with_metrics(frame)
                agent_time = (datetime.now() - agent_start).total_seconds()
                
                # Store result
                results[agent_id] = result
                processing_times[agent_id] = agent_time
                
                # Update status
                self.agent_metadata[agent_id]["status"] = AgentTypeSchema.READY
                
            except Exception as e:
                logger.error(f"Agent {agent_id} processing error: {str(e)}")
                results[agent_id] = {"success": False, "error": str(e)}
                self.agent_metadata[agent_id]["status"] = AgentTypeSchema.ERROR
        
        total_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "camera_id": camera_id,
            "timestamp": datetime.now().isoformat(),
            "success": True,
            "results": results,
            "processing_times": processing_times,
            "total_processing_time": total_time,
            "active_agents": self.active_agents.copy()
        }
    
    async def process_frame_async(self, frame: np.ndarray, camera_id: str) -> asyncio.Task:
        """
        Process frame asynchronously (non-blocking)
        """
        return asyncio.create_task(self.process_frame(frame, camera_id))
    
    async def queue_frame(self, frame: np.ndarray, camera_id: str, callback: callable = None):
        """
        Queue a frame for processing by the worker
        """
        await self.processing_queue.put({
            "frame": frame,
            "camera_id": camera_id,
            "callback": callback,
            "timestamp": datetime.now()
        })
    
    async def _processing_worker(self):
        """
        Background worker that processes queued frames
        """
        logger.info("Processing worker started")
        
        while self.is_running:
            try:
                # Get next item from queue
                item = await self.processing_queue.get()
                
                frame = item["frame"]
                camera_id = item["camera_id"]
                callback = item["callback"]
                
                # Process frame
                result = await self.process_frame(frame, camera_id)
                
                # Store results
                timestamp = datetime.now().isoformat()
                if camera_id not in self.processing_results:
                    self.processing_results[camera_id] = []
                
                # Keep only last 100 results
                self.processing_results[camera_id].append({
                    "timestamp": timestamp,
                    "result": result
                })
                
                if len(self.processing_results[camera_id]) > 100:
                    self.processing_results[camera_id].pop(0)
                
                # Update last results
                self.last_results[camera_id] = result
                
                # Call callback if provided
                if callback:
                    try:
                        await callback(result)
                    except Exception as e:
                        logger.error(f"Callback error: {str(e)}")
                
                # Mark as done
                self.processing_queue.task_done()
                
            except asyncio.CancelledError:
                logger.info("Processing worker cancelled")
                break
                
            except Exception as e:
                logger.error(f"Processing worker error: {str(e)}")
                await asyncio.sleep(0.1)
        
        logger.info("Processing worker stopped")
    
    async def get_results(self, camera_id: str, limit: int = 10) -> List[Dict]:
        """
        Get processing results for a camera
        """
        results = self.processing_results.get(camera_id, [])
        return results[-limit:] if results else []
    
    async def get_last_result(self, camera_id: str) -> Optional[Dict]:
        """
        Get the last processing result for a camera
        """
        return self.last_results.get(camera_id)
    
    async def get_agent_status(self) -> List[Dict[str, Any]]:
        """
        Get status of all agents
        """
        status = []
        for agent_id, metadata in self.agent_metadata.items():
            agent = self.agents.get(agent_id)
            
            status.append({
                "agent_id": agent_id,
                "name": metadata["name"],
                "type": metadata["type"].value,
                "status": metadata["status"],
                "active": agent_id in self.active_agents,
                "performance": agent.get_performance() if agent else {},
                "config": metadata["config"]
            })
        
        return status
    
    async def get_agent_performance(self, agent_id: str) -> Optional[Dict]:
        """
        Get performance metrics for a specific agent
        """
        agent = self.agents.get(agent_id)
        if agent:
            return agent.get_performance()
        return None
    
    async def cleanup_all(self):
        """
        Cleanup all agents and stop worker
        """
        logger.info("Cleaning up all agents")
        
        # Stop worker
        self.is_running = False
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
        
        # Cleanup each agent
        for agent_id, agent in self.agents.items():
            try:
                await agent.cleanup()
                logger.info(f"Agent {agent_id} cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up agent {agent_id}: {str(e)}")
        
        self.agents.clear()
        self.active_agents.clear()
        self.processing_results.clear()
        self.last_results.clear()
        
        logger.info("All agents cleaned up")
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """
        Get system statistics
        """
        return {
            "total_agents": len(self.agents),
            "active_agents": len(self.active_agents),
            "queue_size": self.processing_queue.qsize(),
            "is_running": self.is_running,
            "agent_status": await self.get_agent_status(),
            "cameras_with_results": list(self.last_results.keys())
        }
