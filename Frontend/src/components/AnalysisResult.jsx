import { useEffect, useMemo, useState } from 'react';
import { toast } from 'react-toastify';
import { useWebRTC } from '../hooks/useWebRTC';
import { useCamera } from '../hooks/useCamera';
import { useAgents } from '../hooks/useAgents';

const inputStyle =
  'rounded-xl border border-slate-200 bg-slate-50 px-2 py-2.5 text-sm text-slate-700 outline-none transition focus:border-sky-400 focus:ring-2 focus:ring-sky-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100 dark:focus:border-sky-500 dark:focus:ring-sky-500/20 w-40';

const LS_LOST = 'lost-vehicles:v1';
const LS_FOUND = 'lost-vehicles:found:v1';

const normPlate = (s = '') => s.toUpperCase().replace(/[^A-Z0-9]/g, '');

const DEMO_RESULTS = {
  success: true,
  timestamp: new Date().toISOString(),
  total_processing_time: 0.842,
  active_agents: ['object_detection', 'license_plate'],
  agent_results: {
    object_detection: {
      success: true,
      processing_time: 0.512,
      agent_id: 'obj-det-01',
      agent_name: 'Object Detection',
      confidence_threshold: 0.5,
      performance_metrics: {
        total_processed: 128,
        avg_processing_time: 0.048,
        total_processing_time: 6.14,
        last_processing_time: 0.052,
      },
      result: {
        total_objects: 7,
        object_counts: { car: 4, person: 2, truck: 1 },
        frame_info: { width: 1280, height: 720 },
      },
    },
    license_plate: {
      success: true,
      processing_time: 0.33,
      agent_id: 'lpd-01',
      agent_name: 'License Plate',
      confidence_threshold: 0.5,
      performance_metrics: {
        total_processed: 112,
        avg_processing_time: 0.052,
        total_processing_time: 5.82,
        last_processing_time: 0.048,
      },
      result: {
        plates: [
          { plate_text: 'JH10KL7868', confidence: 0.93 },
          { plate_text: 'MH12DE1433', confidence: 0.88 },
          { plate_text: 'KA05AB1234', confidence: 0.71 },
        ],
        total_plates: 3,
      },
    },
  },
};

export default function AnalysisResults() {
  const results = useWebRTC((s) => s.results);
  if(results){
    console.log(results)
  }
  // const results = DEMO_RESULTS
  const currentCamera = useCamera((s) => s.currentCamera);
  const isProcessing = useAgents((s) => s.isProcessing);

  const [lostVehicle, setLostVehicle] = useState(() => {
    try { return JSON.parse(localStorage.getItem(LS_LOST)) || {}; } catch { return {}; }
  });
  const [foundVehicle, setFoundVehicle] = useState(() => {
    try { return JSON.parse(localStorage.getItem(LS_FOUND)) || {}; } catch { return {}; }
  });

  useEffect(() => {
    try { localStorage.setItem(LS_LOST, JSON.stringify(lostVehicle)); } catch { }
  }, [lostVehicle]);
  useEffect(() => {
    try { localStorage.setItem(LS_FOUND, JSON.stringify(foundVehicle)); } catch { }
  }, [foundVehicle]);

  const showDemo = false;
  const view = results ?? (showDemo ? DEMO_RESULTS : null);

  const matches = useMemo(() => {
    const plates = view?.agent_results?.license_plate?.result?.plates || [];
    if (!plates.length) return [];
    const lostByNorm = new Map(
      Object.entries(lostVehicle).map(([num, meta]) => [normPlate(num), { num, ...meta }])
    );
    return plates
      .map((p) => {
        const hit = lostByNorm.get(normPlate(p.plate_text));
        return hit ? { ...p, matchedNumber: hit.num, owner: hit.owner } : null;
      })
      .filter(Boolean);
  }, [view, lostVehicle]);

  useEffect(() => {
    if (!matches.length) return;
    setFoundVehicle((prev) => {
      const next = { ...prev };
      let changed = false;
      for (const m of matches) {
        if (!next[m.matchedNumber]) {
          next[m.matchedNumber] = {
            owner: m.owner,
            plate_text: m.plate_text,
            confidence: m.confidence,
            at: Date.now(),
          };
          changed = true;
        }
      }
      return changed ? next : prev;
    });
  }, [matches]);

  const handleLostVehicleEntry = (e) => {
    e.preventDefault();
    const owner = e.target[0].value.trim();
    const number = e.target[1].value.trim().toUpperCase();
    if (!owner || !number) { toast.warning('All fields required!'); return; }
    const key = normPlate(number);
    if (lostVehicle[key] && !confirm('Vehicle number already exists. Overwrite owner?')) {
      e.target.reset(); return;
    }
    setLostVehicle((prev) => ({ ...prev, [key]: { owner, createdAt: Date.now() } }));
    e.target.reset();
    toast.success(`Saved ${owner} → ${number}`);
  };

  const removeLost = (key) =>
    setLostVehicle((prev) => { const n = { ...prev }; delete n[key]; return n; });

  const clearFound = () => { setFoundVehicle({}); toast.success('Cleared found vehicles'); };

  const LostVehicleForm = (
    <div className="mb-5 rounded-lg border border-slate-200/80 bg-white/80 p-5 shadow-[0_20px_50px_-28px_rgba(15,23,42,0.35)] backdrop-blur-xl dark:border-slate-800 dark:bg-slate-900/80">
      <h3 className="mb-3 text-lg font-bold text-slate-900 dark:text-white">Add Lost Vehicle Number</h3>
      <form onSubmit={handleLostVehicleEntry} className="flex flex-wrap items-center gap-3">
        <input type="text" placeholder="Nitish Kumar" className={`${inputStyle} capitalize`} />
        <input type="text" pattern="[a-zA-Z0-9]+" placeholder="JH10KL7868"
          title="Only alphanumeric value without spaces" className={`${inputStyle} uppercase`} />
        <button type="submit"
          className="rounded-lg border-2 border-sky-500 bg-sky-500 px-4 py-2 text-sm font-semibold text-white hover:bg-sky-600">
          Add
        </button>
      </form>
      {Object.keys(lostVehicle).length > 0 && (
        <div className="mt-4 flex flex-wrap gap-2">
          {Object.entries(lostVehicle).map(([num, meta]) => (
            <span key={num}
              className="inline-flex items-center gap-2 rounded-full bg-rose-100 px-3 py-1 font-mono text-xs text-rose-700 dark:bg-rose-500/10 dark:text-rose-300">
              {num} • {meta.owner}
              <button onClick={() => removeLost(num)} className="text-rose-500 hover:text-rose-700"
                aria-label={`Remove ${num}`}>×</button>
            </span>
          ))}
        </div>
      )}
    </div>
  );

  if (!view) {
    return (
      <div>
        {LostVehicleForm}
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

  const agentResults = view.agent_results || {};

  return (
    <div>
      {LostVehicleForm}

      <div className="max-h-[620px] overflow-y-auto rounded-lg border border-slate-200/80 bg-white/80 p-5 shadow-[0_20px_50px_-28px_rgba(15,23,42,0.35)] backdrop-blur-xl dark:border-slate-800 dark:bg-slate-900/80">
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

        {matches.length > 0 && (
          <div className="mb-4 rounded-2xl border border-rose-300 bg-rose-50 p-3 dark:border-rose-500/40 dark:bg-rose-500/10">
            <div className="mb-2 flex items-center justify-between">
              <h4 className="text-sm font-bold text-rose-700 dark:text-rose-300">🚨 Lost Vehicle Found</h4>
              <span className="rounded-full bg-rose-600 px-2 py-0.5 text-[10px] font-semibold text-white">{matches.length}</span>
            </div>
            <ul className="space-y-1 text-sm">
              {matches.map((m) => (
                <li key={m.plate_text} className="flex justify-between gap-3">
                  <span className="font-mono font-bold text-rose-800 dark:text-rose-200">{m.plate_text}</span>
                  <span className="text-rose-700 dark:text-rose-300">Owner: {m.owner} • {(m.confidence * 100).toFixed(1)}%</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="space-y-3 rounded-2xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-800/60">
          <div className="text-[11px] font-medium uppercase tracking-[0.2em] text-slate-400 dark:text-slate-500">
            {view.timestamp ? new Date(view.timestamp).toLocaleString() : '—'}
          </div>

          <div className="space-y-3">
            {Object.entries(agentResults).map(([agentId, agentInfo]) => {
              if (!agentInfo?.success) {
                return (
                  <div key={agentId} className="rounded-2xl border border-rose-200 bg-rose-50 p-3 dark:border-rose-500/30 dark:bg-rose-500/10">
                    <h4 className="text-sm font-semibold capitalize text-rose-700 dark:text-rose-300">{agentId.replace(/_/g, ' ')}</h4>
                    <p className="mt-1 text-sm text-rose-600 dark:text-rose-400">{agentInfo?.error || 'Agent failed'}</p>
                  </div>
                );
              }
              const agentResult = agentInfo.result || {};

              if (agentId === 'object-detection') {
                const counts = Object.entries(agentResult.object_counts || {});
                return (
                  <div key={agentId} className="rounded-2xl border border-emerald-200 bg-emerald-50 p-3 dark:border-emerald-500/30 dark:bg-emerald-500/10">
                    <div className="flex items-center justify-between gap-2">
                      <h4 className="text-sm font-semibold capitalize text-emerald-700 dark:text-emerald-300">{agentInfo.agent_name || agentId}</h4>
                      <span className="rounded-full bg-emerald-600 px-2 py-1 text-[10px] font-semibold text-white">{agentResult.total_objects || 0} objects</span>
                    </div>
                    <div className="mt-2 h-16 space-y-1.5 overflow-y-auto pr-1 scrollbar-thin">
                      {counts.length === 0 && <div className="text-xs text-slate-500">No objects detected</div>}
                      {counts.map(([class_name, class_count]) => (
                        <div key={class_name} className="flex items-center justify-between gap-3 text-sm text-slate-700 dark:text-slate-200">
                          <span className="capitalize">{class_name}</span>
                          <span className="font-semibold">{class_count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              }

              if (agentId === 'license-plate') {
                const plates = agentResult?.plates || [];
                return (
                  <div key={agentId} className="rounded-2xl border border-sky-200 bg-sky-50 p-3 dark:border-sky-500/30 dark:bg-sky-500/10">
                    <div className="flex items-center justify-between gap-2">
                      <h4 className="text-sm font-semibold capitalize text-sky-700 dark:text-sky-300">{agentInfo.agent_name || agentId}</h4>
                      <span className="rounded-full bg-sky-600 px-2 py-1 text-[10px] font-semibold text-white">{plates.length} plates</span>
                    </div>
                    <div className="mt-2 h-16 space-y-1.5 overflow-y-auto pr-1 scrollbar-thin">
                      {plates.length === 0 && <div className="text-xs text-slate-500">No plates detected</div>}
                      {plates.map((plate, idx) => {
                        const hit = matches.some((m) => normPlate(m.plate_text) === normPlate(plate.plate_text));
                        return (
                          <div key={idx} className={`flex items-center justify-between gap-3 rounded px-1 text-sm ${hit ? 'bg-rose-100 dark:bg-rose-500/20' : ''}`}>
                            <span className="font-mono font-bold text-sky-800 dark:text-sky-200">{plate.plate_text}</span>
                            <span className="text-slate-500 dark:text-slate-400">{(plate.confidence * 100).toFixed(1)}%</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
              }

              return (
                <div key={agentId} className="rounded-2xl border border-slate-200 bg-white p-3 dark:border-slate-700 dark:bg-slate-900">
                  <h4 className="text-sm font-semibold capitalize text-slate-700 dark:text-slate-200">{agentId.replace(/_/g, ' ')}</h4>
                  <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Processing complete</p>
                </div>
              );
            })}
          </div>

          {view.total_processing_time != null && (
            <div className="mt-4 border-t border-slate-200 pt-3 text-[11px] text-slate-500 dark:border-slate-700 dark:text-slate-400">
              <div className="flex items-center justify-between gap-2">
                <span>Processing Time: {Number(view.total_processing_time).toFixed(2)}s</span>
                <span>Active Agents: {view.active_agents?.length || 0}</span>
              </div>
            </div>
          )}
        </div>

        <div className="mt-3 text-[11px] font-medium uppercase tracking-[0.2em] text-slate-400 dark:text-slate-500">
          Active Agents: {(view.active_agents || []).join(', ') || '—'}
        </div>
      </div>

      {Object.keys(foundVehicle).length > 0 && (
        <div className="mt-5 rounded-lg border border-slate-200/80 bg-white/80 p-5 shadow-[0_20px_50px_-28px_rgba(15,23,42,0.35)] backdrop-blur-xl dark:border-slate-800 dark:bg-slate-900/80">
          <div className="mb-3 flex items-center justify-between">
            <h3 className="text-base font-semibold text-slate-900 dark:text-white">
              Found Vehicles ({Object.keys(foundVehicle).length})
            </h3>
            <button onClick={clearFound}
              className="rounded-md border border-rose-300 px-2 py-1 text-xs text-rose-600 hover:bg-rose-50 dark:border-rose-500/40 dark:text-rose-300 dark:hover:bg-rose-500/10">
              Clear
            </button>
          </div>
          <ul className="space-y-2 text-sm">
            {Object.entries(foundVehicle).map(([num, meta]) => (
              <li key={num} className="flex items-center justify-between rounded-xl bg-rose-50 px-3 py-2 dark:bg-rose-500/10">
                <span className="font-mono font-bold text-rose-700 dark:text-rose-300">{num}</span>
                <span className="text-slate-700 dark:text-slate-300">Owner: {meta.owner} • {new Date(meta.at).toLocaleTimeString()}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}