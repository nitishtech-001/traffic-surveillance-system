# backend/app/api/routes/stream.py
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import FileResponse, StreamingResponse
from typing import Dict, Any
import os

from app.services.camera_manager import CameraManager
from app.services.stream_manager import StreamManager
from app.api.dependencies.authenticate import get_current_user


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
        print("Here it is cleaned thank you",camera_id)

        camera_url = CameraManager.active_cameras.get(camera_id, {}).get("camera_url")
        print(f"Camera id {camera_id} and camera url {camera_url}")
        if not camera_url:
            raise HTTPException(status_code=400, detail="Camera not ready")
        
        # TODO: shifting from hls to SRTP because hls has high latency and we have to choose the low latency technology for live streaming
        # hls_url = await StreamManager.start_stream(camera_id=camera_id, camera_url=camera_url)
        # if not hls_url:
        #     raise HTTPException(status_code=500, detail="Failed to start stream")
        # print("Hls url generated sucessfully ::: ", hls_url)
        # return {
        #     "message": "Stream started successfully",
        #     "camera_id": camera_id,
        #     "hls_url": hls_url
        # }
        # setting the SRTP( secure-real time transfer protocol) and handshake betwene frontend and backend
        
        # now setting the session between the frontend and backend
        # try:
        #     # TODO : add verification for sdp and type later, CURRENTLY in testing phase
        #     print("Stablishing connction between Back and Front")
        #     wsconnection = await StreamManager.start_stream(camera_id, sdp, type)
        #     print("sdp :: ",sdp, " type :::: ", type, " connnection url ::: ", wsconnection)
        #     return wsconnection
        # except Exception as e:
        #     print("Connection stablish Error back and Front")
        #     print(e) 

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

@router.get("/{camera_id}/playlist.m3u8")
async def get_playlist(
    camera_id: str,
    # current_user: Dict = Depends(get_current_user)
):
    """
    Get HLS playlist file
    """
    try:
        playlist_path = f"static/hls/{camera_id}/stream.m3u8"
        if not os.path.exists(playlist_path):
            raise HTTPException(status_code=404, detail="Playlist not found")
        
        return FileResponse(playlist_path, media_type="application/vnd.apple.mpegurl")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{camera_id}/segment/{segment_name}")
async def get_segment(
    camera_id: str,
    segment_name: str,
    # current_user: Dict = Depends(get_current_user)
):
    """
    Get HLS segment file
    """
    try:
        segment_path = f"static/hls/{camera_id}/{segment_name}"
        if not os.path.exists(segment_path):
            raise HTTPException(status_code=404, detail="Segment not found")
        
        return FileResponse(segment_path, media_type="video/MP2T")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))