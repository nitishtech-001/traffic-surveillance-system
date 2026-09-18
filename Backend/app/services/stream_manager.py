# backend/app/services/stream_manager.py
import asyncio
import subprocess
import os
import logging
from typing import Dict, Optional, Any
import signal
from aiortc import RTCPeerConnection, RTCSessionDescription
from .video_capture import WebRTCLiveTrack
from .camera_manager import CameraManager


logger = logging.getLogger(__name__)

class StreamManager:
    """
    Manages video streaming conversion from RTSP to HLS/WebRTC
    """
    
    active_streams: Dict[str, Dict[str, Any]] = {}
    stream_processes: Dict[str, subprocess.Popen] = {}
    
    def __init__(self):
        print("Stream manager initialized")
   
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
    async def stop_stream(cls, camera_id: str):
        """
        Stop WEBRTC
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
