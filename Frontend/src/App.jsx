import React, { useState, useEffect } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import CameraFeed from './components/CameraFeed.jsx';
import CameraSelector from './components/CameraSelector.jsx';
import AgentPanel from './components/AgentPanel.jsx';
import AnalysisResults from './components/AnalysisResult.jsx';
import VideoControls from './components/VideoControls.jsx';
import ProcessingSettings from './components/ProcessingSettings.jsx';
import Header from './components/Header.jsx';

import { useCameraStream } from './hooks/useCameraStream.jsx';
import { useWebSocket } from './hooks/useWebSocket.jsx';
import { useAgents } from './hooks/useAgents.jsx';
// import LiveStream from "./components/VideoStream.jsx"

import { useTheme } from './services/useThemeStore';

export default function App() {
  const theme = useTheme((state)=> state.theme)

  const isDarkMode = theme ==="dark"?true:false;


  const [selectedCamera, setSelectedCamera] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [processingMode, setProcessingMode] = useState('single');
  const [selectedAgents, setSelectedAgents] = useState(['object-detection']);
  const [settings, setSettings] = useState({
    processingInterval: 1000,
    confidenceThreshold: 0.5,
    useLocalProcessing: false
  });

  const {
    videoRef,
    isConnected,
    error: cameraError,
    captureFrame,
    connectCamera,
    disconnectCamera,
    startHLSStream,
    stopHLSStream,
    streamUrl
  } = useCameraStream();

  const {
    agents,
    agentStatus,
    activateAgent,
    deactivateAgent,
    processFrame,
    startContinuousProcessing,
    stopContinuousProcessing,
    results,
    isProcessing
  } = useAgents();

  const {
    connect: connectWebSocket,
    disconnect: disconnectWebSocket,
    isConnected: wsConnected
  } = useWebSocket();

  const handleCameraSelect = async (cameraId) => {
    if (selectedCamera) {
      await disconnectCamera(selectedCamera);
      stopHLSStream(selectedCamera);
    }

    setSelectedCamera(cameraId);

    if (cameraId) {
      const connected = await connectCamera(cameraId);
      if (connected) {
        toast.success('Camera connected successfully!');
        const streamStarted = await startHLSStream(cameraId);
        if (streamStarted) {
          toast.success('Stream started!');
        }
        connectWebSocket(cameraId);
      } else {
        toast.error('Failed to connect camera');
      }
    }
  };

  const handleProcessFrame = async () => {
    if (!selectedCamera || !isConnected) {
      toast.warning('Please connect to a camera first');
      return;
    }

    const frame = captureFrame();
    if (frame) {
      const result = await processFrame(frame, selectedCamera, selectedAgents);
      if (result) {
        toast.success('Frame processed successfully!');
      }
    }
  };

  const toggleContinuousProcessing = () => {
    if (processingMode === 'single') {
      if (!selectedCamera || !isConnected) {
        toast.warning('Please connect to a camera first');
        return;
      }

      startContinuousProcessing(
        captureFrame,
        selectedCamera,
        selectedAgents,
        settings.processingInterval
      );
      setProcessingMode('continuous');
      toast.info('Continuous processing started');
    } else {
      stopContinuousProcessing();
      setProcessingMode('single');
      toast.info('Continuous processing stopped');
    }
  };

  const handleAgentToggle = (agentId) => {
    if (selectedAgents.includes(agentId)) {
      setSelectedAgents(selectedAgents.filter((id) => id !== agentId));
      deactivateAgent(agentId);
    } else {
      setSelectedAgents([...selectedAgents, agentId]);
      activateAgent(agentId);
    }
  };

  return (
    <div className={isDarkMode ? 'dark' : ''}>
      <div className="min-h-screen bg-slate-100 text-slate-900 transition-colors duration-300 dark:bg-slate-950 dark:text-slate-100">
        <div className="mx-auto max-w-7xl px-3 py-4 sm:px-5 lg:px-6">
          <Header />
          <main className="grid gap-5 xl:grid-cols-[minmax(0,1.6fr)_minmax(340px,0.95fr)]">
            <div className="space-y-5">
              <section className="rounded-[28px] border border-slate-200/80 bg-white/80 p-3  dark:border-slate-800 dark:bg-slate-900/80 sm:p-4">
                <CameraFeed
                  videoRef={videoRef}
                  isConnected={isConnected}
                  error={cameraError}
                  streamUrl={streamUrl}
                  isRecording={isRecording}
                />

                <div className="mt-4">
                  <VideoControls
                    isRecording={isRecording}
                    onToggleRecording={() => setIsRecording(!isRecording)}
                    onCaptureFrame={handleProcessFrame}
                    onToggleContinuous={toggleContinuousProcessing}
                    isProcessing={isProcessing}
                    processingMode={processingMode}
                    isConnected={isConnected}
                    selectedCamera={selectedCamera}
                  />
                </div>
              </section>

              <section className="rounded-[28px] border border-slate-200/80 bg-white/80 p-4 dark:border-slate-800 dark:bg-slate-900/80 sm:p-5">
                <ProcessingSettings
                  settings={settings}
                  onSettingsChange={setSettings}
                />
              </section>
            </div>

            <aside className="space-y-5">
              <AgentPanel
                agents={agents}
                agentStatus={agentStatus}
                selectedAgents={selectedAgents}
                onAgentToggle={handleAgentToggle}
              />

              <AnalysisResults
                results={results}
                isProcessing={isProcessing}
                selectedCamera={selectedCamera}
              />
            </aside>
          </main>
          
         
        </div>
      </div>
      {/* SETTIGN THE TOASIFY THEME DYNAMICALLY */}
      <ToastContainer
        position="top-right"
        autoClose={3000}
        // TODO : set the zustand state for dark and light mode
        theme={theme}
        toastClassName="!rounded-xl !shadow-lg"
        className='mt-32'
      />
    </div>
  );
}
