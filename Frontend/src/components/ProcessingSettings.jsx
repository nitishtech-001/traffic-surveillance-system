import  { useState, useRef, useEffect } from 'react';
import { useCamera } from '../hooks/useCamera.js';
import { useCameraStream } from '../hooks/useCameraStream.js';
import { toast } from 'react-toastify';

export default function ProcessingSettings() {
  const currentCamera = useCamera((state)=>state.currentCamera)
  const interval = useCameraStream((s)=>s.interval)
  const conf = useCameraStream((s)=>s.conf)
  const updateConfiguration = useCameraStream((s)=>s.updateConfiguration)
  const record = useCameraStream((s)=>s.record)
  const [currentProcess, setCurrentProcess] = useState({"interval":interval,"conf":conf})
  const timerRef = useRef(null)

  useEffect(()=>{
    setCurrentProcess({ "interval": interval, "conf": conf })
  },[interval,conf])

  const handleChange = (key, value) => {
    if(!currentCamera){
      toast.warning("Select the camera first.",{toastId:"cameranotfound"})
      return
    }
    setCurrentProcess((prev)=>({...prev,[key]:value}))
    // Clear the previous timer as long as the user keeps slidingd
    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }
    timerRef.current = setTimeout(async () => {
      const configuration = {
        [key]: value
      }
      await updateConfiguration(currentCamera.id, configuration )
    },1000)
  };
  
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
            <span>{currentProcess.interval} ms</span>
          </div>
          <input
            type="range"
            min="100"
            max="5000"
            step="100"
            value={currentProcess.interval}
            onChange={(e) => handleChange('interval', parseFloat(e.target.value))}
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
            <span>{currentProcess.conf*100} %</span>
          </div>
          <input
            type="range"
            min="10"
            max="95"
            step="0.5"
            value={currentProcess.conf*100}
            onChange={(e) => handleChange('conf', parseFloat(e.target.value)/100)}
            className="h-2 w-full cursor-pointer appearance-none rounded-full bg-slate-200 accent-indigo-600 dark:bg-slate-700"
          />
          <div className="mt-2 flex justify-between text-[11px] text-slate-400">
            <span>10%</span>
            <span>95%</span>
          </div>
        </div>

      </div>

      <div className="flex flex-wrap items-center justify-between gap-2 border-t border-slate-200 pt-4 text-xs text-slate-500 dark:border-slate-700 dark:text-slate-400">
        <span className="inline-flex items-center gap-2">
          <span className="text-emerald-500">⚡</span>
          {currentCamera ? 'Real-time ON' : 'Real-time OFF'}
        </span>
        <span className="inline-flex items-center gap-2">
          <span className="text-violet-500">💾</span>
          {record===true ? 'Saving ON' : 'Saving OFF'}
        </span>
      </div>
    </div>
  );
}

