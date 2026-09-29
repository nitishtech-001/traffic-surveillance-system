from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
from aiortc.sdp import candidate_from_sdp
from app.services.camera_manager import CameraManager
from app.services.video_capture import WebRTCLiveTrack

router = APIRouter()

@router.websocket("/stream/{camera_id}")
async def stream_websocket(websocket: WebSocket, camera_id: str):
    await websocket.accept()
    pc = RTCPeerConnection()
    
    camera_url = CameraManager.active_cameras.get(camera_id, {}).get("camera_url", "")
    if not camera_url:
        await websocket.close(code=1008, reason="Camera not ready")
        return

    # Data channel explicitly for each annotated_frame
    data_channel = pc.createDataChannel("metadata_channel")

    video_track = WebRTCLiveTrack(camera_id=camera_id, active_cameras_dict=CameraManager.active_cameras, data_channel=data_channel)
    pc.addTrack(video_track)

    @pc.on("connectionstatechange")
    async def on_state():
        if pc.connectionState in ("failed", "closed"):
            await pc.close()
            await websocket.close()

    @pc.on("icecandidate")
    async def on_icecandidate(candidate):
        if candidate:
            await websocket.send_json({
                "type": "candidate",
                "candidate": {
                    "candidate": candidate.candidate,
                    "sdpMid": candidate.sdpMid,
                    "sdpMLineIndex": candidate.sdpMLineIndex,
                }
            })

    try:
        # Backend creates the OFFER (since it has the track)
        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)

        await websocket.send_json({
            "type": "offer",
            "sdp": {
                "type": pc.localDescription.type,
                "sdp": pc.localDescription.sdp,
            }
        })

        while True:
            data = await websocket.receive_json()
            if data["type"] == "answer":
                await pc.setRemoteDescription(
                    RTCSessionDescription(sdp=data["sdp"]["sdp"], type=data["sdp"]["type"])
                )
            elif data["type"] == "candidate":
                c = data["candidate"]
                candidate_str = c.get("candidate", "")
                if not candidate_str:
                    continue    # empty string = end-of-candidates, aiortc doesn't handle it well
                candidate = candidate_from_sdp(candidate_str.removeprefix("candidate:"))
                candidate.sdpMid = c.get("sdpMid")
                candidate.sdpMLineIndex = c.get("sdpMLineIndex")
                await pc.addIceCandidate(candidate)

    except WebSocketDisconnect:
        pass
    finally:
        await pc.close()