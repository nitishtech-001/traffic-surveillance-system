# app/services/model.py
import numpy as np
from ultralytics import YOLO
import logging
import os
import torch

logger = logging.getLogger(__name__)

class TrafficModel:
    """
    Loads the 10-class YOLO model once and runs inference on BGR frames.
    Returns an annotated BGR frame of the same shape.
    """

    def __init__(self, agent_file_name: str,agent_name: str, conf: float = 0.35,
                 device: str = "cuda"):

        if torch.cuda.is_available():
            print("MODEL IS RUNNING ON THE GPU FEEL FREE")
        else:
            print("MODEL IS RUNNING ON CPU MINIMIZE THE LOAD")

        agent_path = os.getcwd()+f"/ai_models/{agent_file_name}"
        if os.path.exists(agent_path):
            logger.info(f"Agent path is valid {agent_path}")
            try:
                self.agent = YOLO(agent_path,task='detect')
                self.agent.to(device)
                self.conf = conf        
                self.device = device
                self.agent_name = agent_name
                logger.info(f"Agent initalized... {agent_path}")
            except Exception as e:
                print("Agent Initalization Error ", e)
        else:
            logger.info(f"Agent path is invalid {agent_path}")
        
    def predict(self,bgr_frame: np.ndarray) -> np.ndarray:
        if self.agent_name == "object-detection":
           return self.predict_object(bgr_frame)
        
        elif self.agent_name == "face-detection":
            return self.predict_face(bgr_frame)
        
        elif self.agent_name == "licenseplate-detection":
           return self.predict_licenseplate(bgr_frame)
        
        elif self.agent_name == "motion-detection":
            return self.predict_motion(bgr_frame)
        
        elif self.agent_name == "text-detection":
            return self.predict_text(bgr_frame)

    def predict_object(self, bgr_frame: np.ndarray) -> np.ndarray:
        """
        Run detection + plot the boxes on the frame.
        Ultralytics .plot() returns a BGR numpy array when the input is BGR.
        """
        results = self.agent.predict(
            source=bgr_frame,
            conf=self.conf,
            device=self.device,
            verbose=False,
        )
        # results[0].plot() draws boxes and returns the same shape
        annotated = results[0].plot()
        return annotated
    
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