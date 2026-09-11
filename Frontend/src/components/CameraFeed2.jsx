import React, { useEffect, useRef } from 'react';
import Hls from 'hls.js';

export default function CameraFeed ({
    videoRef,
    isConnected,
    error,
    streamUrl,
    isRecording
}) {
    const hlsRef = useRef(null);
    const videoElement = videoRef || useRef(null);

    useEffect(() => {
        // Cleanup previous HLS instance
        if (hlsRef.current) {
            hlsRef.current.destroy();
            hlsRef.current = null;
        }

        if (!streamUrl || !videoElement.current) {
            return;
        }

        const video = videoElement.current;

        // Checking if HLS is supporting
        if (Hls.isSupported()) {
            const hls = new Hls({
                enableWorker: true,
                lowLatencyMode: true,
                backbufferLength: 3,
                maxBufferLength: 10,
                maxMaxBufferLength: 20,
                liveSyncDurationCount: 2,
                liveMaxLatencyDurationCount: 4,
                enableLowLatencyMode: true,
                lowLatencyLive: true,
                startPosition: -1,
                debug: false
            });

            hls.loadSource(streamUrl);
            hls.attachMedia(video);
            console.log("something wrong here")
            hls.on(Hls.Events.MANIFEST_PARSED, () => {
                video.play().catch(err => {
                    console.warn('Auto-play prevented:', err);
                });
            });

            hls.on(Hls.Events.ERROR, (event, data) => {
                if (data.fatal) {
                    switch (data.type) {
                        case Hls.ErrorTypes.NETWORK_ERROR:
                            console.log('HLS network error, trying to recover...');
                            hls.startLoad();
                            break;
                        case Hls.ErrorTypes.MEDIA_ERROR:
                            console.log('HLS media error, trying to recover...');
                            hls.recoverMediaError();
                            break;
                        default:
                            console.error('HLS fatal error:', data);
                            break;
                    }
                }
            });

            hlsRef.current = hls;

            return () => {
                if (hlsRef.current) {
                    hlsRef.current.destroy();
                    hlsRef.current = null;
                }
            };
        }
        // For Safari (native HLS support)
        else if (video.canPlayType('application/vnd.apple.mpegurl')) {
            video.src = streamUrl;
            video.addEventListener('loadedmetadata', () => {
                video.play().catch(err => {
                    console.warn('Auto-play prevented:', err);
                });
            });

            return () => {
                video.removeEventListener('loadedmetadata', () => { });
                video.src = '';
            };
        } else {
            console.error('HLS not supported in this browser');
        }
    }, [streamUrl, videoElement]);

    return (
        <div className="relative bg-black rounded-xl overflow-hidden aspect-video min-h-100">
            <video
                ref={videoElement}
                className="w-full h-full object-cover"
                autoPlay
                playsInline
                muted
            />

            {!isConnected && !error && (
                <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/70 text-white">
                    <div className="w-10 h-10 border-4 border-white/30 border-t-green-500 rounded-full animate-spin mb-4"></div>
                    <p>Connecting to camera...</p>
                </div>
            )}

            {error && (
                <div className="absolute inset-0 flex flex-col items-center justify-center bg-red-600/80 text-white">
                    <p className="text-xl mb-2">⚠️ {error}</p>
                    <button className="mt-4 px-6 py-2 bg-white text-gray-800 rounded-lg font-semibold hover:bg-gray-100 transition">
                        Retry
                    </button>
                </div>
            )}

            {isRecording && (
                <div className="absolute top-4 right-4 bg-red-500/90 text-white px-4 py-2 rounded-full flex items-center gap-2 font-bold animate-pulse">
                    <span className="w-2.5 h-2.5 bg-white rounded-full animate-blink"></span>
                    RECORDING
                </div>
            )}

            <div className="absolute bottom-4 left-4 flex gap-4 text-white text-sm bg-black/50 px-3 py-1.5 rounded-full">
                <span>1080p</span>
                <span>30 FPS</span>
            </div>
        </div>
    );
};
