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

    agent_metadata: Dict[str, Dict[str, Any]] = {}
    
    # AgentSchema registry - maps agent types to their classes
    agent_registry = {
        AgentTypeSchema.OBJECT_DETECTION: ObjectDetectionAgent,
        AgentTypeSchema.LICENSE_PLATE: LicensePlateAgent,
        # Add more agents here as you create them
        # AgentTypeSchema.FACE_DETECTION: FaceDetectionAgent,
        # AgentTypeSchema.MOTION_TRACKING: MotionTrackingAgent,
    }
    
    # Active agent configurations
    active_agents: List[str] = []
    
    # Results storage
    processing_results: Dict[str, List[Dict]] = {}
    last_results: Dict[str, Dict] = {}


    @classmethod
    async def initialize(cls):
        # initializing all availbale agents
        try:
            for agent_type, agent_class in cls.agent_registry.items():
                await cls.add_agent(agent_type=agent_type, agent_class=agent_class)
        except Exception as e:
            logger.error(f"Error during the model initializaton ::: {e}")


    @classmethod
    # async def add_agent(cls, agent_type: AgentTypeSchema, config: Dict[str, Any] = None) -> bool:
    async def add_agent(cls,agent_type: AgentTypeSchema, agent_class,config:Dict[str,Any]=None)->bool:
        """
        Add and initialize a new agent
        """
        try:
            # agent_class = cls.agent_registry.get(agent_type)
            # if not agent_class:
            #     logger.error(f"Agent type {agent_type} not registered")
            #     return False
            
            # Create agent instance
            agent_id = agent_type.value
            agent = agent_class(agent_id=agent_id, config=config or {})
            
            # Initialize agent
            success = await agent.initialize()
            if not success:
                logger.error(f"Failed to initialize agent {agent_type}")
                return False
            
            # Store agent
            cls.agents[agent_id] = agent
            cls.agent_metadata[agent_id] = {
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
        
    @classmethod
    async def activate_agent(cls, agent_id: str) -> bool:
        """
        Activate an agent for processing
        """
        print(cls.agents, agent_id)
        if agent_id not in cls.agents:
            logger.error(f"Agent {agent_id} not found")
            return False
        
        if agent_id not in cls.active_agents:
            cls.active_agents.append(agent_id)
            cls.agent_metadata[agent_id]["status"] = AgentStatusSchema.READY
            
            logger.info(f"Agent {agent_id} activated")
            return True
        
        return False

    @classmethod
    async def deactivate_agent(cls, agent_id: str) -> bool:
        """
        Deactivate an agent from processing
        """
        if agent_id in cls.active_agents:
            cls.active_agents.remove(agent_id)
            cls.agent_metadata[agent_id]["status"] = AgentStatusSchema.IDLE
            logger.info(f"Agent {agent_id} deactivated")
            return True
        
        return False

    @classmethod
    async def process_frame(cls,frame: np.ndarray, conf: float=0.5) -> Dict[str, Any]:
        """
        Process a single frame through all active agents
        """
        if not cls.active_agents:
            return None
        start_time = datetime.now()
        agent_ids = []
        tasks = []
        annotated_frame = None
        # Process frame through each active agent
        for agent_id in cls.active_agents:
            agent = cls.agents.get(agent_id)
            if not agent:
                continue
            
            try:
                # Update status
                cls.agent_metadata[agent_id]["status"] = AgentStatusSchema.PROCESSING
                
                task = asyncio.to_thread(agent.process_with_metrics,frame,conf)
                tasks.append(task)
                agent_ids.append(agent_id)
                # Update status
                cls.agent_metadata[agent_id]["status"] = AgentStatusSchema.READY
                
            except Exception as e:
                logger.error(f"Agent {agent_id} processing error: {str(e)}")
                cls.agent_metadata[agent_id]["status"] = AgentStatusSchema.ERROR

        results = {}
        raw_results = await asyncio.gather(*tasks)

        for agent_id, agent_result in zip(agent_ids, raw_results):
            try:
                if agent_id == "object-detection" and isinstance(agent_result,Dict) and "result" in agent_result :
                    result_data = agent_result["result"]
                    if isinstance(result_data, Dict) and "annotated_frame" in result_data:
                        annotated_frame = result_data.pop("annotated_frame",None)
                results[agent_id] = agent_result
            except Exception as e:
                logger.error(f"Error structuring result of {agent_id} ::: {e}")
                cls.agent_metadata[agent_id]["status"] = AgentOrchestrator.ERROR

        total_time = (datetime.now() - start_time).total_seconds()


        # response should be like {information_data, agent_name: there_result}
        # add some extra informaion about the annotated frame
        reponse = {}
        reponse["success"] = True
        reponse["timestamp"] = datetime.now().isoformat()
        reponse["total_processing_time"] = total_time
        reponse["active_agnets"] = cls.active_agents.copy()
        reponse["agent_results"] = results

        if "object-detection" not in agent_ids or annotated_frame is None:
            annotated_frame = frame
        
        cls.last_results = reponse

        return {
            "data": reponse,
            "annotated_frame": annotated_frame,
        }

    @classmethod
    def get_results(cls, camera_id: str, limit: int = 10) -> List[Dict]:
        """
        Get processing results for a camera
        """
        results = cls.processing_results.get(camera_id, [])
        return results[-limit:] if results else []

    @classmethod
    def get_last_result(cls, camera_id: str) -> Optional[Dict]:
        """
        Get the last processing result for a camera
        """
        return cls.last_results.get(camera_id)

    @classmethod
    def get_agent_status(cls) -> List[Dict[str, Any]]:
        """
        Get status of all agents
        """
        status = []
        for agent_id, metadata in cls.agent_metadata.items():
            agent = cls.agents.get(agent_id)
            
            status.append({
                "agent_id": agent_id,
                "name": metadata["name"],
                "type": metadata["type"].value,
                "status": metadata["status"],
                "active": agent_id in cls.active_agents,
                "performance": agent.get_performance() if agent else {},
                "config": metadata["config"]
            })
        
        return status

    @classmethod
    def get_agent_performance(cls, agent_id: str) -> Optional[Dict]:
        """
        Get performance metrics for a specific agent
        """
        agent = cls.agents.get(agent_id)
        if agent:
            return agent.get_performance()
        return None

    @classmethod
    async def cleanup_all(cls):
        """
        Cleanup all agents and stop worker
        """
        logger.info("Cleaning up all agents")
        
        # Cleanup each agent
        for agent_id, agent in cls.agents.items():
            try:
                agent.cleanup()
                logger.info(f"Agent {agent_id} cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up agent {agent_id}: {str(e)}")
        
        cls.agents.clear()
        cls.active_agents.clear()
        cls.processing_results.clear()
        cls.last_results.clear()
        
        logger.info("All agents cleaned up")

    @classmethod
    async def get_system_stats(cls) -> Dict[str, Any]:
        """
        Get system statistics
        """
        return {
            "total_agents": len(cls.agents),
            "active_agents": len(cls.active_agents),
            "queue_size": cls.processing_queue.qsize(),
            "agent_status": await cls.get_agent_status(),
            "cameras_with_results": list(cls.last_results.keys())
        }
