import React from 'react';
import { TabDataMode } from './types';
import { Database, Sparkles, CheckCircle2 } from 'lucide-react';

interface DataModeSelectorProps {
  mode: TabDataMode;
  onChange: (mode: TabDataMode) => void;
  size?: 'sm' | 'md';
  className?: string;
  tabLabel?: string;
}

export const DataModeSelector: React.FC<DataModeSelectorProps> = ({
  mode,
  onChange,
  size = 'sm',
  className = '',
  tabLabel,
}) => {
  const isReal = mode === 'REAL';

  return (
    <div
      className={`inline-flex items-center p-0.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-100 dark:bg-slate-900 select-none shadow-sm ${className}`}
      role="group"
      aria-label="Data Source Mode Selector"
    >
      {/* REAL VERSION TAB */}
      <button
        type="button"
        onClick={() => onChange('REAL')}
        className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold transition-all duration-150 ${
          isReal
            ? 'bg-white dark:bg-slate-800 text-emerald-700 dark:text-emerald-400 shadow-sm border border-emerald-200 dark:border-emerald-800/60'
            : 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'
        }`}
        aria-pressed={isReal}
        title={`View actual live data${tabLabel ? ` for ${tabLabel}` : ''}`}
      >
        <span
          className={`w-1.5 h-1.5 rounded-full ${
            isReal ? 'bg-emerald-500 animate-pulse' : 'bg-slate-400'
          }`}
        />
        <span>REAL VERSION</span>
      </button>

      {/* DEMO VERSION TAB */}
      <button
        type="button"
        onClick={() => onChange('DEMO')}
        className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold transition-all duration-150 ${
          !isReal
            ? 'bg-amber-50 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 shadow-sm border border-amber-300 dark:border-amber-700'
            : 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'
        }`}
        aria-pressed={!isReal}
        title={`View interactive demonstration sample data${tabLabel ? ` for ${tabLabel}` : ''}`}
      >
        <Sparkles
          className={`w-3 h-3 ${
            !isReal ? 'text-amber-600 dark:text-amber-400' : 'text-slate-400'
          }`}
        />
        <span>DEMO VERSION</span>
      </button>
    </div>
  );
};
