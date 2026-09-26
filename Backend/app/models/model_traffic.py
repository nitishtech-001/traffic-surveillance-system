# app/services/model.py
import numpy as np
from ultralytics import YOLO
import logging
# importing all agents
from app.agents.object_detection import ObjectDetection
from app.agents.agent_license_plate import LicensePlateAgent
from app.agents.agent_object_detection import ObjectDetectionAgent

logger = logging.getLogger(__name__)

class TrafficModel:
    """
    Loads the 10-class YOLO model once and runs inference on BGR frames.
    Returns an annotated BGR frame of the same shape.
    """
    
    agents = {
        "object-detection" : {"class":ObjectDetection ,"camera_id": [], "count": 0, "conf": 0.5, "device": "cuda" },
        "licence-plate" : {"class":LicensePlateAgent,"camera_id": [], "count": 0, "conf": 0.5, "device": "cuda" },
    }
    active_agents = {}

    @classmethod
    def initalize(cls, agent_name: str,camera_id:str,device: str = "cuda"):
        if agent_name in cls.agents:
            cls.active_agents[agent_name] = cls.agents[agent_name]['class']()
            cls.agents[agent_name]["camera_id"].append(camera_id)
            

    @classmethod
    def predict(cls,agent_name: str,bgr_frame: np.ndarray,conf:float = 0.35) -> np.ndarray:
        if agent_name == "object-detection":
           return cls.predict_object(bgr_frame,conf)
        
        elif cls.agent_name == "face-detection":
            return cls.predict_face(bgr_frame)
        
        elif cls.agent_name == "licenseplate-detection":
           return cls.predict_licenseplate(bgr_frame)
        
        elif cls.agent_name == "motion-detection":
            return cls.predict_motion(bgr_frame)
        
        elif cls.agent_name == "text-detection":
            return cls.predict_text(bgr_frame)
        else:
            return bgr_frame

    def predict_object(cls, bgr_frame: np.ndarray,conf) -> np.ndarray:
        """
        Run detection + plot the boxes on the frame.
        Ultralytics .plot() returns a BGR numpy array when the input is BGR.
        """
        
    
    def predict_face(self, bgr_frame: np.ndarray) -> np.ndarray:
        """
        Run detection + plot the boxes on the frame.
        Face detection of the persons
        """
        pass
    
    def predict_licenseplate(self, bgr_frame: np.ndarray) -> np.ndarray:
        """
        Run detection + plot the boxes on the frame.
        Licenseplate detection of the vechicle
        """
        pass

    def predict_motion(self, bgr_frame: np.ndarray) -> np.ndarray:
        """
        Run detection + plot the boxes on the frame.
        Motion and speed prediction of the vechicle
        """
        pass
    
    def predict_text(self, bgr_frame: np.ndarray) -> np.ndarray:
        """
        Run detection + plot the boxes on the frame.
        set up for text recognition
        """
        pass