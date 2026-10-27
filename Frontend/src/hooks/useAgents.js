import { create } from 'zustand';
import { axiosInstance } from '../services/axiosInstance.js';
import {toast} from "react-toastify"

export const useAgents = create((set, get) => ({
    // Use a private module-scoped variable for the interval ID to avoid re-renders
    continuousIntervalId : null,

    availableAgents: [
        { id: 'object-detection', name: 'Object Detection', icon: '🔍' },
        // { id: 'face-detection', name: 'Face Detection', icon: '👤' },
        { id: 'license-plate', name: 'License Plate', icon: '🚗' },
        // { id: 'motion-tracking', name: 'Motion Tracking', icon: '🏞️' },
    ],
    // addedAgents: [],
    activeAgents: new Set(),
    agentStatus: {},
    results: [],
    isProcessing: false,
    isContinuousRunning: false,

    // HTTP Action: Activate specific agent
    activateAgent: async (agentId) => {
        try {
            const response = await axiosInstance.post(`/api/agents/${agentId}/activate`);
            if(response.data){
                toast.success(response.data.message)
                const activeAgents = get().activeAgents
                const updateAgents = new Set([...activeAgents,agentId])
                set((s) => ({
                    activeAgents: updateAgents,
                    agentStatus: { ...s.agentStatus, [agentId]: "processing" },
                    isProcessing: true
                }))
                toast.success("Agent is now activated.")
                toast.success("Agent is processing..")
            }else{
                toast.warning("response is empty during activating agents")
            }
        } catch (error) {
            console.error('Error activating agent:', error);
            toast.error("May be server is not running...")
        }
    },

    // HTTP Action: Deactivate specific agent
    deactivateAgent: async (agentId) => {
        try {
            const response = await axiosInstance.post(`/api/agents/${agentId}/deactivate`);
            if (response.data) {
                toast.success(response.data.message)
                const activeAgents = get().activeAgents
                const updateAgents = new Set(activeAgents)
                updateAgents.delete(agentId)
                set((s)=>({
                    activeAgents: updateAgents,
                    agentStatus: {...s.agentStatus, [agentId]: "activate"},
                    isProcessing: false
                }))
                toast.success("Agent is now initialized..")
            } else {
                toast.warning("response is empty during deactivating agents")
            }
        } catch (error) {
            console.error('Error deactivating agent:', error);
            toast.error("May be server is not running...")
        }
    },

    // HTTP Action: Fetch all agent statuses
    loadAgents: async () => {
        try {
            const response = await axiosInstance.get('/api/agents/list');
            if(response.data){
                set({ agentStatus: response.data || {} });
                toast.success("Agents loaded sucessfully!")
            }else{
                toast.warning("Response is empty during agent loads")
            }
        } catch (error) {
            console.error('Error loading agents:', error);
            toast.error("May be server is not running...")
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

}))
