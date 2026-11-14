import React from 'react';
import { PlatformIcon } from '../../../design-system/components';
import { ShieldCheck, Chrome, CheckCircle2 } from 'lucide-react';

export const LogosTicker: React.FC = () => {
  return (
    <div className="py-12 border-y border-slate-200/80 dark:border-slate-800/80 bg-white/50 dark:bg-slate-900/40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <p className="text-center text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-8">
          Trusted by non-native professionals from global teams & platforms
        </p>

        <div className="flex flex-wrap items-center justify-center gap-8 sm:gap-12 md:gap-16 opacity-85 hover:opacity-100 transition-opacity">
          {/* Google Meet */}
          <div className="flex items-center gap-2.5 grayscale hover:grayscale-0 transition-all cursor-pointer">
            <PlatformIcon platform="google-meet" size={26} />
            <span className="font-extrabold text-sm text-slate-800 dark:text-slate-200">Google Meet</span>
          </div>

          {/* Zoom */}
          <div className="flex items-center gap-2.5 grayscale hover:grayscale-0 transition-all cursor-pointer">
            <PlatformIcon platform="zoom" size={26} />
            <span className="font-extrabold text-sm text-slate-800 dark:text-slate-200">Zoom</span>
          </div>

          {/* Microsoft Teams */}
          <div className="flex items-center gap-2.5 grayscale hover:grayscale-0 transition-all cursor-pointer">
            <PlatformIcon platform="teams" size={26} />
            <span className="font-extrabold text-sm text-slate-800 dark:text-slate-200">Microsoft Teams</span>
          </div>

          {/* Chrome Web Store */}
          <div className="flex items-center gap-2.5 grayscale hover:grayscale-0 transition-all cursor-pointer">
            <div className="w-6 h-6 rounded-full bg-gradient-to-tr from-amber-400 via-rose-500 to-emerald-500 flex items-center justify-center shadow-sm">
              <Chrome className="w-3.5 h-3.5 text-white" />
            </div>
            <span className="font-bold text-sm text-slate-800 dark:text-slate-200">Chrome Store</span>
          </div>

          {/* Security & SOC2 */}
          <div className="flex items-center gap-2 grayscale hover:grayscale-0 transition-all cursor-pointer">
            <ShieldCheck className="w-5 h-5 text-emerald-500" />
            <span className="font-bold text-sm text-slate-800 dark:text-slate-200">SOC2 Type II</span>
          </div>
        </div>
      </div>
    </div>
  );
};
