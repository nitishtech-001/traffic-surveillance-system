import React, { useState } from 'react';
import { useCamera } from '../hooks/useCamera.js';
export default function ProcessingSettings({ settings, onSettingsChange }) {
  const {currentCamera} = useCamera()

  const [localSettings, setLocalSettings] = useState({
    processingInterval: settings?.processingInterval || 1000,
    confidenceThreshold: settings?.confidenceThreshold || 0.5,
    useLocalProcessing: settings?.useLocalProcessing || false,
    realtimeAnalysis: settings?.realtimeAnalysis || true,
    saveResults: settings?.saveResults || true
  });

  const handleChange = (key, value) => {
    const newSettings = { ...localSettings, [key]: value };
    setLocalSettings(newSettings);
    if (onSettingsChange) {
      onSettingsChange(newSettings);
    }
  };
  console.log("Current camers ", currentCamera)
  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-sky-600 dark:text-sky-400">
            Controls
          </p>
          <h3 className="mt-1 text-xl font-semibold text-slate-900 dark:text-white">
            Processing Settings
          </h3>
        </div>
        <span className="inline-flex items-center rounded-full border border-slate-200 bg-slate-100 px-2.5 py-1 text-[11px] font-medium text-slate-600 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300">
          Live tuning
        </span>
      </div>

      <div className="space-y-5">
        <div>
          <div className="mb-2 flex items-center justify-between text-sm">
            <label className="font-medium text-slate-700 dark:text-slate-200">Processing Interval</label>
            <span className="text-slate-500 dark:text-slate-400">{localSettings.processingInterval}ms</span>
          </div>
          <input
            type="range"
            min="100"
            max="5000"
            step="100"
            value={localSettings.processingInterval}
            onChange={(e) => handleChange('processingInterval', parseInt(e.target.value))}
            className="h-2 w-full cursor-pointer appearance-none rounded-full bg-slate-200 accent-sky-600 dark:bg-slate-700"
          />
          <div className="mt-2 flex justify-between text-[11px] text-slate-400">
            <span>100ms</span>
            <span>5s</span>
          </div>
        </div>

        <div>
          <div className="mb-2 flex items-center justify-between text-sm">
            <label className="font-medium text-slate-700 dark:text-slate-200">Confidence Threshold</label>
            <span className="text-slate-500 dark:text-slate-400">{(localSettings.confidenceThreshold * 100).toFixed(0)}%</span>
          </div>
          <input
            type="range"
            min="0.1"
            max="0.95"
            step="0.05"
            value={localSettings.confidenceThreshold}
            onChange={(e) => handleChange('confidenceThreshold', parseFloat(e.target.value))}
            className="h-2 w-full cursor-pointer appearance-none rounded-full bg-slate-200 accent-indigo-600 dark:bg-slate-700"
          />
          <div className="mt-2 flex justify-between text-[11px] text-slate-400">
            <span>10%</span>
            <span>95%</span>
          </div>
        </div>

        <div className="grid gap-3 pt-2 sm:grid-cols-3">
          <label className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm text-slate-700 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200">
            <input
              type="checkbox"
              checked={localSettings.realtimeAnalysis}
              onChange={(e) => handleChange('realtimeAnalysis', e.target.checked)}
              className="h-4 w-4 rounded border-slate-300 text-sky-600 focus:ring-sky-500 dark:border-slate-600"
            />
            Real-time
          </label>

          <label className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm text-slate-700 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200">
            <input
              type="checkbox"
              checked={localSettings.saveResults}
              onChange={(e) => handleChange('saveResults', e.target.checked)}
              className="h-4 w-4 rounded border-slate-300 text-sky-600 focus:ring-sky-500 dark:border-slate-600"
            />
            Save results
          </label>

          <label className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm text-slate-700 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200">
            <input
              type="checkbox"
              checked={localSettings.useLocalProcessing}
              onChange={(e) => handleChange('useLocalProcessing', e.target.checked)}
              className="h-4 w-4 rounded border-slate-300 text-sky-600 focus:ring-sky-500 dark:border-slate-600"
            />
            Local mode
          </label>
        </div>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-2 border-t border-slate-200 pt-4 text-xs text-slate-500 dark:border-slate-700 dark:text-slate-400">
        <span className="inline-flex items-center gap-2">
          <span className="text-emerald-500">⚡</span>
          {localSettings.realtimeAnalysis ? 'Real-time ON' : 'Real-time OFF'}
        </span>
        <span className="inline-flex items-center gap-2">
          <span className="text-violet-500">💾</span>
          {localSettings.saveResults ? 'Saving ON' : 'Saving OFF'}
        </span>
      </div>
    </div>
  );
}

