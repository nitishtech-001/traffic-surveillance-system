import React from 'react';
import { FaCamera, FaPause, FaStop, FaSync, FaVideo } from 'react-icons/fa';

export default function VideoControls({
  isRecording,
  onToggleRecording,
  onCaptureFrame,
  onToggleContinuous,
  isProcessing,
  processingMode,
  isConnected,
  selectedCamera
}) {
  console.log(selectedCamera)
  return (
    <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
      <div className="flex flex-wrap items-center gap-3">
        <button
          type="button"
          className={`inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold shadow-sm transition ${isRecording ? 'bg-rose-500 text-white shadow-rose-500/20 hover:bg-rose-600' : 'bg-slate-900 text-white hover:bg-slate-700 dark:bg-slate-700 dark:hover:bg-slate-600'} disabled:cursor-not-allowed disabled:opacity-50`}
          onClick={onToggleRecording}
          disabled={!isConnected}
        >
          {isRecording ? <FaStop /> : <FaVideo />}
          {isRecording ? 'Stop' : 'Record'}
        </button>

        <button
          type="button"
          className="inline-flex items-center gap-2 rounded-xl border border-sky-200 bg-sky-50 px-4 py-2.5 text-sm font-semibold text-sky-700 shadow-sm transition hover:border-sky-300 hover:bg-sky-100 disabled:cursor-not-allowed disabled:opacity-50 dark:border-sky-500/40 dark:bg-sky-500/10 dark:text-sky-300 dark:hover:bg-sky-500/20"
          onClick={onCaptureFrame}
          disabled={!isConnected || isProcessing}
        >
          <FaCamera />
          {isProcessing ? 'Processing...' : 'Capture'}
        </button>

        <button
          type="button"
          className={`inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold shadow-sm transition ${processingMode === 'continuous' ? 'bg-amber-500 text-white shadow-amber-500/20 hover:bg-amber-600' : 'border border-slate-200 bg-white text-slate-700 hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700'} disabled:cursor-not-allowed disabled:opacity-50`}
          onClick={onToggleContinuous}
          disabled={!isConnected}
        >
          {processingMode === 'continuous' ? <FaPause /> : <FaSync />}
          {processingMode === 'continuous' ? 'Stop' : 'Continuous'}
        </button>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <span className={`inline-flex items-center rounded-full border px-3 py-1.5 text-xs font-medium ${isConnected ? 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-500/40 dark:bg-emerald-500/10 dark:text-emerald-300' : 'border-rose-200 bg-rose-50 text-rose-700 dark:border-rose-500/40 dark:bg-rose-500/10 dark:text-rose-300'}`}>
          {isConnected ? '● Online' : '● Offline'}
        </span>

        {isProcessing && (
          <span className="inline-flex items-center gap-2 rounded-full border border-amber-200 bg-amber-50 px-3 py-1.5 text-xs font-medium text-amber-700 dark:border-amber-500/50 dark:bg-amber-500/10 dark:text-amber-300">
            <span className="h-2 w-2 animate-pulse rounded-full bg-amber-500" />
            Processing...
          </span>
        )}

        {selectedCamera && (
          <span className="hidden rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-600 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 sm:inline-flex">
            Camera {selectedCamera}
          </span>
        )}
      </div>
    </div>
  );
}
