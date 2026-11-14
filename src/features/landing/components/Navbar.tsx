import React, { useState } from 'react';
import {
  Sparkles,
  Sun,
  Moon,
  Menu,
  X,
  ArrowRight,
  User,
  LayoutDashboard,
  LogOut,
  ChevronDown,
  Puzzle,
  Download,
  ShieldCheck
} from 'lucide-react';
import { AuthUser } from '../types';

interface NavbarProps {
  user: AuthUser | null;
  isDark: boolean;
  onToggleTheme: () => void;
  onOpenAuth: (mode: 'signin' | 'signup') => void;
  onSignOut: () => void;
  onNavigateApp: (app: 'dashboard' | 'extension') => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  user,
  isDark,
  onToggleTheme,
  onOpenAuth,
  onSignOut,
  onNavigateApp,
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 w-full">
      {/* Top Pro Announcement Strip */}
      <div className="bg-gradient-to-r from-indigo-700 via-purple-700 to-indigo-800 text-white text-[11px] font-medium py-1.5 px-4 text-center flex items-center justify-center gap-2 shadow-sm">
        <span className="inline-flex items-center gap-1 bg-white/20 text-white font-bold px-1.5 py-0.5 rounded text-[9px] uppercase tracking-wider">
          v1.0 Released
        </span>
        <span className="truncate">
          Real-time AI English meeting coach for Google Meet, Zoom & MS Teams with CEFR scoring!
        </span>
        <button
          onClick={() => onNavigateApp('extension')}
          className="hidden sm:inline-flex items-center gap-1 font-bold underline hover:opacity-90 ml-1 text-amber-200"
        >
          Download Extension →
        </button>
      </div>

      {/* Main Glassmorphic Navigation Bar */}
      <nav className="backdrop-blur-xl bg-white/85 dark:bg-slate-900/85 border-b border-slate-200/80 dark:border-slate-800 transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
          {/* Logo & Brand */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-500 flex items-center justify-center shadow-lg shadow-indigo-500/30 text-white font-black text-xl tracking-tighter">
              F
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-extrabold text-base tracking-tight text-slate-900 dark:text-white">
                  FluentMeet<span className="text-indigo-600 dark:text-indigo-400">.AI</span>
                </span>
                <span className="bg-indigo-100 dark:bg-indigo-950/80 text-indigo-700 dark:text-indigo-300 text-[10px] font-bold px-1.5 py-0.2 rounded-md">
                  Coach
                </span>
              </div>
              <span className="text-[10px] text-slate-400 font-medium hidden sm:block leading-none">
                Real-Time Meeting English Co-Pilot
              </span>
            </div>
          </div>

          {/* Desktop Navigation Links */}
          <div className="hidden md:flex items-center gap-7 text-xs font-semibold text-slate-600 dark:text-slate-300">
            <a href="#how-it-works" className="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
              How It Works
            </a>
            <a href="#features" className="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
              Features
            </a>
            <a href="#live-demo" className="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
              Interactive Demo
            </a>
            <a href="#use-cases" className="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
              Use Cases
            </a>
            <a href="#pricing" className="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
              Pricing
            </a>
            <button
              onClick={() => onNavigateApp('extension')}
              className="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors flex items-center gap-1"
            >
              <Puzzle className="w-3.5 h-3.5 text-indigo-500" />
              <span>Chrome Extension</span>
            </button>
          </div>

          {/* Right Controls: Theme + Auth */}
          <div className="flex items-center gap-2.5">
            {/* Theme Toggle */}
            <button
              onClick={onToggleTheme}
              className="p-2 rounded-xl text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              aria-label="Toggle theme"
            >
              {isDark ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-600" />}
            </button>

            {user ? (
              /* Authenticated User Menu */
              <div className="relative">
                <button
                  onClick={() => setProfileDropdownOpen(!profileDropdownOpen)}
                  className="flex items-center gap-2 p-1.5 pr-2.5 rounded-full border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:border-indigo-500 transition-all text-xs"
                >
                  {user.avatarUrl ? (
                    <img
                      src={user.avatarUrl}
                      alt={user.name}
                      className="w-7 h-7 rounded-full object-cover border border-indigo-200"
                    />
                  ) : (
                    <div className="w-7 h-7 rounded-full bg-indigo-600 text-white font-bold text-xs flex items-center justify-center">
                      {user.name.charAt(0)}
                    </div>
                  )}
                  <div className="text-left hidden sm:block">
                    <span className="font-bold text-slate-900 dark:text-white block leading-tight truncate max-w-[100px]">
                      {user.name.split(' ')[0]}
                    </span>
                    <span className="text-[9px] text-indigo-600 dark:text-indigo-400 font-semibold block leading-none">
                      {user.tier === 'enterprise' ? 'Enterprise' : 'Pro Coach'}
                    </span>
                  </div>
                  <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                </button>

                {/* Profile Dropdown */}
                {profileDropdownOpen && (
                  <div
                    className="absolute right-0 mt-2 w-56 bg-white dark:bg-slate-800 rounded-2xl shadow-xl border border-slate-200 dark:border-slate-700 py-1.5 z-50 animate-in fade-in zoom-in-95 text-xs font-medium"
                    onClick={() => setProfileDropdownOpen(false)}
                  >
                    <div className="px-3.5 py-2 border-b border-slate-100 dark:border-slate-700">
                      <div className="font-bold text-slate-900 dark:text-white truncate">{user.name}</div>
                      <div className="text-[10px] text-slate-400 truncate">{user.email}</div>
                    </div>

                    <button
                      onClick={() => onNavigateApp('dashboard')}
                      className="w-full px-3.5 py-2 text-left text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700 flex items-center gap-2"
                    >
                      <LayoutDashboard className="w-4 h-4 text-indigo-500" />
                      <span>Open Web Dashboard</span>
                    </button>

                    <button
                      onClick={() => onNavigateApp('extension')}
                      className="w-full px-3.5 py-2 text-left text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700 flex items-center gap-2"
                    >
                      <Puzzle className="w-4 h-4 text-purple-500" />
                      <span>Open Chrome Extension</span>
                    </button>

                    <div className="border-t border-slate-100 dark:border-slate-700 my-1" />

                    <button
                      onClick={onSignOut}
                      className="w-full px-3.5 py-2 text-left text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/40 flex items-center gap-2"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Sign Out</span>
                    </button>
                  </div>
                )}
              </div>
            ) : (
              /* Non-authenticated CTAs */
              <div className="flex items-center gap-2">
                <button
                  onClick={() => onOpenAuth('signin')}
                  className="px-3.5 py-2 text-xs font-bold text-slate-700 dark:text-slate-200 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
                >
                  Log In
                </button>
                <button
                  onClick={() => onOpenAuth('signup')}
                  className="px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-xs font-bold shadow-md shadow-indigo-500/20 flex items-center gap-1.5 transition-all hover:scale-[1.02] active:scale-[0.98]"
                >
                  <span>Start Free</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            )}

            {/* Mobile Hamburger Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="md:hidden px-4 pt-2 pb-5 space-y-2 border-t border-slate-200 dark:border-slate-800 bg-white/95 dark:bg-slate-900/95 backdrop-blur-lg">
            <a
              href="#how-it-works"
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 rounded-lg text-sm font-semibold text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800"
            >
              How It Works
            </a>
            <a
              href="#features"
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 rounded-lg text-sm font-semibold text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800"
            >
              Features
            </a>
            <a
              href="#live-demo"
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 rounded-lg text-sm font-semibold text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800"
            >
              Interactive Demo
            </a>
            <a
              href="#pricing"
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 rounded-lg text-sm font-semibold text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800"
            >
              Pricing Plans
            </a>
            <button
              onClick={() => {
                setMobileMenuOpen(false);
                onNavigateApp('extension');
              }}
              className="w-full text-left px-3 py-2 rounded-lg text-sm font-semibold text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-950/50 flex items-center gap-2"
            >
              <Puzzle className="w-4 h-4" />
              <span>Download Chrome Extension</span>
            </button>

            {user ? (
              <div className="pt-2 border-t border-slate-100 dark:border-slate-800 space-y-2">
                <button
                  onClick={() => {
                    setMobileMenuOpen(false);
                    onNavigateApp('dashboard');
                  }}
                  className="w-full py-2.5 rounded-xl bg-indigo-600 text-white font-bold text-xs text-center flex items-center justify-center gap-2"
                >
                  <LayoutDashboard className="w-4 h-4" />
                  <span>Launch Web Dashboard</span>
                </button>
              </div>
            ) : (
              <div className="pt-2 border-t border-slate-100 dark:border-slate-800 grid grid-cols-2 gap-2">
                <button
                  onClick={() => {
                    setMobileMenuOpen(false);
                    onOpenAuth('signin');
                  }}
                  className="py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-200 font-bold text-xs text-center"
                >
                  Sign In
                </button>
                <button
                  onClick={() => {
                    setMobileMenuOpen(false);
                    onOpenAuth('signup');
                  }}
                  className="py-2.5 rounded-xl bg-indigo-600 text-white font-bold text-xs text-center"
                >
                  Get Started
                </button>
              </div>
            )}
          </div>
        )}
      </nav>
    </header>
  );
};
