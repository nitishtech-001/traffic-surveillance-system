# backend/app/agents/license_plate.py
import cv2
import numpy as np
from typing import Dict, Any, List, Optional
import easyocr
import re
import logging
import os

from app.core.config import settings
from app.agents.agent_base import BaseAgent

logger = logging.getLogger(__name__)

class LicensePlateAgent(BaseAgent):
    """
    License plate detection and recognition agent
    """
    
    def __init__(self, agent_id: str = "license-plate", config: Dict[str, Any] = None):
        super().__init__(
            agent_id=agent_id,
            name="License Plate Recognition",
            config=config or {}
        )
        self.reader = None
        self.detection_model = None
        self._normalize = lambda s: re.sub(r'[^A-Z0-9]', '', s.upper())
        
    async def initialize(self) -> bool:
        """
        Initialize OCR and detection models
        """
        try:
            logger.info("Initializing License Plate Detection Agent")
            
            # Initialize EasyOCR reader
            languages = self.config.get("languages", ['en'])
            self.reader = easyocr.Reader(languages, gpu=True)
            
            # Load plate detection model if needed
            model_path = settings.AGENT_MODEL_PATH+"/"+settings.AGENT_LICENSE_PLATE
            if os.path.exists(model_path):
                from ultralytics import YOLO

                self.detection_model = YOLO(model_path)
            else:
                raise FileNotFoundError(f"YOLO model for license plate missing ::: {model_path}")
            
            self.is_initialized = True
            logger.info("License Plate Agent initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize License Plate Agent: {str(e)}")
            return False
    
    def process(self, frame: np.ndarray, conf) -> Dict[str, Any]:
        """
        Detect and read license plates from frame
        """
        if not self.is_initialized:
            raise RuntimeError("Agent not initialized")
        
        # Detect potential plate regions
        results = self.detection_model.predict(frame,conf,verbose=False)
        
        plates = []
        try:
            for result in results:
                # Crop plate region
                boxes = result.boxes

                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy.cpu().numpy().astype(int).tolist()[0]

                    x1_pad, y1_pad = max(0, x1-5), max(0, y1-5)
                    x2_pad, y2_pad = max(0, x2+5), max(0, y2+5)

                    cropped = frame[y1_pad: y2_pad, x1_pad: x2_pad]

                    if cropped.size == 0:
                        continue

                    ocr_result = self.reader.readtext(cropped, detail=1)

                    if ocr_result:
                        combined_text = ""
                        ocr_confidences = []

                        for detection in ocr_result:
                            raw_text = detection[1]

                            ocr_conf = detection[2]

                            cleaned_text = self._clean_plate_text(raw_text)

                            if cleaned_text:
                                combined_text += cleaned_text
                                ocr_confidences.append(ocr_conf)

                        if combined_text:
                            final_ocr_conf = sum(ocr_confidences)/len(ocr_confidences)
                            final_text = self._normalize(combined_text)
                            final_text = final_text[0:10] if len(final_text) > 10 else final_text
                            plate = {
                                "plate_text": final_text,
                                "confidence": final_ocr_conf
                            }

                            plates.append(plate)

        except Exception as e:
            print(e)
        
        return {
            "plates": plates,
            "total_plates": len(plates)
        }
    
    
    def _clean_plate_text(self, text: str) -> Optional[str]:
        """
        Clean and validate license plate text
        """
        # Remove whitespace and special characters
        text = re.sub(r'[^A-Za-z0-9]', '', text)
        
        # Remove common OCR errors
        text = text.replace('O', '0')
        text = text.replace('I', '1')
        text = text.replace('S', '5')
        text = text.replace('B', '8')
        
        # Check minimum length (3-8 characters typical for plates)
        if 3 <= len(text) <= 8:
            return text.upper()
        
        return None
    
    async def cleanup(self) -> bool:
        """
        Cleanup resources
        """
        self.reader = None
        self.is_initialized = False
        return True