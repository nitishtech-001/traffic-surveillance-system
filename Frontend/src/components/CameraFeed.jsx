import { useEffect, useRef, useState } from 'react';
import { useCameraStore } from "../services/useCameraStore.js";
import { useStreamStore } from '../services/useStreamStore.js';

export default function CameraLiveFeed() {
    const currentCamera = useCameraStore((state) => state.currentCamera);
    const startStream = useStreamStore((state) => state.startStream);
    const currentStream = useStreamStore((state)=>state.currentStream)

    // let wsSignalingUrl = "ws://localhost:8000/ws/stream";
    const videoRef = useRef(null);
    const peerConnectionRef = useRef(null);
    const socketRef = useRef(null);
    const [connectionStatus, setConnectionStatus] = useState("Disconnected");

    useEffect(() => {
        // 1. Safety check: Exit if no active camera selection exists
        if (!currentCamera || !currentCamera.id) {
            disconnectFeed();
            setConnectionStatus("No Camera Selected");
            return;
        }

        // Trigger your global store action
        startStream(currentCamera);

    }, [currentCamera]);

    useEffect(()=>{
        if (!currentStream)  return
        // 2. Fire up the WebRTC signaling connection
        connectToLiveFeed(currentStream);

        // 3. Clear the peer connections on component switch/unmount
        return () => {
            disconnectFeed();
        };
    },[currentStream])

    const connectToLiveFeed = (ws_url) => {
        setConnectionStatus("Connecting...");
        
        // Connect to FastAPI WebRTC signaling route
        socketRef.current = new WebSocket(ws_url);

        // FIX #1: Corrected standard Google STUN url syntax
        peerConnectionRef.current = new RTCPeerConnection({
            iceServers: [{ urls: "stun:stun.l.google.com:19302" }]
        });

        // Handle incoming WebRTC video track from backend
        peerConnectionRef.current.ontrack = (event) => {
            if (videoRef.current && event.streams[0]) {
                videoRef.current.srcObject = event.streams[0];
                setConnectionStatus("Live 🟢");
            }
        };

        // Forward local network candidates up to FastAPI
        peerConnectionRef.current.onicecandidate = (event) => {
            if (event.candidate && socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
                socketRef.current.send(JSON.stringify({
                    type: "candidate",
                    candidate: event.candidate,
                    cameraId: currentCamera.id
                }));
            }
        };

        socketRef.current.onopen = () => {
            // Let the backend know which camera stream we want to pull
            socketRef.current.send(JSON.stringify({
                type: "request_stream",
                cameraId: currentCamera.id
            }));
        };

        socketRef.current.onmessage = async (message) => {
            const data = JSON.parse(message.data);

            // Handle incoming backend configuration offer
            if (data.type === "offer") {
                await peerConnectionRef.current.setRemoteDescription(new RTCSessionDescription(data.sdp));

                const answer = await peerConnectionRef.current.createAnswer();
                await peerConnectionRef.current.setLocalDescription(answer);

                socketRef.current.send(JSON.stringify({
                    type: "answer",
                    sdp: peerConnectionRef.current.localDescription,
                    cameraId: currentCamera.id
                }));
            }
            // Ingest candidate routes dropped by the server
            else if (data.type === "candidate" && data.candidate) {
                try {
                    await peerConnectionRef.current.addIceCandidate(new RTCIceCandidate(data.candidate));
                } catch (e) {
                    console.error("Error adding received ice candidate", e);
                }
            }
        };

        socketRef.current.onclose = () => setConnectionStatus("Disconnected 🔴");
        socketRef.current.onerror = () => setConnectionStatus("Connection Error ⚠️");
    };

    const disconnectFeed = () => {
        if (videoRef.current) videoRef.current.srcObject = null;
        if (peerConnectionRef.current) {
            peerConnectionRef.current.close();
            peerConnectionRef.current = null;
        }
        if (socketRef.current) {
            socketRef.current.close();
            socketRef.current = null;
        }
        setConnectionStatus("Disconnected 🔴");
    };

    return (
        <div className="w-full max-w-2xl mx-auto rounded-2xl overflow-hidden bg-slate-900 border border-slate-800 p-4 shadow-xl">
            <div className="flex justify-between items-center mb-3">
                <h3 className="text-sm font-semibold text-slate-200">
                    {currentCamera?.name || "Unknown Camera"} - Live Feed
                </h3>
                <span className={`text-xs px-2.5 py-1 rounded-full font-bold ${connectionStatus === "Live 🟢" ? "bg-emerald-500/10 text-emerald-400" : "bg-slate-800 text-slate-400"
                    }`}>
                    {connectionStatus}
                </span>
            </div>

            <div className="relative aspect-video w-full rounded-xl overflow-hidden bg-black flex items-center justify-center">
                <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    muted
                    className="w-full h-full object-cover"
                />
                {!currentCamera && (
                    <p className="absolute text-slate-500 text-sm">Please select a camera to start the feed</p>
                )}
            </div>
        </div>
    );
}
