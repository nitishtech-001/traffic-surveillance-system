import React from 'react';
import { FaCheck, FaSpinner } from 'react-icons/fa';

export default function AgentPanel({
  agents,
  agentStatus,
  selectedAgents,
  onAgentToggle
}) {
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
        {agents.map((agent) => {
          const isSelected = selectedAgents.includes(agent.id);
          const status = agentStatus?.find((s) => s.agent_id === agent.id);
          const isActive = status?.status === 'ready' || status?.status === 'processing';

          return (
            <button
              type="button"
              key={agent.id}
              onClick={() => onAgentToggle(agent.id)}
              className={`flex w-full items-center gap-3 rounded-2xl border p-3 text-left transition ${isSelected ? 'border-sky-200 bg-sky-50 shadow-sm dark:border-sky-500/40 dark:bg-sky-500/10' : 'border-slate-200 bg-slate-50 hover:border-slate-300 hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-800/70 dark:hover:border-slate-600 dark:hover:bg-slate-800'}`}
            >
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-linear-to-br from-slate-900 to-slate-700 text-lg text-white shadow-inner dark:from-slate-700 dark:to-slate-600">
                {agent.icon || '🤖'}
              </div>

              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between gap-2">
                  <span className="truncate text-sm font-semibold text-slate-800 dark:text-slate-100">
                    {agent.name}
                  </span>
                  {isSelected && (
                    <span className="flex h-6 w-6 items-center justify-center rounded-full bg-sky-600 text-xs text-white">
                      <FaCheck />
                    </span>
                  )}
                </div>

                <div className="mt-1 flex items-center gap-2 text-[11px] text-slate-500 dark:text-slate-400">
                  <span className={`h-2.5 w-2.5 rounded-full ${isActive ? 'bg-emerald-500' : 'bg-slate-300 dark:bg-slate-600'}`} />
                  <span className="capitalize">{status?.status || 'idle'}</span>
                  {status?.status === 'processing' && <FaSpinner className="animate-spin text-amber-500" />}
                </div>
              </div>

              {status?.performance && (
                <span className="rounded-full bg-slate-200 px-2 py-1 text-[10px] font-semibold text-slate-600 dark:bg-slate-700 dark:text-slate-300">
                  {status.performance.avg_processing_time?.toFixed(2)}ms
                </span>
              )}
            </button>
          );
        })}
      </div>

      <div className="mt-5 flex gap-3">
        <button
          type="button"
          className="flex-1 rounded-xl bg-slate-900 px-3 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-700 dark:bg-slate-700 dark:hover:bg-slate-600"
          onClick={() => agents.forEach((agent) => {
            if (!selectedAgents.includes(agent.id)) onAgentToggle(agent.id);
          })}
        >
          Select All
        </button>
        <button
          type="button"
          className="flex-1 rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700"
          onClick={() => agents.forEach((agent) => {
            if (selectedAgents.includes(agent.id)) onAgentToggle(agent.id);
          })}
        >
          Clear All
        </button>
      </div>
    </div>
  );
}
