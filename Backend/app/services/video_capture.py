# from aiortc import MediaStreamTrack
from aiortc import VideoStreamTrack
import asyncio
from av import VideoFrame

class WebRTCLiveTrack(VideoStreamTrack):
    """
    A WebRTC track that pulls the absolute latest frame from your Class-level active_cameras dict.
    """
    kind = "video"

    def __init__(self, camera_id: str, active_cameras_dict: dict):
        super().__init__()
        self.camera_id = camera_id
        self.active_cameras = active_cameras_dict
        self.anotated_frame_count = None

    async def recv(self):
        # 1. Ensure the camera entry exists and has processed at least one frame
        while (self.camera_id not in self.active_cameras or 
               self.active_cameras[self.camera_id].get("last_anotated_frame") is None):
            await asyncio.sleep(0.02)

        camera_info = self.active_cameras[self.camera_id]
        
        # 2. Track frame counts to detect duplicates (leveraging camera_info["frame_count"] from your worker!)
        current_frame_count = camera_info.get("anotated_frame_count", 0)

        # If the worker hasn't grabbed a new frame yet, back off to target ~30 FPS
        if current_frame_count == self.anotated_frame_count:
            await asyncio.sleep(1 / 30)
            # Re-fetch after sleep
            camera_info = self.active_cameras[self.camera_id]
            current_frame_count = camera_info.get("anotated_frame_count", 0)

        self.anotated_frame_count = current_frame_count

        # 3. Safely copy the frame array from the dictionary 
        frame = camera_info["last_anotated_frame"].copy()

        # 4. Optional AI Model processing step without blocking the main event loop
        # frame = await asyncio.get_event_loop().run_in_executor(None, your_ai_model, frame)

        # 5. Convert OpenCV BGR array to PyAV VideoFrame for aiortc transmission
        new_frame = VideoFrame.from_ndarray(frame, format="bgr24")
        pts, time_base = await self.next_timestamp()
        new_frame.pts = pts
        new_frame.time_base = time_base

        return new_frame