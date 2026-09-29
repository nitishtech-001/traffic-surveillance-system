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
        if not self.is_initialized:
            raise RuntimeError("Agent not initialized")
        
        # Get confidence threshold from config or use default
        confidence_threshold = conf
        
        # Run inference
        results = self.model(frame, conf=confidence_threshold, verbose=False)
        
        detections = []
        total_objects = 0
        objects_counts = {}     
        annotated_frame = frame   
        if results and len(results) > 0:
            result = results[0]

            # Extract bounding boxes, classes, and confidences
            if result.boxes is not None:
                boxes = result.boxes.xyxy.cpu().numpy()
                confidences = result.boxes.conf.cpu().numpy()
                class_ids = result.boxes.cls.cpu().numpy()
                
                for box, conf, class_id in zip(boxes, confidences, class_ids):
                    x1, y1, x2, y2 = box
                    class_name = self.class_names.get(int(class_id), "unknown")
                    
                    detection = ObjectDetectionSchema(
                        class_name=class_name,
                        class_id=int(class_id),
                        bbox=BoundingBoxSchema(
                            x1=float(x1),
                            y1=float(y1),
                            x2=float(x2),
                            y2=float(y2),
                            confidence=float(conf)
                        ),
                        confidence=float(conf)
                    )
                    detections.append(detection)
                    total_objects += 1
                    objects_counts[class_name] = objects_counts.get(class_name,0)+1
                


            annotated_frame = self.draw_detections(frame,detections)
            # annotated_frame = results[0].plot()

        return {
            "total_objects": total_objects,
            "object_counts": objects_counts,
            "annotated_frame": annotated_frame,
            "frame_info": {
                "width": frame.shape[1],
                "height": frame.shape[0],
            },
        }
    
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
            Draw bounding boxes and filled text labels on the frame with distinct colors per class.
            Matches the style of results[0].plot()
        """
        frame_copy = frame.copy()
        
        for detection in detections:
            bbox = detection.bbox
            x1, y1, x2, y2 = int(bbox.x1), int(bbox.y1), int(bbox.x2), int(bbox.y2)
            
            # 1. Generate a unique, deterministic color based on the class name string
            # This guarantees 'person' is always one color, 'car' is another, etc.
            class_name = detection.class_name
            hash_val = hash(class_name)
            color = (
                (hash_val & 0xFF), 
                ((hash_val >> 8) & 0xFF), 
                ((hash_val >> 16) & 0xFF)
            )
            
            # 2. Draw the main bounding box line
            cv2.rectangle(frame_copy, (x1, y1), (x2, y2), color, 2)
            
            # 3. Create a clean, modern label text string
            label = f"{class_name} {detection.confidence:.2f}"
            
            # Get width and height of text box to size the background rectangle perfectly
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.8
            font_thickness = 2
            (text_width, text_height), baseline = cv2.getTextSize(
                label, font, font_scale, font_thickness
            )
            
            # Determine top-left and bottom-right of the text background rectangle
            # Fallback to drawing inside the bounding box if the box touches the top edge of the screen
            text_y1 = max(y1 - text_height - baseline - 5, 0)
            text_y2 = text_y1 + text_height + baseline + 5
            text_x2 = x1 + text_width + 10
            
            # 4. Draw the filled background rectangle for the text label
            cv2.rectangle(frame_copy, (x1, text_y1), (text_x2, text_y2), color, cv2.FILLED)
            
            # 5. Draw contrast-enhancing white text over the solid colored background box
            text_position = (x1 + 5, text_y2 - baseline - 2)
            cv2.putText(
                frame_copy, 
                label, 
                text_position, 
                font, 
                font_scale, 
                (255, 255, 255),  # Pure white text for readability
                font_thickness, 
                lineType=cv2.LINE_AA
            )
        
        return frame_copy