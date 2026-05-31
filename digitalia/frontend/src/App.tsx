import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { api, LearnerData, Project } from './services/api';
import { ProgressDashboard } from './components/ProgressDashboard';
import { PortfolioView } from './components/PortfolioView';
import { Sparkles, Terminal, ShieldAlert, Cpu } from 'lucide-react';

function App() {
  const [learnerData, setLearnerData] = useState<LearnerData | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'dashboard' | 'portfolio'>('dashboard');

  const loadAllData = async () => {
    setLoading(true);
    try {
      const [learnerRes, projectsRes] = await Promise.all([
        api.getLearnerData(),
        api.getAvailableProjects()
      ]);
      setLearnerData(learnerRes);
      setProjects(projectsRes);
    } catch (e) {
      console.error("Erro ao carregar dados do ecossistema DigitalIA:", e);
    } finally {
      // Small timeout to feel premium transition smoother
      setTimeout(() => setLoading(false), 300);
    }
  };

  useEffect(() => {
    loadAllData();
  }, []);

  return (
    <div className="min-h-screen bg-brand-abyss text-slate-100 flex flex-col font-sans selection:bg-brand-purple-neon selection:text-white">
      {/* Dynamic Background Gradients */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-brand-purple-deep/10 rounded-full blur-[140px]" />
        <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-brand-cyan-deep/10 rounded-full blur-[140px]" />
        <div className="absolute top-1/2 left-1/3 w-[300px] h-[300px] bg-radial-gradient opacity-40 pointer-events-none" />
      </div>

      {/* Nav Header */}
      <header className="sticky top-0 z-40 w-full border-b border-white/5 bg-brand-abyss/70 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          {/* Logo Brand Title */}
          <div 
            onClick={() => setViewMode('dashboard')}
            className="flex items-center gap-2 cursor-pointer group"
          >
            <div className="p-2 rounded-xl bg-gradient-to-tr from-brand-purple-neon to-brand-cyan-neon p-[1.5px] group-hover:scale-105 transition-transform">
              <div className="bg-brand-obsidian p-1 rounded-[10px] flex items-center justify-center">
                <Cpu className="w-5 h-5 text-brand-cyan-glow animate-pulse" />
              </div>
            </div>
            <span className="font-black text-lg bg-gradient-to-r from-white via-slate-200 to-brand-purple-glow bg-clip-text text-transparent tracking-tight">
              Digital<span className="text-brand-cyan-neon">IA</span>
            </span>
          </div>

          {/* Quick Info badges for Developers / Reviewers */}
          <div className="flex items-center gap-3">
            <span className="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-mono font-semibold tracking-wider bg-brand-purple-deep/40 text-brand-purple-glow border border-brand-purple-neon/20">
              <Terminal className="w-3 h-3" />
              Vite + TS + Tailwind
            </span>
            <span className="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-mono font-semibold tracking-wider bg-brand-emerald-deep/40 text-brand-emerald-glow border border-brand-emerald-neon/20">
              <ShieldAlert className="w-3 h-3 animate-ping" />
              HMAC Integrado
            </span>
          </div>
        </div>
      </header>

      {/* Main Container Content */}
      <main className="flex-grow z-10 relative">
        <AnimatePresence mode="wait">
          {viewMode === 'dashboard' ? (
            <motion.div
              key="dashboard"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
            >
              <ProgressDashboard
                learnerData={learnerData}
                projects={projects}
                loading={loading}
                onRefresh={loadAllData}
                onViewPortfolio={() => setViewMode('portfolio')}
              />
            </motion.div>
          ) : (
            <motion.div
              key="portfolio"
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.98 }}
              transition={{ duration: 0.4 }}
            >
              {learnerData && (
                <PortfolioView
                  learnerData={learnerData}
                  onBackToDashboard={() => setViewMode('dashboard')}
                />
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}

export default App;
