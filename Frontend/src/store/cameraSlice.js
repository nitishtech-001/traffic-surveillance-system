import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../services/api';

// Async thunks
export const fetchCameras = createAsyncThunk(
    'camera/fetchCameras',
    async () => {
        const response = await api.get('/api/cameras/list');
        return response.data;
    }
);

export const addCamera = createAsyncThunk(
    'camera/addCamera',
    async (cameraData) => {
        const response = await api.post('/api/cameras/add', cameraData);
        return response.data;
    }
);

export const connectCamera = createAsyncThunk(
    'camera/connectCamera',
    async (cameraId) => {
        const response = await api.post(`/api/cameras/${cameraId}/connect`);
        return { cameraId, data: response.data };
    }
);

export const disconnectCamera = createAsyncThunk(
    'camera/disconnectCamera',
    async (cameraId) => {
        await api.post(`/api/cameras/${cameraId}/disconnect`);
        return cameraId;
    }
);

const initialState = {
    cameras: [],
    currentCamera: null,
    isConnected: false,
    loading: false,
    error: null,
    streamUrl: null
};

const cameraSlice = createSlice({
    name: 'camera',
    initialState,
    reducers: {
        setCurrentCamera: (state, action) => {
            state.currentCamera = action.payload;
        },
        setStreamUrl: (state, action) => {
            state.streamUrl = action.payload;
        },
        clearError: (state) => {
            state.error = null;
        }
    },
    extraReducers: (builder) => {
        builder
            // Fetch cameras
            .addCase(fetchCameras.pending, (state) => {
                state.loading = true;
            })
            .addCase(fetchCameras.fulfilled, (state, action) => {
                state.loading = false;
                state.cameras = action.payload;
            })
            .addCase(fetchCameras.rejected, (state, action) => {
                state.loading = false;
                state.error = action.error.message;
            })
            // Connect camera
            .addCase(connectCamera.fulfilled, (state, action) => {
                state.isConnected = true;
                state.currentCamera = action.payload.cameraId;
                state.error = null;
            })
            .addCase(connectCamera.rejected, (state, action) => {
                state.isConnected = false;
                state.error = action.error.message;
            })
            // Disconnect camera
            .addCase(disconnectCamera.fulfilled, (state, action) => {
                state.isConnected = false;
                if (state.currentCamera === action.payload) {
                    state.currentCamera = null;
                }
            });
    }
});

export const { setCurrentCamera, setStreamUrl, clearError } = cameraSlice.actions;
export default cameraSlice.reducer;