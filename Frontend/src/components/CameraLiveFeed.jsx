import { useEffect, useRef } from 'react';
import { useCamera } from "../hooks/useCamera.js";
import { useCameraStream } from '../hooks/useCameraStream.js';
import { useWebRTC } from '../hooks/useWebRTC.js'; // Import your new store

export default function CameraLiveFeed() {
    const currentCamera = useCamera((state) => state.currentCamera);
    const currentStream = useCameraStream((state) => state.streamUrl);
    const startStream = useCameraStream((state) => state.startStream);

    // Subscribe to decoupled WebRTC global states/actions
    const connectionStatus = useWebRTC((state) => state.connectionStatus);
    const streamObject = useWebRTC((state) => state.streamObject);
    const connectToLiveFeed = useWebRTC((state) => state.connectToLiveFeed);
    const disconnectFeed = useWebRTC((state) => state.disconnectFeed);

    const videoRef = useRef(null);

    // Hook 1: Handle stream configuration changes on camera switch
    useEffect(() => {
        if (!currentCamera?.id) return;
        startStream(currentCamera.id);
        console.log("Current Camera ::: "+currentCamera.id+" Stream Url ::: "+currentStream)
    }, [currentCamera?.id, startStream]);

    // Hook 2: Trigger WebRTC process and handle cleanups
    useEffect(() => {
        if (!currentStream || !currentCamera?.id) return;

        connectToLiveFeed(currentStream, currentCamera.id);

        return () => {
            disconnectFeed();
        };
    }, [currentStream, currentCamera?.id, connectToLiveFeed, disconnectFeed]);

    // Hook 3: Synchronize global MediaStream object to DOM element video source
    useEffect(() => {
        if (videoRef.current) {
            videoRef.current.srcObject = streamObject;
        }
    }, [streamObject]);
 
    return (
        <div className="w-full max-w-4xl mx-auto rounded-2xl overflow-hidden bg-slate-900 border border-slate-800 p-2 shadow-xl">
            <div className="flex justify-between items-center mb-3">
                <h3 className="text-sm font-semibold text-slate-200">
                    {currentCamera?.name || "Unknown Camera"} - Live Feed
                </h3>
                <span className={`text-xs px-2.5 py-1 rounded-full font-bold ${connectionStatus === "Live 🟢" ? "bg-emerald-500/10 text-emerald-400" : "bg-slate-800 text-slate-400"
                    }`}>
                    {connectionStatus}
                </span>
            </div>

            <div className="relative aspect-video w-full rounded-lg overflow-hidden bg-black flex items-center justify-center">
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
