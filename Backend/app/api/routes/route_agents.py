# backend/app/api/routes/agents.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import logging

from app.services.agent_orchestrator import AgentOrchestrator
from app.schema.schema_agent import AgentTypeSchema
from app.api.dependencies.authenticate import get_current_user


logger = logging.getLogger(__name__)

router = APIRouter()
agent_orchestrator = AgentOrchestrator()

# TODO: If you want to add the authentication then uncomment
# authenticate_user = Depends(get_current_user)
authenticate_user = {}

@router.get("/list", response_model=List[Dict[str, Any]])
async def list_agents(current_user: Dict = authenticate_user ):
    """List all agents with their status"""
    try:
        status = await agent_orchestrator.get_agent_status()
        return status
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{agent_id}/activate")
async def activate_agent(
    agent_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Activate an agent"""
    try:
        success = await agent_orchestrator.activate_agent(agent_id)
        if not success:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return {
            "message": f"Agent {agent_id} activated successfully",
            "agent_id": agent_id
        }
    except Exception as e:
        logger.error(f"Error activating agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{agent_id}/deactivate")
async def deactivate_agent(
    agent_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Deactivate an agent"""
    try:
        success = await agent_orchestrator.deactivate_agent(agent_id)
        if not success:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return {
            "message": f"Agent {agent_id} deactivated successfully",
            "agent_id": agent_id
        }
    except Exception as e:
        logger.error(f"Error deactivating agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add/{agent_type}")
async def add_agent(
    agent_type: str,
    config: Dict[str, Any] = None,
    current_user: Dict = Depends(get_current_user)
):
    """Add a new agent to the system"""
    try:
        # Validate agent type
        try:
            agent_type_enum = AgentTypeSchema(agent_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid agent type: {agent_type}")
        
        success = await agent_orchestrator.add_agent(agent_type_enum, config)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to add agent")
        
        return {
            "message": f"Agent {agent_type} added successfully",
            "agent_id": agent_type
        }
    except Exception as e:
        logger.error(f"Error adding agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{agent_id}/performance")
async def get_agent_performance(
    agent_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get performance metrics for an agent"""
    try:
        performance = await agent_orchestrator.get_agent_performance(agent_id)
        if not performance:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return performance
    except Exception as e:
        logger.error(f"Error getting agent performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_orchestrator_stats(current_user: Dict = Depends(get_current_user)):
    """Get orchestrator statistics"""
    try:
        stats = await agent_orchestrator.get_system_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting orchestrator stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))