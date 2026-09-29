# from aiortc import MediaStreamTrack
from aiortc import VideoStreamTrack
import asyncio
from av import VideoFrame
import logging
import json

logger = logging.getLogger(__name__)

class WebRTCLiveTrack(VideoStreamTrack):
    """
    A WebRTC track that pulls the absolute latest frame from your Class-level active_cameras dict.
    """
    kind = "video"

    def __init__(self, camera_id: str, active_cameras_dict: dict, data_channel: dict=None):
        super().__init__()
        self.camera_id = camera_id
        self.active_cameras = active_cameras_dict
        self.annotated_frame_count = None
        self.data_channel = data_channel
        logger.info("WebRTC Establish....")

    async def recv(self):
        # 1. Ensure the camera entry exists and has processed at least one frame
        while (self.camera_id not in self.active_cameras or 
               self.active_cameras[self.camera_id].get("results") is None):
            await asyncio.sleep(0.02)

        camera_info = self.active_cameras[self.camera_id]
        
        # 2. Track frame counts to detect duplicates (leveraging camera_info["frame_count"] from your worker!)
        current_frame_count = camera_info.get("annotated_frame_count", 0)

        # If the worker hasn't grabbed a new frame yet, back off to target ~30 FPS
        if current_frame_count == self.annotated_frame_count:
            await asyncio.sleep(1 / 30)
            # Re-fetch after sleep
            camera_info = self.active_cameras[self.camera_id]
            current_frame_count = camera_info.get("annotated_frame_count", 0)

        self.annotated_frame_count = current_frame_count
        
        # 3. Safely copy the frame array from the dictionary 
        frame_with_data = camera_info["results"].copy()

        # 4. setting the data about the annotated frame
        if "data" in frame_with_data:
            if self.data_channel and self.data_channel.readyState == "open":
                self.data_channel.send(json.dumps(frame_with_data["data"]))
        
        frame = frame_with_data["annotated_frame"]

        # 5. Convert OpenCV BGR array to PyAV VideoFrame for aiortc transmission
        new_frame = VideoFrame.from_ndarray(frame, format="bgr24")
        pts, time_base = await self.next_timestamp()
        new_frame.pts = pts
        new_frame.time_base = time_base

        return new_frame