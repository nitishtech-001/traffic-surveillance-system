from ultralytics import YOLO
import torch
import os
import logging
import numpy as np

logger = logging.getLogger(__name__)

class ObjectDetection:
    def __init__(self, device: str="cuda"):
        agent_model_name = "object_detection.pt"
        if torch.cuda.is_available():
            print("MODEL IS RUNNING ON THE GPU FEEL FREE")
        else:
            print("MODEL IS RUNNING ON CPU MINIMIZE THE LOAD")

        agent_model_path = os.getcwd()+f"/ai_models/{agent_model_name}"
        if os.path.exists(agent_model_path):
            logger.info(f"Agent path is valid {agent_model_path}")
            try:
                self.agent = YOLO(agent_model_path,task='detect')
                self.agent.to(device)      
                self.device = device
                logger.info(f"Agent initalized... {agent_model_path}")
            except Exception as e:
                print("Agent Initalization Error ", e)

    def predict(self, bgr_frame:np.ndarray,conf):
        results = self.agent.predict(
            source=bgr_frame,
            conf=conf,
            device=self.device,
            verbose=False,
        )
        # results[0].plot() draws boxes and returns the same shape
        annotated = results[0].plot()
        return annotated