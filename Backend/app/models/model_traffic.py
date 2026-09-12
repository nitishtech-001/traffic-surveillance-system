# app/services/model.py
import numpy as np
from ultralytics import YOLO
import logging
import os

logger = logging.getLogger(__name__)

class TrafficModel:
    """
    Loads the 10-class YOLO model once and runs inference on BGR frames.
    Returns an annotated BGR frame of the same shape.
    """

    def __init__(self, model_name: str, conf: float = 0.35,
                 device: str = "cuda"):

        model_path = os.getcwd()+f"/ai_models/{model_name}"
        if os.path.exists(model_path):
            logger.info(f"Model path is valid {model_path}")
            try:
                self.model = YOLO(model_path)
                self.model.to(device)
                self.conf = conf        
                self.device = device
                logger.info(f"Model initalized... {model_path}")
            except Exception as e:
                print("Model Initalization Error ", e)
        else:
            logger.info(f"Model path is invalid {model_path}")
        

    def infer(self, bgr_frame: np.ndarray) -> np.ndarray:
        """
        Run detection + plot the boxes on the frame.
        Ultralytics .plot() returns a BGR numpy array when the input is BGR.
        """
        results = self.model.predict(
            source=bgr_frame,
            conf=self.conf,
            device=self.device,
            verbose=False,
        )
        # results[0].plot() draws boxes and returns the same shape
        annotated = results[0].plot()
        return annotated