import { useState, useRef, useCallback } from 'react';
import { connectCamera, disconnectCamera, startStream, stopStream, getFrame } from '../services/api';

export const useCameraStream = () => {
    const [isConnected, setIsConnected] = useState(false);
    const [error, setError] = useState(null);
    const [streamUrl, setStreamUrl] = useState(null);
    const videoRef = useRef(null);
    const canvasRef = useRef(document.createElement('canvas'));

    const connectCamera = useCallback(async (cameraId) => {
        try {
            const response = await connectCamera(cameraId);
            setIsConnected(true);
            setError(null);
            return true;
        } catch (err) {
            setError(err.message);
            setIsConnected(false);
            return false;
        }
    }, []);

    const disconnectCamera = useCallback(async (cameraId) => {
        try {
            await disconnectCamera(cameraId);
            setIsConnected(false);
            setStreamUrl(null);
            return true;
        } catch (err) {
            setError(err.message);
            return false;
        }
    }, []);

    const startHLSStream = useCallback(async (cameraId) => {
        try {
            
            const response = await startStream(cameraId);
            const url = response.data.hls_url;
            setStreamUrl(`http://localhost:8000${url}`);
            console.log(`http://localhost:8000${url}`)
            return true;
        } catch (err) {
            setError(err.message);
            return false;
        }
    }, []);

    const stopHLSStream = useCallback(async (cameraId) => {
        try {
            await stopStream(cameraId);
            setStreamUrl(null);
            return true;
        } catch (err) {
            setError(err.message);
            return false;
        }
    }, []);

    const captureFrame = useCallback(() => {
        if (!videoRef.current) return null;

        const video = videoRef.current;
        const canvas = canvasRef.current;
        canvas.width = video.videoWidth || 1280;
        canvas.height = video.videoHeight || 720;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0);
        return canvas.toDataURL('image/jpeg', 0.8);
    }, []);

    return {
        videoRef,
        isConnected,
        error,
        streamUrl,
        connectCamera,
        disconnectCamera,
        startHLSStream,
        stopHLSStream,
        captureFrame
    };
};