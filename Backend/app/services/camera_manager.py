# backend/app/services/camera_manager.py
import logging
from fastapi import HTTPException
from typing import Dict, List, Any
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
            
            # Create Camera URL
            camera_url = cls._build_camera_url(camera)
            logger.info(f"Camera URL :: {camera_url}")
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
                "retry_count": 0,
                "conf": 0.5,
                "interval": 100/1000 # in milisecond for processing frame
            }
            agent_file_name = ""
            agent_name = ""
            save_dir = os.getcwd()+"/uploads"
            conf = 0.5 # hardcode value of confidence
            if camera.agent:
                ## TODO : UPDATE this for new model you use
                user_agent_name = camera.agent.lower()
                if "object-detection" in user_agent_name:
                    agent_file_name = "nightvision.pt"
                    agent_name = "object-detection"
                elif "face-detection" in user_agent_name:
                    agent_file_name = "facedetection.pt"
                    agent_name = "face-detection"
                elif "licenseplate-detection" in user_agent_name:
                    agent_file_name = "licenseplate.pt"
                    agent_name = "licenseplate-detection"
                elif "motion-detection" in user_agent_name:
                    agent_file_name = "motiondetection.pt"
                    agent_name = "motion-detection"
                elif "text-detection" in user_agent_name:
                    agent_file_name = "textdetection.pt"
                    agent_name = "text-detection"
                else:
                    agent_file_name = ""
                    agent_name = ""

            # Start camera thread
            cls.camera_threads[camera_id] = Thread(
                target=cls._camera_worker,
                args=(camera_id, camera_url,save_dir, agent_file_name,agent_name),
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
        Get camera information and generate Camera url so backend and listen the camera feed
        """
        # Different camera brands have different RTSP URL formats
        # Hikvision: rtsp://username:password@ip:554/Streaming/Channels/101
        # Dahua: rtsp://username:password@ip:554/cam/realmonitor?channel=1&subtype=0
        # Generic: rtsp://username:password@ip:554/stream or /video
        
        username = camera.username or settings.CAMERA_USERNAME
        password = camera.password or settings.CAMERA_PASSWORD
        protocol = camera.protocol
        route = ""
        if camera.protocol == "rtsp" and camera.model:
            # TODO: UPDATE THE URL FOR THAT SPECIFIC CCTV CAMERA 
            #url = f"rtsp://{camera.ip_address}:{camera.port}/h264.sdp"
            camera_model = camera.model.lower()
            # Axis Communications P3818-PVE CCTV CAMERA
            if "axispve" in camera_model:
                route = "axis-media/media.amp?camera=1&videocodec=h264"
            # for Hikvision Pro DS-2DE7A225IW-AEB CCTV CAMERA
            elif "hikvision" in camera_model:
                route = "Streaming/Channels/101"
            # for Dahua WizMind S Series 4K CCTV CAMERA
            elif "dahua" in camera_model:
                route = "cam/realmonitor?channel=1&subtype=0"
            elif "ipwebcam" in camera_model:
                route = "video"
            # chaaper camers TP-Link Tapo C200 for local
            elif "local" in camera_model:
                route = "/stream1"

        elif camera.protocol == "http" and camera.model:
            camera_model = camera.model.lower()
            # Axis Communications P3818-PVE CCTV CAMERA
            if "axispve" in camera_model:
                route = "axis-cgi/mjpeg/video.cgi?camera=1"
            # for Hikvision Pro DS-2DE7A225IW-AEB CCTV CAMERA
            elif "hikvision" in camera_model:
                route = "ISAPI/Streaming/channels/102/httpPreview"
            # for Dahua WizMind S Series 4K CCTV CAMERA
            elif "dahua" in camera_model:
                route = "cgi-bin/mjpg/video.cgi?channel=1&subtype=1"
            # Mobile camera steam using IP-WEBCAM Application
            elif "ipwebcam" in camera_model:
                route = "video"
            elif "local" in camera_model:
                route = "set for local camera"
        
        camera_url = f"{protocol}://{username}:{password}@{camera.ip_address}:{camera.port}/{route}"
        return camera_url

    ## deamon service of camera handling the straming
    @classmethod
    def _camera_worker(cls, camera_id: str, camera_url: str, save_dir="./uploads",agent_file_name: str=None,agent_name: str=None):
        """
        Worker thread for continuous camera frame capture
        """
        cap = None
        video_writer = None
        retry_attempts = 0
        max_retries = settings.MAX_RETRIES
        predict_interval = time.time()

        save_dir += f"/{camera_id}"
        try:
            os.makedirs(save_dir,exist_ok=True)
        except Exception as e:
            logger.error(e)

        fps_start_time = datetime.now()
        fps_frame_counter = 0
        annotated_frame_counter = 0
        agent = None
        
        agent = TrafficModel(agent_file_name,agent_name)
       
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

                    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 1280
                    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 720
                    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
                    if fps <= 0 or fps > 60: fps = 30
                    
                  
                    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                    save_path = os.path.join(save_dir, f"_{timestamp_str}.mp4")
                    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                    video_writer = cv2.VideoWriter(save_path, fourcc, fps, (frame_width, frame_height))
                    logger.info(f"Recording initialized for {camera_id} at path: {save_path}")
                
                    
                # Read frame
                ret, frame = cap.read()
                
                if not ret :
                    logger.warning(f"Failed to read frame from camera {camera_id}")
                    cap.release()
                    cap = None
                    if video_writer:
                        video_writer.release()
                    cls.camera_status[camera_id] = CameraStatusSchema.OFFLINE
                    time.sleep(0.5)
                    continue

                # TODO : remove it for testing camera only
                # display_frame = cv2.resize(frame, (800,800))
                # cv2.imshow("cemera feed", display_frame)
                # cv2.waitKey(1)

                if video_writer is not None:
                    video_writer.write(frame)

                camera_info = cls.active_cameras[camera_id]
                if predict_interval+camera_info['interval'] <= time.time():
                    try:
                        annotated = agent.predict(frame,camera_info['conf'])
                        annotated_frame_counter += 1
                        camera_info["annotated_frame_count"] = annotated_frame_counter
                        camera_info["last_annotated_frame"] = annotated
                        predict_interval = time.time()
                    except Exception as e:
                        camera_info["last_annotated_frame"] = frame
                        logger.error(f"{camera_id} YOLO model failed")
                        print(e)

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
                if video_writer:
                    video_writer.release()
                
                time.sleep(1)
       
        if cap:
            cap.release()
        if video_writer:
            video_writer.release()

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
                    logger.info(f"camera {camera_id} is still running think another way")
            
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

    @classmethod
    async def update_conf_interval(cls, camera_id,conf, interval):
        if camera_id in cls.camera_status and cls.camera_status[camera_id] == CameraStatusSchema.STREAMING:
            cls.active_cameras[camera_id]['conf'] = conf
            cls.active_cameras[camera_id]['interval'] = interval
            return True
        
        raise HTTPException(404,"camera id not found.")
