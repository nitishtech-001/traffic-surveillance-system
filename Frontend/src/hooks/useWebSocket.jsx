import { useState, useEffect, useCallback, useRef } from 'react';

export const useWebSocket = (cameraId = null) => {
    const [isConnected, setIsConnected] = useState(false);
    const [lastMessage, setLastMessage] = useState(null);
    const [error, setError] = useState(null);
    const wsRef = useRef(null);
    const reconnectAttempts = useRef(0);
    const maxReconnectAttempts = 5;
    const reconnectDelay = 3000;

    const connect = useCallback((cameraIdParam = null) => {
        const targetCameraId = cameraIdParam || cameraId;
        if (!targetCameraId) {
            console.warn('No camera ID provided for WebSocket connection');
            return;
        }

        // Close existing connection
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }

        const wsUrl = `${import.meta.env.VITE_APP_WS_URL || 'ws://localhost:8000'}/api/ws/${targetCameraId}`;

        try {
            const ws = new WebSocket(wsUrl);
            wsRef.current = ws;

            ws.onopen = () => {
                console.log(`WebSocket connected for camera ${targetCameraId}`);
                setIsConnected(true);
                setError(null);
                reconnectAttempts.current = 0;
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    setLastMessage(data);
                } catch (error) {
                    console.error('WebSocket message parse error:', error);
                }
            };

            ws.onclose = (event) => {
                console.log(`WebSocket disconnected for camera ${targetCameraId}`, event);
                setIsConnected(false);

                // Attempt reconnect
                if (reconnectAttempts.current < maxReconnectAttempts) {
                    reconnectAttempts.current++;
                    const delay = reconnectDelay * reconnectAttempts.current;
                    console.log(`Reconnecting in ${delay}ms... (${reconnectAttempts.current}/${maxReconnectAttempts})`);
                    setTimeout(() => {
                        connect(targetCameraId);
                    }, delay);
                } else {
                    setError('Max reconnect attempts reached');
                }
            };

            ws.onerror = (event) => {
                console.error('WebSocket error:', event);
                setError('WebSocket connection error');
            };

        } catch (error) {
            console.error('WebSocket connection error:', error);
            setError(error.message);
        }
    }, [cameraId]);

    const disconnect = useCallback(() => {
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
            setIsConnected(false);
            reconnectAttempts.current = 0;
        }
    }, []);

    const sendMessage = useCallback((data) => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(data));
            return true;
        }
        console.warn('WebSocket not connected, message not sent');
        return false;
    }, []);

    // Auto-connect when cameraId changes
    useEffect(() => {
        if (cameraId) {
            connect(cameraId);
        }
        return () => {
            disconnect();
        };
    }, [cameraId, connect, disconnect]);

    return {
        isConnected,
        lastMessage,
        error,
        connect,
        disconnect,
        sendMessage,
        reconnectAttempts: reconnectAttempts.current
    };
};