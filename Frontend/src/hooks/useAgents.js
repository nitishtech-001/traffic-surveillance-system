import { create } from 'zustand';
import { axiosInstance } from '../services/axiosInstance.js';

export const useAgents = create((set, get) => {
    // Use a private module-scoped variable for the interval ID to avoid re-renders
    let continuousIntervalId = null;

    return {
        // Hardcoded static agent items
        agents: [
            { id: 'object-detection', name: 'Object Detection', icon: '🔍' },
            { id: 'face-detection', name: 'Face Detection', icon: '👤' },
            { id: 'license-plate', name: 'License Plate', icon: '🚗' },
            { id: 'motion-tracking', name: 'Motion Tracking', icon: '🏞️' },
            { id: 'text-recognition', name: 'Text Recognition', icon: '📝' }
        ],

        // Dynamic Application States
        agentStatus: [],
        results: [],
        isProcessing: false,
        isContinuousRunning: false,

        // HTTP Action: Fetch all agent statuses
        loadAgents: async () => {
            try {
                const response = await axiosInstance.get('/api/agents'); // Adjust endpoints if necessary
                set({ agentStatus: response.data || [] });
            } catch (error) {
                console.error('Error loading agents:', error);
            }
        },

        // HTTP Action: Activate specific agent
        activateAgent: async (agentId) => {
            try {
                await axiosInstance.post(`/api/agents/${agentId}/activate`);
                await get().loadAgents(); // Reload statuses
                return true;
            } catch (error) {
                console.error('Error activating agent:', error);
                return false;
            }
        },

        // HTTP Action: Deactivate specific agent
        deactivateAgent: async (agentId) => {
            try {
                await axiosInstance.post(`/api/agents/${agentId}/deactivate`);
                await get().loadAgents(); // Reload statuses
                return true;
            } catch (error) {
                console.error('Error deactivating agent:', error);
                return false;
            }
        },

        // HTTP Action: Upload a frame for inference processing
        processFrame: async (frame, cameraId) => {
            set({ isProcessing: true });
            try {
                const response = await axiosInstance.post('/api/process-frame', { frame, cameraId });
                const result = response.data;

                set((state) => ({
                    results: [
                        {
                            id: Date.now(),
                            timestamp: new Date().toISOString(),
                            cameraId,
                            result
                        },
                        ...state.results
                    ].slice(0, 100) // Keep the latest 100 entries
                }));

                return result;
            } catch (error) {
                console.error('Error processing frame:', error);
                return null;
            } finally {
                set({ isProcessing: false });
            }
        },

        // Continuous Frame Processing Controls
        startContinuousProcessing: (captureFrame, cameraId, intervalMs) => {
            // Clear any pre-existing timer loops
            if (continuousIntervalId) {
                clearInterval(continuousIntervalId);
            }

            set({ isContinuousRunning: true });

            continuousIntervalId = setInterval(async () => {
                const frame = captureFrame();
                if (frame) {
                    await get().processFrame(frame, cameraId);
                }
            }, intervalMs);
        },

        stopContinuousProcessing: () => {
            if (continuousIntervalId) {
                clearInterval(continuousIntervalId);
                continuousIntervalId = null;
            }
            set({ isContinuousRunning: false });
        },

        // HTTP Action: Retrieve historic analytical logs for a camera
        getResults: async (cameraId) => {
            try {
                const response = await axiosInstance.get(`/api/results/${cameraId}`);
                return response.data;
            } catch (error) {
                console.error('Error getting results:', error);
                return [];
            }
        }
    };
});
