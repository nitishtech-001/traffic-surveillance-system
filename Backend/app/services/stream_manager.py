# backend/app/services/stream_manager.py
import asyncio
import subprocess
import os
import logging
from typing import Dict, Optional, Any
from datetime import datetime
import signal
import cv2
from aiortc import RTCPeerConnection, RTCSessionDescription
from .video_capture import WebRTCLiveTrack
from .camera_manager import CameraManager

from app.core.config import settings

logger = logging.getLogger(__name__)

class StreamManager:
    """
    Manages video streaming conversion from RTSP to HLS/WebRTC
    """
    
    active_streams: Dict[str, Dict[str, Any]] = {}
    stream_processes: Dict[str, subprocess.Popen] = {}
    
    def __init__(self):
        print("Stream manager initialized")
        # cls.stream_processes: Dict[str, subprocess.Popen] = {}

    
    @classmethod
    async def TODOstart_stream(cls, camera_id: str, camera_url: str) -> str:
        """
        Start HLS stream from RTSP source
        """
        try:
            # Create stream directory
            stream_dir = f"static/hls/{camera_id}"
            os.makedirs(stream_dir, exist_ok=True)
            
            # HLS output path
            hls_path = f"{stream_dir}/stream.m3u8"
            
            # FFmpeg command for RTSP to HLS conversion
            cmd = [
                "ffmpeg",
                "-fflags", "nobuffer",
                "-flags", "low_delay",
                "-i", camera_url,
                "-g","30",
                "-c:v", "libx264",
                "-preset", "veryfast",
                "-tune", "zerolatency",
                "-c:a", "aac",
                "-f", "hls",
                "-hls_time", str(settings.HLS_SEGMENT_DURATION),
                "-hls_list_size", str(settings.HLS_SEGMENT_COUNT),
                "-hls_flags", "delete_segments+append_list",
                "-hls_segment_filename", f"{stream_dir}/segment_%03d.ts",
                "-hls_start_number_source", "datetime",
                hls_path
            ]
            
            # Start FFmpeg process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid if os.name == 'posix' else None
            )
            
            # Store process
            cls.stream_processes[camera_id] = process
            
            # Store stream info
            cls.active_streams[camera_id] = {
                "camera_id": camera_id,
                "camera_url": camera_url,
                "hls_url": f"/static/hls/{camera_id}/stream.m3u8",
                "started_at": datetime.now(),
                "status": "running",
                "segments_created": 0
            }
            
            logger.info(f"HLS stream started for camera {camera_id}")
            logger.info(f"Stream URL: {cls.active_streams[camera_id]['hls_url']}")
            
            # Start monitoring process
            asyncio.create_task(cls._monitor_stream(camera_id))
            
            return cls.active_streams[camera_id]["hls_url"]
            
        except Exception as e:
            logger.error(f"Failed to start stream for camera {camera_id}: {str(e)}")
            return ""
   
    @classmethod
    async def start_stream(cls, camera_id: str, sdp: str, type: str):
        pc = RTCPeerConnection()
        video_track = WebRTCLiveTrack(camera_id=camera_id, active_cameras_dict=CameraManager.active_cameras)
        pc.addTrack(video_track)
        @pc.on("connectionstatechange")
        async def on_connectionstatechange():
            if pc.connectionState in ["failed", "closed"]:
                await pc.close()

        # 3. Perform SDP Handshake
        offer = RTCSessionDescription(sdp=sdp, type=type)
        await pc.setRemoteDescription(offer)
        
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        return {
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        }
        
    @classmethod
    async def _monitor_stream(cls, camera_id: str):
        """
        Monitor FFmpeg process and handle errors
        """
        process = cls.stream_processes.get(camera_id)
        if not process:
            return
        
        while True:
            try:
                # Check if process is still running
                if process.poll() is not None:
                    logger.error(f"FFmpeg process for camera {camera_id} stopped")
                    
                    # Restart stream
                    camera_url = cls.active_streams.get(camera_id, {}).get("camera_url")
                    if camera_url:
                        logger.info(f"Restarting stream for camera {camera_id}")
                        await cls.restart_stream(camera_id, camera_url)
                    break
                
                # Read stderr for errors
                if process.stderr:
                    error_line = process.stderr.readline()
                    if error_line:
                        error_str = error_line.decode().strip()
                        if "error" in error_str.lower():
                            logger.warning(f"FFmpeg warning for {camera_id}: {error_str}")
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Stream monitoring error for {camera_id}: {str(e)}")
                await asyncio.sleep(5)

    @classmethod
    async def stop_stream(cls, camera_id: str):
        """
        Stop HLS stream
        """
        try:
            process = cls.stream_processes.get(camera_id)
            if process:
                # Terminate process
                if os.name == 'posix':
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                else:
                    process.terminate()
                
                process.wait(timeout=5)
                cls.stream_processes.pop(camera_id, None)
                
            # Remove from active streams
            cls.active_streams.pop(camera_id, None)
            
            logger.info(f"Stream stopped for camera {camera_id}")
            
        except Exception as e:
            logger.error(f"Error stopping stream for {camera_id}: {str(e)}")

    @classmethod
    async def restart_stream(cls, camera_id: str, camera_url: str) -> bool:
        """
        Restart HLS stream
        """
        try:
            # Stop existing stream
            await cls.stop_stream(camera_id)
            
            # Wait for cleanup
            await asyncio.sleep(1)
            
            # Start new stream
            hls_url = await cls.start_stream(camera_id, camera_url)
            
            return bool(hls_url)
            
        except Exception as e:
            logger.error(f"Error restarting stream for {camera_id}: {str(e)}")
            return False

    @classmethod
    async def get_stream_info(cls, camera_id: str) -> Optional[Dict[str, Any]]:
        """
        Get stream information
        """
        return cls.active_streams.get(camera_id)

    @classmethod
    async def stop_all_streams(cls):
        """
        Stop all active streams
        """
        for camera_id in list(cls.active_streams.keys()):
            await cls.stop_stream(camera_id)
        logger.info("All streams stopped")

    @classmethod
    def _generate_stream_thumbnail(cls, camera_id: str, frame) -> bool:
        """
        Generate thumbnail for stream preview
        """
        try:
            thumbnail_dir = f"static/thumbnails"
            os.makedirs(thumbnail_dir, exist_ok=True)
            
            # Save thumbnail
            thumbnail_path = f"{thumbnail_dir}/{camera_id}_thumb.jpg"
            cv2.imwrite(thumbnail_path, frame)
            
            return True
            
        except Exception as e:
            logger.error(f"Error generating thumbnail: {str(e)}")
            return False