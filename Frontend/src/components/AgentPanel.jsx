import {  FaSpinner } from 'react-icons/fa';
import { useAgents } from '../hooks/useAgents';
import { useCamera } from "../hooks/useCamera.js"
import { toast } from 'react-toastify';

export default function AgentPanel() {
  const currentCamera = useCamera((s) => s.currentCamera)
  const availableAgents = useAgents((s) => s.availableAgents)
  const activeAgents = useAgents((s) => s.activeAgents)
  const activateAgent = useAgents((s)=>s.activateAgent)
  const deactivateAgnet = useAgents((s) => s.deactivateAgent)
  const agentStatus = useAgents((s)=>s.agentStatus)


  console.log(agentStatus)

  const activateDeactiveAll = async()=>{
    for( const agent of availableAgents){
      await handleActivateDeactivate(agent.id)
    }
  }

  const handleActivateDeactivate = async (agentId)=> {
    if(!currentCamera || !activeAgents){
      toast.warning("Select the camers first..")
      return 
    }
    
    if(activeAgents.has(agentId)){
      await deactivateAgnet(agentId)
    }else{
      await activateAgent(agentId)
    }

    // add to the selected agents
  }

  return (
    <div className="rounded-[28px] border border-slate-200/80 bg-white/80 p-4 dark:border-slate-800 dark:bg-slate-900/80 sm:p-5">
      <div className="mb-4 flex items-center justify-between gap-2">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-violet-600 dark:text-violet-400">
            AI Stack
          </p>
          <h3 className="mt-1 text-xl font-semibold text-slate-900 dark:text-white">AI Agents</h3>
        </div>
      </div>

      <div className="space-y-3">
        {availableAgents.map((agent) => (
          <div
            key={agent.id}
            className={`flex w-full items-center gap-3 rounded-2xl border p-3 text-left transition ${activeAgents.has(agent.id) ? 'border-sky-200 bg-sky-50 shadow-sm dark:border-sky-500/40 dark:bg-sky-500/10' : 'border-slate-200 bg-slate-50 hover:border-slate-300 hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-800/70 dark:hover:border-slate-600 dark:hover:bg-slate-800'}`}
          >
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-linear-to-br from-slate-900 to-slate-700 text-lg text-white shadow-inner dark:from-slate-700 dark:to-slate-600">
              {agent.icon}
            </div>

            <div className="min-w-0 flex-1">
              <div className="flex items-center justify-between gap-2">
                <span className="truncate text-sm font-semibold text-slate-800 dark:text-slate-100">
                  {agent.name}
                </span>

                <button className={`flex w-22 h-8 items-center justify-center rounded-lg text-xs text-white ${agentStatus[agent.id] === "processing"?"bg-green-500":"bg-sky-500"} cursor-pointer`}
                  onClick={() => handleActivateDeactivate(agent.id)}
                >
                  {agentStatus[agent.id] || "activate"}
                </button>
                
              </div>

              <div className="-mt-1px absolute flex items-center gap-2 text-[11px] text-slate-500 dark:text-slate-400">


                <span className={`h-2.5 w-2.5 rounded-full ${agentStatus[agent.id] !== "add" ? 'bg-emerald-500' : 'bg-slate-300 dark:bg-slate-600'}`} />

                <span className="capitalize relative">
                  {agentStatus[agent.id] }
                </span>

                {agentStatus[agent.id] === 'processing' && <FaSpinner className="animate-spin text-amber-500" />}
              </div>
            </div>

            {agent.status?.performance && (
              <span className="rounded-full bg-slate-200 px-2 py-1 text-[10px] font-semibold text-slate-600 dark:bg-slate-700 dark:text-slate-300">
                {agent.status.performance.avg_processing_time?.toFixed(2)}ms
              </span>
            )}
          </div>
        )
        )}
      </div>

      <div className="mt-5 flex gap-3">
        <button
          type="button"
          className="flex-1 rounded-xl bg-slate-900 px-3 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-700 dark:bg-slate-700 dark:hover:bg-slate-600"
          onClick={activateDeactiveAll}
        >
          Activate All
        </button>
        <button
          type="button"
          className="flex-1 rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700"
          onClick={activateDeactiveAll}
        >
          Clear All
        </button>
      </div>
    </div>
  );
}
