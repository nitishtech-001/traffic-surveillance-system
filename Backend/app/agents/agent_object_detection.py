# backend/app/agents/object_detection.py
import cv2
import numpy as np
from typing import Dict, Any, List
import torch
from pathlib import Path
import logging
from app.agents.agent_base import BaseAgent
from app.schema.schema_detection import ObjectDetectionSchema, BoundingBoxSchema
from app.core.config import settings
import os

logger = logging.getLogger(__name__)

class ObjectDetectionAgent(BaseAgent):
    """
    YOLO-based object detection agent
    """
    
    def __init__(self, agent_id: str = "object-detection", config: Dict[str, Any] = None):
        super().__init__(
            agent_id=agent_id,
            name="Object Detection Agent",
            config=config or {}
        )
        self.model = None
        self.class_names = []
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    async def initialize(self) -> bool:
        """
        Initialize YOLO model
        """
        try:
            logger.info(f"Initializing Object Detection Agent on {self.device}")
            
            # Load YOLO model - using ultralytics
            from ultralytics import YOLO
            
            model_path = Path(settings.AGENT_MODEL_PATH)/ Path(settings.AGENT_MODEL_OBJECT_DETECTION)
            print("CURRENT WORKING DIRECTORY ::: ",os.getcwd())
            print("MODEL PATH IS :::: ",model_path)
            if not model_path.exists():
                logger.info(f"Downloading YOLO model from {model_path}")
                # self.model = YOLO('yolov8n.pt')  # Downloads if not exists
            else:
                self.model = YOLO(str(model_path))
            
            # Move to device
            self.model.to(self.device)
            
            # Get class names
            self.class_names = self.model.names
            
            self.is_initialized = True
            logger.info(f"Object Detection Agent initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Object Detection Agent: {str(e)}")
            return False
    
    def process(self, frame: np.ndarray,conf:float) -> Dict[str, Any]:
        """
        Process frame and detect objects
        """
        # if not self.is_initialized:
        #     raise RuntimeError("Agent not initialized")
        
        # # Get confidence threshold from config or use default
        # confidence_threshold = conf
        
        # # Run inference
        # results = self.model(frame, conf=confidence_threshold, verbose=False)
        
        # detections = []
        # total_objects = 0
        # class_counts = {}        
        # if results and len(results) > 0:
        #     result = results[0]

        #     # Extract bounding boxes, classes, and confidences
        #     if result.boxes is not None:
        #         boxes = result.boxes.xyxy.cpu().numpy()
        #         confidences = result.boxes.conf.cpu().numpy()
        #         class_ids = result.boxes.cls.cpu().numpy()
                
        #         for box, conf, class_id in zip(boxes, confidences, class_ids):
        #             x1, y1, x2, y2 = box
        #             class_name = self.class_names.get(int(class_id), "unknown")
                    
        #             detection = ObjectDetectionSchema(
        #                 class_name=class_name,
        #                 class_id=int(class_id),
        #                 bbox=BoundingBoxSchema(
        #                     x1=float(x1),
        #                     y1=float(y1),
        #                     x2=float(x2),
        #                     y2=float(y2),
        #                     confidence=float(conf)
        #                 ),
        #                 confidence=float(conf)
        #             )
        #             detections.append(detection)
        #             total_objects += 1
        #             class_counts[class_id] = class_counts.get(class_id,0)+1


        # annotated_frame = self.draw_detections(frame,detections)

        # return {
        #     "total_objects": total_objects,
        #     "class_counts": class_counts,
        #     "annotated_frame": annotated_frame,
        #     "frame_info": {
        #         "width": frame.shape[1],
        #         "height": frame.shape[0],
        #     }
        # }
        if self.is_initialized:
            results = self.model.predict(
                        source=frame,
                        conf=conf,
                        device=self.device,
                        verbose=False,
                    )
            annotatd_frame = results[0].plot()
        else:
            print("Model is not initailize check it again")
            annotatd_frame = frame
        return annotatd_frame
    
    async def cleanup(self) -> bool:
        """
        Cleanup resources
        """
        try:
            if self.model:
                del self.model
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            self.is_initialized = False
            return True
        except Exception as e:
            logger.error(f"Cleanup error: {str(e)}")
            return False
    
    def draw_detections(self, frame: np.ndarray, detections: List[ObjectDetectionSchema]) -> np.ndarray:
        """
        Draw bounding boxes and labels on frame
        """
        frame_copy = frame.copy()
        
        for detection in detections:
            bbox = detection.bbox
            x1, y1, x2, y2 = int(bbox.x1), int(bbox.y1), int(bbox.x2), int(bbox.y2)
            
            # Draw rectangle
            cv2.rectangle(frame_copy, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw label
            label = f"{detection.class_name} {detection.confidence:.2f}"
            cv2.putText(frame_copy, label, (x1, y1 - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return frame_copy