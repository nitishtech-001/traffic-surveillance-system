# backend/app/agents/license_plate.py
import cv2
import numpy as np
from typing import Dict, Any, List, Optional
import easyocr
import re
import logging

from app.agents.agent_base import BaseAgent
from app.schema.schema_detection import LicensePlateDetectionSchema, BoundingBoxSchema

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
        
    async def initialize(self) -> bool:
        """
        Initialize OCR and detection models
        """
        try:
            logger.info("Initializing License Plate Detection Agent")
            
            # Initialize EasyOCR reader
            languages = self.config.get("languages", ['en'])
            self.reader = easyocr.Reader(languages, gpu=False)
            
            # Load plate detection model if needed
            # We'll use simple morphological operations for plate detection
            
            self.is_initialized = True
            logger.info("License Plate Agent initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize License Plate Agent: {str(e)}")
            return False
    
    async def process(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Detect and read license plates from frame
        """
        if not self.is_initialized:
            raise RuntimeError("Agent not initialized")
        
        # Detect potential plate regions
        plate_regions = self._detect_plate_regions(frame)
        
        plates = []
        
        for bbox in plate_regions:
            # Crop plate region
            x1, y1, x2, y2 = bbox
            cropped = frame[y1:y2, x1:x2]
            
            if cropped.size == 0:
                continue
            
            # Perform OCR
            result = self.reader.readtext(cropped, detail=1)
            
            if result:
                for detection in result:
                    text = detection[1]
                    confidence = detection[2]
                    
                    # Clean and validate plate text
                    plate_text = self._clean_plate_text(text)
                    
                    if plate_text and confidence > 0.5:
                        plate = LicensePlateDetectionSchema(
                            plate_text=plate_text,
                            bbox=BoundingBoxSchema(
                                x1=float(x1),
                                y1=float(y1),
                                x2=float(x2),
                                y2=float(y2),
                                confidence=float(confidence)
                            ),
                            confidence=float(confidence)
                        )
                        plates.append(plate)
        
        return {
            "plates": [p.dict() for p in plates],
            "total_plates": len(plates)
        }
    
    def _detect_plate_regions(self, frame: np.ndarray) -> List[List[int]]:
        """
        Detect potential license plate regions using image processing
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply bilateral filter for noise reduction
        gray = cv2.bilateralFilter(gray, 11, 17, 17)
        
        # Edge detection
        edged = cv2.Canny(gray, 30, 200)
        
        # Find contours
        contours, _ = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours based on aspect ratio and area
        plate_contours = []
        min_area = frame.shape[0] * frame.shape[1] * 0.001
        max_area = frame.shape[0] * frame.shape[1] * 0.1
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            if min_area < area < max_area:
                # Approximate contour to polygon
                peri = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
                
                # Check if it's a rectangle-like shape
                if len(approx) == 4:
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h if h > 0 else 0
                    
                    # License plates typically have aspect ratio between 2:1 and 5:1
                    if 2 < aspect_ratio < 5:
                        plate_contours.append([x, y, x + w, y + h])
        
        return plate_contours
    
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