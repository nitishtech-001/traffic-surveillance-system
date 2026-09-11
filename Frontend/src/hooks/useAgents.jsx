import { useState, useCallback } from 'react';
import { getAgents, activateAgent, deactivateAgent, processFrame, getResults } from '../services/api';

export const useAgents = () => {
    const [agents, setAgents] = useState([
        { id: 'object-detection', name: 'Object Detection', icon: '🔍' },
        { id: 'face-detection', name: 'Face Detection', icon: '👤'  },
        { id: 'license-plate', name: 'License Plate', icon: '🚗' },
        { id: 'motion-tracking', name: 'Motion Tracking', icon: '🏞️' },
        { id: 'text-recognition', name: 'Text Recognition', icon: '📝' }
    ]);

    const [agentStatus, setAgentStatus] = useState([]);
    const [results, setResults] = useState([]);
    const [isProcessing, setIsProcessing] = useState(false);
    const [continuousInterval, setContinuousInterval] = useState(null);

    const loadAgents = useCallback(async () => {
        try {
            const response = await getAgents();
            setAgentStatus(response.data || []);
        } catch (error) {
            console.error('Error loading agents:', error);
        }
    }, []);

    const activateAgent = useCallback(async (agentId) => {
        try {
            await activateAgent(agentId);
            await loadAgents();
            return true;
        } catch (error) {
            console.error('Error activating agent:', error);
            return false;
        }
    }, [loadAgents]);

    const deactivateAgent = useCallback(async (agentId) => {
        try {
            await deactivateAgent(agentId);
            await loadAgents();
            return true;
        } catch (error) {
            console.error('Error deactivating agent:', error);
            return false;
        }
    }, [loadAgents]);

    const processFrame = useCallback(async (frame, cameraId, selectedAgents) => {
        setIsProcessing(true);
        try {
            const response = await processFrame(frame, cameraId);
            const result = response.data;

            setResults(prev => [{
                id: Date.now(),
                timestamp: new Date().toISOString(),
                cameraId,
                result
            }, ...prev].slice(0, 100));

            return result;
        } catch (error) {
            console.error('Error processing frame:', error);
            return null;
        } finally {
            setIsProcessing(false);
        }
    }, []);

    const startContinuousProcessing = useCallback((captureFrame, cameraId, selectedAgents, interval) => {
        if (continuousInterval) {
            clearInterval(continuousInterval);
        }

        const newInterval = setInterval(async () => {
            const frame = captureFrame();
            if (frame) {
                await processFrame(frame, cameraId, selectedAgents);
            }
        }, interval);

        setContinuousInterval(newInterval);
    }, [continuousInterval, processFrame]);

    const stopContinuousProcessing = useCallback(() => {
        if (continuousInterval) {
            clearInterval(continuousInterval);
            setContinuousInterval(null);
        }
    }, [continuousInterval]);

    const getResults = useCallback(async (cameraId) => {
        try {
            const response = await getResults(cameraId);
            return response.data;
        } catch (error) {
            console.error('Error getting results:', error);
            return [];
        }
    }, []);

    return {
        agents,
        agentStatus,
        results,
        isProcessing,
        loadAgents,
        activateAgent,
        deactivateAgent,
        processFrame,
        startContinuousProcessing,
        stopContinuousProcessing,
        getResults
    };
};