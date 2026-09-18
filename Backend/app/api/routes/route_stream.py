# backend/app/api/routes/stream.py
from fastapi import APIRouter, HTTPException

from app.services.camera_manager import CameraManager
from app.services.stream_manager import StreamManager


router = APIRouter()

@router.post("/{camera_id}/start")
async def start_stream(
    # camera_id: str, request: Reques
    camera_id: str
    # current_user: Dict = Depends(get_current_user)
):
    """
    Start HLS stream for a camera
    """
    try:

        # Get camera info
        # params = await request.json()
        camera_info = await CameraManager.get_camera_info(camera_id)
        if not camera_info:
            raise HTTPException(status_code=404, detail="Camera not found")
        sdp = "nk"
        type = "offer"
        
        # Get RTSP URL
        

        camera_url = CameraManager.active_cameras.get(camera_id, {}).get("camera_url")
        print(f"Camera id {camera_id} and camera url {camera_url}")
        if not camera_url:
            raise HTTPException(status_code=400, detail="Camera not ready")

        # returning the websoket url
        return {"ws_url":f"ws://localhost:8000/api/ws/stream/{camera_id}"}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{camera_id}/stop")
async def stop_stream(
    camera_id: str,
    # current_user: Dict = Depends(get_current_user)
):
    """
    Stop HLS stream for a camera
    """
    try:
        await StreamManager.stop_stream(camera_id)
        return {
            "message": "Stream stopped successfully",
            "camera_id": camera_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{camera_id}/update/{conf}/{interval}")
async def update_stream(camera_id, conf:float, interval:float):
    conf = conf/100
    interval = interval/1000 # changing to milisecond
    try:
        success = await CameraManager.update_conf_interval(camera_id, conf, interval)
        if success:
            return {"message": f"Interval now : {interval*1000}ms and Conf now : {conf*100}%"}
        else:
            raise HTTPException(504, "Something went wrong.")
    except Exception as e:
        print(e)
