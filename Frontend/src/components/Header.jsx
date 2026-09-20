import { useTheme } from '../hooks/useTheme.js'
import CameraSelector from './CameraSelector.jsx'
import { useCameraStream } from '../hooks/useCameraStream.js'
import { useCamera } from '../hooks/useCamera.js'

export default function Header() {
    const toggleTheme = useTheme((state) => state.toggleTheme)
    const theme = useTheme((state) => state.theme)
    const wsConnected = useCameraStream((s) => s.streamUrl != null)
    const isConnected = useCamera((s) => s.currentCamera != null)

    return (
        <header className="z-50 mb-5 rounded-[28px] border border-slate-200/80 bg-white/80 shadow-[0_20px_50px_-24px_rgba(15,23,42,0.25)]  dark:border-slate-800 dark:bg-slate-900/80">
            <div className="flex flex-col gap-4 p-4 sm:p-5 xl:flex-row xl:items-center xl:justify-between">
                {/* TOP HEADER */}
                <div className="flex items-start gap-3 sm:gap-4">
                    <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-linear-to-br from-sky-500 via-cyan-500 to-indigo-600 text-xl shadow-lg shadow-sky-500/30">
                        <img src="/traffic_survillance_logo.png" alt="Brand Logo" className='rounded-lg dark:border-2 border-s-white'/>
                    </div>
                    <div>
                        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-sky-600 dark:text-sky-400">
                            Live Intelligence
                        </p>
                        <h1 className="mt-1 text-xl font-bold tracking-tight text-slate-900 dark:text-white sm:text-2xl">
                            Video Analysis System
                        </h1>
                    </div>
                </div>
                {/* STATE OF CMERA AND WEBSOCKET */}
                <div className="flex flex-col items-stretch gap-3 sm:flex-row sm:items-center">
                    <div className="flex flex-wrap items-center gap-2">
                        <span className={`inline-flex items-center rounded-full border px-3 py-1.5 text-xs font-medium ${isConnected ? 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-500/40 dark:bg-emerald-500/10 dark:text-emerald-300' : 'border-rose-200 bg-rose-50 text-rose-700 dark:border-rose-500/40 dark:bg-rose-500/10 dark:text-rose-300'}`}>
                            {isConnected ? '● Connected' : '● Disconnected'}
                        </span>
                        
                        <span className={`inline-flex items-center rounded-full border border-sky-200 bg-sky-50 px-3 py-1.5 text-xs font-medium dark:border-sky-500/40  ${wsConnected ? 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-500/40 dark:bg-emerald-500/10 dark:text-emerald-300' : 'border-rose-200 bg-rose-50 text-rose-700 dark:border-rose-500/40 dark:bg-rose-500/10 dark:text-rose-300'}`}>
                            {wsConnected ? '● WebSocket Live' :'● WebSocket Offline'}
                        </span>
                        

                        </div>

                    <button
                        type="button"
                        onClick={() => toggleTheme()}
                        className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-2.5 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:border-slate-600 dark:hover:bg-slate-700 cursor-pointer"
                    >
                        {theme === "light" ? '☀️ Light' : '🌙 Dark'}
                    </button>

                    <CameraSelector />

                </div>
            </div>
        </header>
    )
}
