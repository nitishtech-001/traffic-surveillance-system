import { useWebRTC } from '../hooks/useWebRTC';
import { useCamera } from '../hooks/useCamera';
import { useAgents } from '../hooks/useAgents';
import { useState } from 'react';
import { toast } from 'react-toastify';

const input_custom_style = `rounded-xl border border-slate-200 bg-slate-50 px-2 py-2.5 text-sm text-slate-700 outline-none transition focus:border-sky-400 focus:ring-2 focus:ring-sky-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100 dark:focus:border-sky-500 dark:focus:ring-sky-500/20 w-40`

export default function AnalysisResults() {
  const results = useWebRTC((s) => s.results)
  const currentCamera = useCamera((s)=>s.currentCamera)
  const isProcessing = useAgents((s)=>s.isProcessing)
  const [lostVahicle, setLostVehicle] = useState({}) // {vehicleNumber: ownerename}
  const [foundVehicle, setFoundVehicle] = useState([])

  const handleLostVehicleEntry = (e)=>{
    e.preventDefault()
    console.log(e)
    const owenereName = e.target[0].value
    const vehicleNumber = e.target[1].value.toUpperCase()

    if(!owenereName || !vehicleNumber){
      toast.warning("All field required!")
      return
    }

    if(vehicleNumber in lostVahicle){
      const res = confirm("Vehicle Number already exist what to update")
      if(!res){
        e.target[0].value = ""
        e.target[1].value = ""
        return
      }
    }

    setLostVehicle((prev)=> ({...prev, [vehicleNumber]:owenereName, "found": false}))
    e.target[0].value = ""
    e.target[1].value = ""
    toast.success(`Lost vehicle details saved ${owenereName}: ${vehicleNumber}`)
  }
  
  // console.log(results)
  console.log(foundVehicle)

  if (!results || results?.success !== true) {
    return (
      <div>
        <div className='border border-slate-200/80 bg-white/80 p-5 shadow-[0_20px_50px_-28px_rgba(15,23,42,0.35)] backdrop-blur-xl dark:border-slate-800 dark:bg-slate-900/80 rounded-lg mb-5'>
          <h3 className='text-lg font-bold text-slate-900 dark:text-white'>Add Lost Vehicle Number</h3>
          <form onSubmit={(e) => handleLostVehicleEntry(e)} className='flex justify-evenly' >
            <input type="text" placeholder='Nitish Kumar' className={`${input_custom_style} capitalize`} />
            <input type="alphanum" pattern="[a-zA-Z0-9]+" placeholder='JH10KL7868' title="Only alphanumeric value without space" className={`${input_custom_style} uppercase`} />
            <button type='submit' className='border-2 rounded-lg p-1 bg-sky-500 cursor-pointer'>Add</button>
          </form>
        </div>

      <div className="rounded-[28px] border border-slate-200/80 bg-white/80 p-5 shadow-[0_20px_50px_-28px_rgba(15,23,42,0.35)] backdrop-blur-xl dark:border-slate-800 dark:bg-slate-900/80">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Analysis Results</h3>
          <span className="rounded-full bg-slate-100 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-500 dark:bg-slate-800 dark:text-slate-400">
            {currentCamera ? 'Live' : 'Idle'}
          </span>
        </div>
        <div className="flex h-48 flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-slate-50 text-center dark:border-slate-700 dark:bg-slate-800/60">
          <p className="text-lg font-semibold text-slate-700 dark:text-slate-200">No results yet</p>
          <span className="mt-1 text-sm text-slate-500 dark:text-slate-400">Capture a frame to start analysis</span>
        </div>
      </div>
      </div>
    );
  }

  return (
    <div>

      

      <div className='max-h-155 border border-slate-200/80 bg-white/80 p-5 shadow-[0_20px_50px_-28px_rgba(15,23,42,0.35)] backdrop-blur-xl dark:border-slate-800 dark:bg-slate-900/80 rounded-lg'>

      <div className="mb-4 flex items-center justify-between gap-2">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Analysis Results</h3>
        <span className="rounded-full bg-sky-100 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-sky-700 dark:bg-sky-500/10 dark:text-sky-300">
          Latest
        </span>
      </div>

      {isProcessing && (
        <div className="mb-4 flex items-center gap-3 rounded-2xl border border-amber-200 bg-amber-50 p-3 text-sm font-medium text-amber-700 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-300">
          <div className="h-5 w-5 animate-spin rounded-full border-2 border-amber-500 border-t-transparent" />
          Processing frame...
        </div>
      )}

      <div className="space-y-3 rounded-2xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-800/60">
        <div className="text-[11px] font-medium uppercase tracking-[0.2em] text-slate-400 dark:text-slate-500">
          {new Date(results?.timestamp).toLocaleString()}
        </div>

        {results && results?.agent_results && (
          <div className="space-y-3">
            {Object.entries(results?.agent_results).map(([agentId, agentInfo]) => {
              const agentResult = agentInfo?.result || {}

              if (agentId === 'object-detection' && agentInfo.success) {

                return (
                  <div key={agentId} className="rounded-2xl border border-emerald-200 bg-emerald-50 p-3 dark:border-emerald-500/30 dark:bg-emerald-500/10">
                    <div className="flex items-center justify-between gap-2">
                      <h4 className="text-sm font-semibold capitalize text-emerald-700 dark:text-emerald-300">
                        {agentInfo.agent_name}
                      </h4>
                      <span className="rounded-full bg-emerald-600 px-2 py-1 text-[10px] font-semibold text-white">
                        {agentResult.total_objects || 0} objects
                      </span>
                    </div>
                    <div className="mt-2 h-15 overflow-y-auto pr-1 scrollbar-thin space-y-1.5 ">
                      {Object.entries(agentResult?.object_counts).map(([class_name, class_count]) => 
                        (
                        <div key={class_name} className="flex items-center justify-between gap-3 text-sm text-slate-700 dark:text-slate-200">
                          <span>{class_name}</span>
                          <span>{class_count}</span>
                        </div>
                        )
                      )}

                    </div>
                  </div>
                );
              }

              if (agentId === 'license-plate' && agentInfo?.success) {
                const plates = agentResult?.plates || [];

                return (
                  <div key={agentId} className="rounded-2xl border border-sky-200 bg-sky-50 p-3 dark:border-sky-500/30 dark:bg-sky-500/10">
                    <div className="flex items-center justify-between gap-2">
                      <h4 className="text-sm font-semibold capitalize text-sky-700 dark:text-sky-300">
                        {agentInfo.agent_name}
                      </h4>
                      <span className="rounded-full bg-sky-600 px-2 py-1 text-[10px] font-semibold text-white">
                        {plates.length} plates
                      </span>
                    </div>
                    <div className="mt-2 h-15 overflow-y-auto pr-1 scrollbar-thin space-y-1.5">
                      {plates.map((plate, idx) => (
                        <div key={idx} className="flex items-center justify-between gap-3 text-sm">
                          <span className="font-mono font-bold text-sky-800 dark:text-sky-200">{plate.plate_text}</span>
                          {plate in lostVahicle && !foundVehicle.includes(plate)? setFoundVehicle((prev)=>([...prev, plate])):""}
                          <span className="text-slate-500 dark:text-slate-400">{(plate.confidence * 100).toFixed(1)}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              }

              return (
                <div key={agentId} className="rounded-2xl border border-slate-200 bg-white p-3 dark:border-slate-700 dark:bg-slate-900">
                  <h4 className="text-sm font-semibold capitalize text-slate-700 dark:text-slate-200">
                    {agentId.replace('-', ' ')}
                  </h4>
                  <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Processing complete</p>
                </div>
              );
            })}

          </div>
        )}

        {results.total_processing_times && (
          <div className="mt-4 border-t border-slate-200 pt-3 text-[11px] text-slate-500 dark:border-slate-700 dark:text-slate-400">
            <div className="flex items-center justify-between gap-2">
              <span>Processing Time: {results.total_processing_time?.toFixed(2)}s</span>
              <span>Active Agents: {results.active_agents?.length || 0}</span>
            </div>
          </div>
        )}
      </div>

      <div className="text-[11px] font-medium uppercase tracking-[0.2em] text-slate-400 dark:text-slate-500">
        Active Agents : {results?.active_agents}
      </div>

      {results.length > 1 && (
        <div className="mt-3 text-center text-[11px] uppercase tracking-[0.2em] text-slate-400 dark:text-slate-500">
          Showing latest of {results.length} results
        </div>
      )}

      {foundVehicle.map( (vehicleNo) =>(
        <div>
          <span>Ownere Name : {lostVahicle[vehicleNo]}</span>
          <span>Vechil No : {vehicleNo}</span>
        </div>
        ))
      }

    </div>
    </div>
  );
}
