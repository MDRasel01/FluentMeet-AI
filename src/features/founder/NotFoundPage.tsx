import React from 'react';
import { Compass, ArrowLeft } from 'lucide-react';

interface NotFoundPageProps {
  onGoHome?: () => void;
}

/**
 * Standard 404 Page.
 * Displayed whenever a non-owner attempts to access /founder/* routes.
 * Ensures zero leakage of founder markup, route structure, or 403 permissions.
 */
export const NotFoundPage: React.FC<NotFoundPageProps> = ({ onGoHome }) => {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex items-center justify-center p-6">
      <div className="max-w-md w-full text-center space-y-6">
        <div className="w-16 h-16 rounded-3xl bg-slate-200/80 dark:bg-slate-800 flex items-center justify-center mx-auto text-slate-500 dark:text-slate-400 shadow-inner">
          <Compass className="w-8 h-8" />
        </div>

        <div className="space-y-2">
          <span className="text-xs font-mono font-bold uppercase tracking-widest text-indigo-600 dark:text-indigo-400">
            Error 404
          </span>
          <h1 className="text-3xl font-black tracking-tight">Page Not Found</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 leading-relaxed">
            The page you requested does not exist or may have been moved.
          </p>
        </div>

        <div className="pt-2">
          <button
            onClick={() => {
              if (onGoHome) {
                onGoHome();
              } else {
                window.location.href = '/';
              }
            }}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 dark:bg-white dark:hover:bg-slate-100 text-white dark:text-slate-900 text-xs font-bold transition-all shadow-md"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Return to Homepage</span>
          </button>
        </div>
      </div>
    </div>
  );
};
