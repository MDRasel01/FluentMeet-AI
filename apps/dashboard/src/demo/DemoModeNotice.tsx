import React from 'react';
import { Sparkles, ArrowRight } from 'lucide-react';

interface DemoModeNoticeProps {
  tabName: string;
  onSwitchReal: () => void;
  className?: string;
}

export const DemoModeNotice: React.FC<DemoModeNoticeProps> = ({
  tabName,
  onSwitchReal,
  className = '',
}) => {
  return (
    <div
      className={`mb-4 p-3.5 rounded-xl border border-amber-300 dark:border-amber-700/60 bg-amber-50/90 dark:bg-amber-950/40 text-amber-900 dark:text-amber-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-sm ${className}`}
      role="alert"
    >
      <div className="flex items-start gap-2.5">
        <div className="w-7 h-7 rounded-lg bg-amber-100 dark:bg-amber-900/60 text-amber-700 dark:text-amber-300 flex items-center justify-center shrink-0 mt-0.5 sm:mt-0">
          <Sparkles className="w-4 h-4" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-amber-800 dark:text-amber-300">
              Interactive Demo Mode
            </span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-200/80 dark:bg-amber-900/80 text-amber-900 dark:text-amber-200 font-medium">
              Sample Data Active
            </span>
          </div>
          <p className="text-xs text-amber-800/90 dark:text-amber-300/90 mt-0.5 leading-relaxed">
            You are viewing pre-populated demonstration data for <strong>{tabName}</strong>. This lets you explore all features before recording actual meetings.
          </p>
        </div>
      </div>

      <button
        type="button"
        onClick={onSwitchReal}
        className="self-end sm:self-center shrink-0 px-3 py-1.5 text-xs font-semibold rounded-lg bg-white dark:bg-slate-900 border border-amber-300 dark:border-amber-700 text-amber-900 dark:text-amber-200 hover:bg-amber-100/50 dark:hover:bg-slate-800 transition-colors shadow-sm flex items-center gap-1.5"
      >
        <span>Switch to Real Version</span>
        <ArrowRight className="w-3.5 h-3.5" />
      </button>
    </div>
  );
};

