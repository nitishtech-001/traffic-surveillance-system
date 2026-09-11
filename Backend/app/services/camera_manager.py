# backend/app/services/camera_manager.py
import logging
import numpy as np
from typing import Dict, Optional, List, Any
from datetime import datetime
from threading import Thread, Event
import queue
import time
import cv2
import os
from app.schema.schema_camera import CameraSchema, CameraStatusSchema
from app.models.model_traffic import TrafficModel
from app.core.config import settings

logger = logging.getLogger(__name__)

class CameraManager:
    """
    Manages multiple camera connections and RTSP streams
    """
    
    active_cameras: Dict[str, Dict[str, Any]] = {}
    camera_threads: Dict[str, Thread] = {}
    # frame_buffers: Dict[str, queue.Queue] = {}
    stop_events: Dict[str, Event] = {}
    camera_status: Dict[str, CameraStatusSchema] = {}

    @classmethod
    async def add_camera(cls, camera: CameraSchema) -> bool:
        """
        Add and connect a new camera
        """
        try:
            camera_id = camera.id
            
            # Create RTSP URL
            camera_url = cls._build_camera_url(camera)
            logging.info(f"APP MANAGER (line 38) : rtsp url :: {camera_url} ")
            # Create frame buffer
            # cls.frame_buffers[camera_id] = queue.Queue(maxsize=10)
            
            # Create stop event
            cls.stop_events[camera_id] = Event()
            
            # Store camera info
            cls.active_cameras[camera_id] = {
                "camera": camera,
                "camera_url": camera_url,
                "last_frame": None,
                "last_update": None,
                "fps": 0,
                "frame_count": 0,
                "connected": False,
                "retry_count": 0
            }

            model_path = "../ai_models/nightvision.pt"
            # Start camera thread
            cls.camera_threads[camera_id] = Thread(
                target=cls._camera_worker,
                args=(camera_id, camera_url,model_path),
                daemon=True
            )
            cls.camera_threads[camera_id].start()
            

            # Update status
            cls.camera_status[camera_id] = CameraStatusSchema.CONNECTING
            
            logger.info(f"Camera {camera_id} added successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add camera {camera.id}: {str(e)}")
            return False

    @classmethod
    def _build_camera_url(cls, camera: CameraSchema) -> str:
        """
        Build RTSP URL from camera configuration
        """
        # Different camera brands have different RTSP URL formats
        # Hikvision: rtsp://username:password@ip:554/Streaming/Channels/101
        # Dahua: rtsp://username:password@ip:554/cam/realmonitor?channel=1&subtype=0
        # Generic: rtsp://username:password@ip:554/stream
        
        username = camera.username or settings.CAMERA_USERNAME
        password = camera.password or settings.CAMERA_PASSWORD
        ## TODO: THIS IS FOR RTSP PROTOCOL
        if camera.protocol == "rtsp":
            # TODO: UPDATE THE URL FOR THAT SPECIFIC CCTV CAMERA
            
            #TODO:  FOR DEMO WE ARE USING HTTP PROTOCOL FOR PRODUCTION UPDATE CODE FOR RTSP PROTOCOL
            #url = f"rtsp://{camera.ip_address}:{camera.port}/h264.sdp"
            url = f"http://{username}:{password}@{camera.ip_address}:{camera.port}"
            
            # TODO : CHANGE THE URL LATER FOR STRAMING DIFFERENT CHANNELS

            # for  Hikvision brand CCTV CAMERA
            if camera.model and "hikvision" in camera.model.lower():
                url += "/Streaming/Channels/101"
            # for  Hikvision brand DAHUA CAMERA
            elif camera.model and "dahua" in camera.model.lower():
                url += "/cam/realmonitor?channel=1&subtype=0"
            # for testing with ip webcam using mobile phone
            else:
                url += "/video"

            print("(_build_camera_url) URL GENERATED ::: ",url)
            return url
        elif camera.protocol == "http":
            url = f"http://{username}:{password}@{camera.ip_address}:{camera.port}"

            #TODO: for differnet model we have to update the route 
            # for testing purpose we are using ip webcam that has /video route
            url += "/video"

            return url
        
        return ""

    ## deamon service of camera handling the straming
    @classmethod
    def _camera_worker(cls, camera_id: str, camera_url: str, save_dir="./uploads",model_path: str=None,conf:float=0.4):
        """
        Worker thread for continuous camera frame capture
        """
        cap = None
        video_writer = None
        retry_attempts = 0
        max_retries = settings.MAX_RETRIES
        save_dir += f"/{camera_id}"

        fps_start_time = datetime.now()
        fps_frame_counter = 0
        anotated_frame_counter = 0
        if model_path:
            model = TrafficModel(model_path=model_path,conf=conf )
        
       
       
        while not cls.stop_events[camera_id].is_set():
            try:
                # Open CAMERA URL stream
                if cap is None or not cap.isOpened():
                    logger.info(f"Connecting to camera {camera_id}: {camera_url}")

                    if video_writer:
                        video_writer.release()
                        video_writer = None

                    cap = cv2.VideoCapture(camera_url)
                    cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
                    # cap.set(cv2.CAP_PROP_FPS, 30)
                    
                    # Set timeout
                    # cap.set(cv2.CAP_PROP_POS_MSEC, 0)
                    
                    if not cap.isOpened():
                        retry_attempts += 1
                        if retry_attempts >= max_retries:
                            logger.error(f"Failed to connect to camera {camera_id} after {max_retries} attempts")
                            cls.camera_status[camera_id] = CameraStatusSchema.ERROR
                            time.sleep(2)
                            retry_attempts = 0
                        else:
                            logger.warning(f"Retrying connection to camera {camera_id} (attempt {retry_attempts}/{max_retries})")
                            time.sleep(1)
                        continue
                    
                    # # Reset retry count on successful connection
                    retry_attempts = 0
                    cls.camera_status[camera_id] = CameraStatusSchema.ONLINE
                    logger.info(f"Camera {camera_id} connected successfully")

                    # Initialize VideoWriter properties for file saving
                    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 1280
                    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 720
                    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
                    if fps <= 0 or fps > 60: fps = 30
                    
                    # Create unique file path for this reference video recording
                    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                    save_path = os.path.join(save_dir, f"_{timestamp_str}.mp4")
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    video_writer = cv2.VideoWriter(save_path, fourcc, fps, (frame_width, frame_height))
                    logger.info(f"Recording initialized for {camera_id} at path: {save_path}")
                
                    
                # Read frame
                ret, frame = cap.read()
                
                if not ret :
                    logger.warning(f"Failed to read frame from camera {camera_id}")
                    cap.release()
                    cap = None
                    cls.camera_status[camera_id] = CameraStatusSchema.OFFLINE
                    time.sleep(0.5)
                    continue

                # TODO : remove it for testing camera only
                # display_frame = cv2.resize(frame, (800,800))
                # cv2.imshow("cemera feed", display_frame)
                # cv2.waitKey(1)
                # TODO: later store the video to local for future reference
                # if video_writer is not None:
                #     video_writer.write(frame)

                camera_info = cls.active_cameras[camera_id]

                if model_path:
                    try:
                        anotated = model.infer(frame)
                        anotated_frame_counter += 1
                        camera_info["anotated_frame_count"] = anotated_frame_counter
                        camera_info["last_anotated_frame"] = anotated
                    except Exception as e:
                        camera_info["last_anotated_frame"] = frame
                        logger.error(f"{camera_id} YOLO model failed")

                # Update camera info
                camera_info["last_frame"] = frame
                
                camera_info["last_update"] = datetime.now()
                camera_info["frame_count"] += 1
                camera_info["connected"] = True
                cls.camera_status[camera_id] = CameraStatusSchema.STREAMING
                
                # Calculate FPS
                fps_frame_counter += 1
                if fps_frame_counter >= 30:
                    now = datetime.now()
                    time_diff = (now - fps_start_time).total_seconds()
                    if time_diff > 0:
                        camera_info["fps"] = round(fps_frame_counter / time_diff, 2)
                    
                    # Reset counters for the next 30-frame window
                    fps_start_time = now
                    fps_frame_counter = 0
                
            except Exception as e:
                logger.error(f"Camera worker error for {camera_id}: {str(e)}")
                if cap:
                    cap.release()
                    cap = None
                
                time.sleep(1)
       
        if cap:
            cap.release()
        if video_writer:
            video_writer.release()
        logger.info(f"Camera worker stopped for {camera_id}")

    """
    @classmethod
    async def get_frame(cls, camera_id: str, timeout: float = 0.1) -> Optional[np.ndarray]:
        try:
            if camera_id not in cls.frame_buffers:
                logger.error(f"Camera {camera_id} not found")
                return None
            
            # Try to get frame from buffer
            frame = cls.frame_buffers[camera_id].get(timeout=timeout)
            return frame
            
        except queue.Empty:
            # Fallback to last frame
            camera_info = cls.active_cameras.get(camera_id)
            if camera_info:
                return camera_info.get("last_frame")
            return None
        except Exception as e:
            logger.error(f"Error getting frame from camera {camera_id}: {str(e)}")
            return None
    """

    @classmethod
    async def get_camera_info(cls, camera_id: str) -> Dict[str, Any]:
        """
        Get camera information and status
        """
        camera_info = cls.active_cameras.get(camera_id)
        
        if not camera_info:
            return {}
        
        return {
            "id": camera_id,
            "name": camera_info["camera"].name,
            "status": cls.camera_status.get(camera_id, CameraStatusSchema.OFFLINE),
            # "buffer_size": cls.frame_buffers.get(camera_id, queue.Queue()).qsize(),
            "connected": camera_info["connected"],
            "fps": camera_info["fps"],
            "frame_count": camera_info["frame_count"],
            "last_update": camera_info["last_update"],
            "camera_url": camera_info["camera_url"]
        }

    @classmethod
    async def list_cameras(cls) -> List[Dict[str, Any]]:
        """
        List all connected cameras with status
        """
        cameras = []
        for camera_id in cls.active_cameras:
            info = await cls.get_camera_info(camera_id)
            cameras.append(info)
        return cameras

    @classmethod
    async def disconnect_camera(cls, camera_id: str) -> bool:
        """
        Disconnect a camera
        """
        try:
            
            if camera_id in cls.stop_events:
                cls.stop_events[camera_id].set()
            
            if camera_id in cls.camera_threads:
                cls.camera_threads[camera_id].join(timeout=5)
                if cls.camera_threads[camera_id].is_alive():
                    logging.info(f"camera {camera_id} is still running think another way")
            
            # Clean up
            if camera_id in cls.frame_buffers:
                while not cls.frame_buffers[camera_id].empty():
                    try:
                        cls.frame_buffers[camera_id].get_nowait()
                    except queue.Empty:
                        break
            
            # Remove from active cameras
            cls.active_cameras.pop(camera_id, None)
            cls.camera_status.pop(camera_id, None)
            
            logger.info(f"Camera {camera_id} disconnected successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting camera {camera_id}: {str(e)}")
            return False
        
    @classmethod
    async def disconnect_all(cls) -> bool:
        """
        Disconnect all cameras
        """
        try:
            for camera_id in list(cls.stop_events.keys()):
                await cls.disconnect_camera(camera_id)
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting all cameras: {str(e)}")
            return False

    @classmethod
    async def update_camera_settings(cls, camera_id: str, settings: Dict[str, Any]) -> bool:
        """
        Update camera settings (reconnect required for some changes)
        """
        try:
            camera_info = cls.active_cameras.get(camera_id)
            if not camera_info:
                return False
            
            # Update camera object
            camera = camera_info["camera"]
            for key, value in settings.items():
                if hasattr(camera, key):
                    setattr(camera, key, value)
            
            # Reconnect if IP or port changed
            if "ip_address" in settings or "port" in settings:
                await cls.disconnect_camera(camera_id)
                await cls.add_camera(camera)
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating camera settings: {str(e)}")
            return False

    