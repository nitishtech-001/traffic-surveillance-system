import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Components import
import CameraLiveFeed from './components/CameraLiveFeed.jsx';
import AgentPanel from './components/AgentPanel.jsx';
import AnalysisResults from './components/AnalysisResult.jsx';

import ProcessingSettings from './components/ProcessingSettings.jsx';
import Header from './components/Header.jsx';

import { useTheme } from './hooks/useTheme.js';



export default function App() {
  const theme = useTheme((state) => state.theme)

  const isDarkMode = theme === "dark" ? true : false;

  return (
    <div className={isDarkMode ? 'dark' : ''}>
      <div className="min-h-screen bg-slate-100 text-slate-900 transition-colors duration-300 dark:bg-slate-950 dark:text-slate-100">
        <div className="mx-auto max-w-7xl px-3 py-4 sm:px-5 lg:px-6">
          <Header />
          <main className="grid gap-5 xl:grid-cols-[minmax(0,1.6fr)_minmax(340px,0.95fr)]">
            <div className="space-y-5">
              <section className="rounded-[28px] border border-slate-200/80 bg-white/80 p-3  dark:border-slate-800 dark:bg-slate-900/80 sm:p-4">
                <CameraLiveFeed />
              </section>

              <section className="rounded-[28px] border border-slate-200/80 bg-white/80 p-4 dark:border-slate-800 dark:bg-slate-900/80 sm:p-5">
                <ProcessingSettings/>
              </section>
            </div>

            <aside className="space-y-5">
              <AgentPanel />

              <AnalysisResults/>
            </aside>
          </main>


        </div>
      </div>
      {/* SETTIGN THE TOASIFY THEME DYNAMICALLY */}
      <ToastContainer
        position="bottom-right"
        autoClose={3000}
        // TODO : set the zustand state for dark and light mode
        theme={theme}
        toastClassName="!rounded-xl !shadow-lg"
        className='mt-32'
      />
    </div>
  );
}
