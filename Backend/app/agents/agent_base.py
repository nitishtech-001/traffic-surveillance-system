# backend/app/agents/base_agent.py
from abc import ABC, abstractmethod
from typing import  Dict, Any
import numpy as np
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Abstract base class for all AI agents
    """
    
    def __init__(self, agent_id: str, name: str, config: Dict[str, Any] = None):
        self.id = agent_id
        self.name = name
        self.config = config or {}
        self.is_initialized = False
        self.model = None
        self.performance_metrics = {
            "total_processed": 0,
            "avg_processing_time": 0,
            "total_processing_time": 0,
            "last_processing_time": 0
        }
        
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the agent and load models"""
        pass
    
    @abstractmethod
    def process(self, frame: np.ndarray,conf) -> Dict[str, Any]:
        """Process a single frame and return results"""
        pass
    
    @abstractmethod
    def cleanup(self) -> bool:
        """Cleanup resources"""
        pass
    
    def process_with_metrics(self, frame: np.ndarray, conf) -> Dict[str, Any]:
        """
        Process frame with performance tracking
        """
        start_time = datetime.now()
        
        try:
            result = self.process(frame,conf)
            
            # Update metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            self.performance_metrics["total_processed"] += 1
            self.performance_metrics["last_processing_time"] = processing_time
            self.performance_metrics["total_processing_time"] += processing_time
            self.performance_metrics["avg_processing_time"] = (
                self.performance_metrics["total_processing_time"] / 
                self.performance_metrics["total_processed"]
            )
            
            # return {
            #     "success": True,
            #     "data": result,
            #     "processing_time": processing_time,
            #     "agent_id": self.id,
            #     "agent_name": self.name
            # }
            return result
            
        except Exception as e:
            logger.error(f"Agent {self.id} processing error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.id,
                "agent_name": self.name
            }
    
    def get_performance(self) -> Dict[str, Any]:
        """Get agent performance metrics"""
        return {
            "agent_id": self.id,
            "agent_name": self.name,
            **self.performance_metrics
        }