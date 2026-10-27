import { useEffect, useRef } from 'react';
import { useCamera } from "../hooks/useCamera.js";
import { useCameraStream } from '../hooks/useCameraStream.js';
import { useWebRTC } from '../hooks/useWebRTC.js'; // Import your new store
import { FaCamera, FaStop, FaVideo } from 'react-icons/fa';

export default function CameraLiveFeed() {
    const currentCamera = useCamera((state) => state.currentCamera);
    const currentStream = useCameraStream((state) => state.streamUrl);
    const startStream = useCameraStream((state) => state.startStream);

    // Subscribe to decoupled WebRTC global states/actions
    const connectionStatus = useWebRTC((state) => state.connectionStatus);
    const streamObject = useWebRTC((state) => state.streamObject);
    const connectToLiveFeed = useWebRTC((state) => state.connectToLiveFeed);
    const disconnectFeed = useWebRTC((state) => state.disconnectFeed);

    const record = useCameraStream(state => state.record)
    const updateConfiguration = useCameraStream(state=> state.updateConfiguration)

    const videoRef = useRef(null);

    // Hook 1: Handle stream updateConfiguration changes on camera switch
    useEffect(() => {
        if (!currentCamera?.id) return;
        startStream(currentCamera.id);
        console.log("Current Camera ::: " + currentCamera.id + " Stream Url ::: " + currentStream)
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
    console.log(streamObject)

    const handleRecord = async () => {
        if(!currentCamera){
            toast.warning("Select the camera first.",{toastId:"cameranotfound"})
            return
        }
        const toggle = record === true ? false : true
        const configuration ={
            "record" : toggle
        }
        await updateConfiguration(currentCamera.id,configuration)
    }

    const handleCapture = ()=>{
        if(!currentCamera){
            toast.warning("Select the camera first.",{toastId:"cameranotfound"})
            return
        }

        const video = videoRef.current;
        if (!video) return;

        // Use intrinsic video size, fallback to client size, or default to 640x480
        const w = video.videoWidth || video.clientWidth || 640;
        const h = video.videoHeight || video.clientHeight || 480;

        const canvas = document.createElement("canvas");
        canvas.width = w;
        canvas.height = h;

        const ctx = canvas.getContext("2d");
        ctx.drawImage(video, 0, 0, w, h);

        // Using toBlob prevents the 0-byte issue common with data URLs
        canvas.toBlob((blob) => {
            if (!blob || blob.size === 0) return console.error("Empty frame caught");

            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `snapshot_${Date.now()}.png`;

            document.body.appendChild(a);
            a.click();

            // Clean up
            a.remove();
            URL.revokeObjectURL(url);
        }, "image/png");

    }

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
            <div className="flex items-center justify-between mt-2">
                <div className="flex flex-wrap items-center gap-3">
                    <button
                        type="button"
                        className={`inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold shadow-sm transition ${record ? 'bg-rose-500 text-white shadow-rose-500/20 hover:bg-rose-600' : 'bg-slate-900 text-white hover:bg-slate-700 dark:bg-slate-700 dark:hover:bg-slate-600'} disabled:cursor-not-allowed disabled:opacity-50`}
                        onClick={handleRecord}
                        disabled={!currentCamera?.id}
                    >
                        {record ? <FaStop /> : <FaVideo />}
                        {record ? 'Stop' : 'Record'}
                    </button>

                    <button
                        type="button"
                        className="inline-flex items-center gap-2 rounded-xl border border-sky-200 bg-sky-50 px-4 py-2.5 text-sm font-semibold text-sky-700 shadow-sm transition hover:border-sky-300 hover:bg-sky-100 disabled:cursor-not-allowed disabled:opacity-50 dark:border-sky-500/40 dark:bg-sky-500/10 dark:text-sky-300 dark:hover:bg-sky-500/20"
                        onClick={handleCapture}
                        disabled={!currentCamera?.id}
                    >
                        <FaCamera />
                        Capture
                    </button>

                </div>

                <div className="flex flex-wrap items-center gap-2">
                    <span className={`inline-flex items-center rounded-full border px-3 py-1.5 text-xs font-medium ${currentCamera?.id ? 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-500/40 dark:bg-emerald-500/10 dark:text-emerald-300' : 'border-rose-200 bg-rose-50 text-rose-700 dark:border-rose-500/40 dark:bg-rose-500/10 dark:text-rose-300'}`}>
                        {currentCamera?.id ? '● Online' : '● Offline'}
                    </span>

                    {currentCamera && (
                        <span className="hidden rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-600 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 sm:inline-flex">
                            Camera {currentCamera?.name}
                        </span>
                    )}
                </div>
            </div>
        </div>
    );
}
