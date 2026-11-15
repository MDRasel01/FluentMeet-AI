import React, { useState, useEffect } from 'react';
import {
  Crown,
  LayoutDashboard,
  Puzzle,
  ShieldAlert,
  Palette,
  Globe,
  Download,
  Sun,
  Moon,
  CheckCircle2,
  Database,
  Layers,
  Sparkles
} from 'lucide-react';
import { fetchAppSpaces, fetchScreenTrackerStats, AppSpace, ScreenTrackerStats } from '../../lib/supabase';
import { ExtensionDownloadModal } from './ExtensionDownloadModal';

export type FounderSpace = 'landing' | 'dashboard' | 'extension' | 'admin' | 'design-system';

interface FounderLayoutProps {
  activeSpace: FounderSpace;
  onSelectSpace: (space: FounderSpace) => void;
  isDark: boolean;
  onToggleTheme: () => void;
  isDemoMode: boolean;
  onToggleDemoMode: () => void;
  children: React.ReactNode;
}

export const FounderLayout: React.FC<FounderLayoutProps> = ({
  activeSpace,
  onSelectSpace,
  isDark,
  onToggleTheme,
  isDemoMode,
  onToggleDemoMode,
  children,
}) => {
  const [appSpaces, setAppSpaces] = useState<AppSpace[]>([]);
  const [stats, setStats] = useState<ScreenTrackerStats>({
    readyCount: 49,
    totalCount: 49,
    percentage: 100,
  });
  const [downloadModalOpen, setDownloadModalOpen] = useState(false);

  useEffect(() => {
    fetchAppSpaces().then(setAppSpaces);
    fetchScreenTrackerStats().then(setStats);
  }, []);

  const getSpaceIcon = (slug: string) => {
    switch (slug) {
      case 'landing':
        return <Globe className="w-3.5 h-3.5 text-amber-300" />;
      case 'dashboard':
        return <LayoutDashboard className="w-3.5 h-3.5 text-indigo-400" />;
      case 'extension':
        return <Puzzle className="w-3.5 h-3.5 text-purple-400" />;
      case 'admin':
        return <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />;
      case 'design-system':
        return <Palette className="w-3.5 h-3.5 text-emerald-400" />;
      default:
        return <Layers className="w-3.5 h-3.5" />;
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 dark:bg-slate-950 flex flex-col font-sans">
      {/* 
        FOUNDER WORKBENCH TOP BAR
        Rendered only when server-verified role is 'owner'.
      */}
      <header className="bg-slate-900 text-white px-4 py-2.5 flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 z-50 text-xs shadow-lg sticky top-0">
        <div className="flex items-center gap-3">
          {/* Owner Badge */}
          <div className="flex items-center gap-1.5 font-bold tracking-tight">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="font-extrabold text-white">Founder Workbench</span>
            <span className="ml-1 px-2 py-0.5 rounded-full bg-amber-400/20 text-amber-300 font-extrabold text-[10px] border border-amber-400/30 flex items-center gap-1 shadow-sm">
              <Crown className="w-3 h-3 text-amber-400 inline" /> Owner Role
            </span>
          </div>

          <div className="h-4 w-px bg-slate-700 hidden sm:block" />

          {/* Dynamic App Switcher Tabs (Queried from app_spaces table) */}
          <nav className="flex items-center bg-slate-800/90 rounded-xl p-0.5 border border-slate-700/80 overflow-x-auto scrollbar-none">
            {appSpaces.map((space) => {
              const isActive = activeSpace === space.slug;
              return (
                <button
                  key={space.id || space.slug}
                  onClick={() => onSelectSpace(space.slug as FounderSpace)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all whitespace-nowrap text-xs font-semibold ${
                    isActive
                      ? 'bg-indigo-600 text-white shadow-sm'
                      : 'text-slate-300 hover:text-white hover:bg-slate-700/50'
                  }`}
                >
                  {getSpaceIcon(space.slug)}
                  <span>{space.name}</span>
                </button>
              );
            })}
          </nav>

          {/* Quick Extension Download Action */}
          <button
            onClick={() => setDownloadModalOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all bg-emerald-600 hover:bg-emerald-500 text-white font-bold shadow-sm text-xs shrink-0"
            title="Download Extension ZIP & Setup Instructions"
          >
            <Download className="w-3.5 h-3.5" />
            <span className="hidden md:inline">Download Extension</span>
          </button>
        </div>

        {/* Right Controls: Data Mode + Theme + DB Computed Screen Tracker */}
        <div className="flex items-center gap-3">
          {/* Data Mode Switcher: Demo Data vs Live Supabase */}
          <button
            onClick={onToggleDemoMode}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-bold border transition-colors ${
              isDemoMode
                ? 'bg-purple-950/60 border-purple-500/50 text-purple-300'
                : 'bg-emerald-950/60 border-emerald-500/50 text-emerald-300'
            }`}
            title="Toggle between rich sample mock data and live Supabase queries"
          >
            <Database className="w-3 h-3" />
            <span>{isDemoMode ? 'Mode: Demo Mock' : 'Mode: Live DB'}</span>
          </button>

          {/* Theme Engine: Light/Dark Switcher */}
          <button
            onClick={onToggleTheme}
            className="p-1.5 rounded-lg bg-slate-800 border border-slate-700 hover:bg-slate-700 text-slate-300 transition-colors"
            title="Toggle Theme (Persisted to profiles.theme)"
          >
            {isDark ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-300" />}
          </button>

          {/* Screen Completion Tracker: Computed dynamically from screen_registry */}
          <div
            className="flex items-center gap-1 px-3 py-1 rounded-full bg-emerald-950/80 border border-emerald-500/50 text-emerald-300 font-bold text-[11px] shadow-sm"
            title={`Dynamic completion computed from screen_registry: ${stats.readyCount} ready out of ${stats.totalCount} registered screens`}
          >
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>{stats.readyCount} / {stats.totalCount} Screens Ready</span>
          </div>
        </div>
      </header>

      {/* Main App Container */}
      <main className="flex-1 w-full bg-white dark:bg-slate-900 flex flex-col min-h-[calc(100vh-48px)]">
        {children}
      </main>

      {/* Quick Download Modal */}
      <ExtensionDownloadModal
        isOpen={downloadModalOpen}
        onClose={() => setDownloadModalOpen(false)}
      />
    </div>
  );
};
