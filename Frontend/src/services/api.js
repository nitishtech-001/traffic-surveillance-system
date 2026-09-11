import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Camera endpoints
export const getCameras = () => api.get('/api/cameras/list');
export const addCamera = (camera) => api.post('/api/cameras/add', camera);
export const connectCamera = (cameraId) => api.post(`/api/cameras/${cameraId}/connect`);
export const disconnectCamera = (cameraId) => api.post(`/api/cameras/${cameraId}/disconnect`);

// Stream endpoints
export const startStream = (cameraId) => api.post(`/api/streams/${cameraId}/start`);
export const stopStream = (cameraId) => api.post(`/api/streams/${cameraId}/stop`);
export const getStreamUrl = (cameraId) => api.get(`/api/streams/${cameraId}/playlist.m3u8`);

// Agent endpoints
export const getAgents = () => api.get('/api/agents/list');
export const activateAgent = (agentId) => api.post(`/api/agents/${agentId}/activate`);
export const deactivateAgent = (agentId) => api.post(`/api/agents/${agentId}/deactivate`);

// Processing endpoints
export const processFrame = (frameData, cameraId) => {
    return api.post('/api/process/frame', {
        camera_id: cameraId,
        frame: frameData
    });
};

// frame endpoints
export const getFrame = (cameraId) => api.get(`/api/cameras/${cameraId}/frame`);
export const captureFrame = (cameraId) => api.post(`/api/cameras/${cameraId}/capture`);

export const getResults = (cameraId, limit = 10) => {
    return api.get(`/api/process/results/${cameraId}?limit=${limit}`);
};

export default api;