import React from 'react';
import { Sparkles, Shield, Heart, ArrowUpRight } from 'lucide-react';
import { PlatformIcon } from '../../../../design-system/components';

interface FooterProps {
  onOpenAuth: (mode: 'signin' | 'signup') => void;
  onNavigateApp: (app: 'dashboard' | 'extension') => void;
}

export const Footer: React.FC<FooterProps> = ({ onOpenAuth, onNavigateApp }) => {
  return (
    <footer className="border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 text-slate-600 dark:text-slate-400 text-xs">
      {/* Top CTA Banner */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="p-8 sm:p-12 rounded-3xl bg-gradient-to-r from-indigo-900 via-indigo-950 to-purple-950 text-white flex flex-col md:flex-row items-center justify-between gap-6 shadow-2xl relative overflow-hidden">
          <div className="space-y-2 text-center md:text-left z-10">
            <span className="text-xs font-bold text-indigo-300 uppercase tracking-wider block">
              Join 50,000+ Global Professionals
            </span>
            <h3 className="text-2xl sm:text-3xl font-black tracking-tight">
              Ready to speak confident English in every call?
            </h3>
            <p className="text-xs sm:text-sm text-slate-300 max-w-lg">
              Install the Chrome extension in 30 seconds. Start receiving discreet speech coaching today.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-center gap-3 z-10 w-full sm:w-auto">
            <button
              onClick={() => onOpenAuth('signup')}
              className="w-full sm:w-auto px-6 py-3 rounded-xl bg-white text-indigo-950 font-bold hover:bg-slate-100 transition-all shadow-md text-xs whitespace-nowrap"
            >
              Start Free (14-Day Trial)
            </button>
            <button
              onClick={() => onNavigateApp('extension')}
              className="w-full sm:w-auto px-5 py-3 rounded-xl bg-white/10 hover:bg-white/20 text-white font-semibold transition-all border border-white/20 text-xs whitespace-nowrap"
            >
              Download Extension
            </button>
          </div>
        </div>
      </div>

      {/* Main Footer Links */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12 grid grid-cols-2 md:grid-cols-5 gap-8">
        <div className="col-span-2 space-y-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-white font-black text-sm">
              F
            </div>
            <span className="font-extrabold text-base text-slate-900 dark:text-white">
              FluentMeet<span className="text-indigo-600">.AI</span>
            </span>
          </div>
          <p className="text-xs text-slate-500 max-w-sm leading-relaxed">
            The intelligent real-time meeting English co-pilot. Built to empower non-native speakers to communicate with clarity, precision, and confidence.
          </p>
          <div className="flex items-center gap-2 text-[11px] text-slate-400">
            <Shield className="w-3.5 h-3.5 text-emerald-500" />
            <span>SOC2 Type II • GDPR Compliant • AES-256</span>
          </div>
        </div>

        <div>
          <h5 className="font-bold text-slate-900 dark:text-white mb-3 text-xs uppercase tracking-wider">
            Platforms
          </h5>
          <ul className="space-y-2">
            <li>
              <a href="#live-demo" className="hover:text-indigo-600 transition-colors">Google Meet Coach</a>
            </li>
            <li>
              <a href="#live-demo" className="hover:text-indigo-600 transition-colors">Zoom Meeting Coach</a>
            </li>
            <li>
              <a href="#live-demo" className="hover:text-indigo-600 transition-colors">Microsoft Teams Coach</a>
            </li>
            <li>
              <button onClick={() => onNavigateApp('extension')} className="hover:text-indigo-600 transition-colors flex items-center gap-1">
                Chrome Extension <ArrowUpRight className="w-3 h-3" />
              </button>
            </li>
          </ul>
        </div>

        <div>
          <h5 className="font-bold text-slate-900 dark:text-white mb-3 text-xs uppercase tracking-wider">
            Product
          </h5>
          <ul className="space-y-2">
            <li>
              <a href="#how-it-works" className="hover:text-indigo-600 transition-colors">How It Works</a>
            </li>
            <li>
              <a href="#features" className="hover:text-indigo-600 transition-colors">Features & Accuracy</a>
            </li>
            <li>
              <a href="#use-cases" className="hover:text-indigo-600 transition-colors">Scenarios & Roles</a>
            </li>
            <li>
              <a href="#pricing" className="hover:text-indigo-600 transition-colors">Pricing Plans</a>
            </li>
            <li>
              <button onClick={() => onNavigateApp('dashboard')} className="hover:text-indigo-600 transition-colors">
                Web Dashboard
              </button>
            </li>
          </ul>
        </div>

        <div>
          <h5 className="font-bold text-slate-900 dark:text-white mb-3 text-xs uppercase tracking-wider">
            Account & Security
          </h5>
          <ul className="space-y-2">
            <li>
              <button onClick={() => onOpenAuth('signin')} className="hover:text-indigo-600 transition-colors">
                Sign In
              </button>
            </li>
            <li>
              <button onClick={() => onOpenAuth('signup')} className="hover:text-indigo-600 transition-colors">
                Create Free Account
              </button>
            </li>
            <li>
              <a href="#pricing" className="hover:text-indigo-600 transition-colors">Privacy Policy</a>
            </li>
            <li>
              <a href="#pricing" className="hover:text-indigo-600 transition-colors">Terms of Service</a>
            </li>
          </ul>
        </div>
      </div>

      <div className="border-t border-slate-100 dark:border-slate-800/80 py-6 text-center text-[11px] text-slate-400">
        © {new Date().getFullYear()} FluentMeet AI Inc. All rights reserved. Built for global teams.
      </div>
    </footer>
  );
};
