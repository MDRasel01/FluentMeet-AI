import React, { useState, useEffect } from 'react';
import { DashboardApp } from '../apps/dashboard/DashboardApp';
import { ExtensionApp } from '../apps/extension/ExtensionApp';
import { AdminApp } from '../apps/admin/AdminApp';
import { LandingPage } from './features/landing/LandingPage';
import { useAuth } from './features/landing/useAuth';
import { AuthMode, AuthUser } from './features/landing/types';
import { sanitizeInternalRedirect } from './lib/validation';
import {
  LayoutDashboard,
  Puzzle,
  ShieldAlert,
  Palette,
  CheckCircle2,
  Moon,
  Sun,
  Sparkles,
  Download,
  ExternalLink,
  Globe,
  Crown
} from 'lucide-react';
import {
  Button,
  Card,
  Badge,
  Input,
  ScoreIndicator,
  AudioPlayer,
  TranscriptSegment,
  GrammarErrorCard,
  PlatformIcon,
  PlatformBadge,
  PlatformSelect,
} from '../design-system/components';

type ActiveApp = 'landing' | 'dashboard' | 'extension' | 'admin' | 'design-system';

export const App: React.FC = () => {
  const auth = useAuth();
  const [activeApp, setActiveApp] = useState<ActiveApp>('landing');
  const [dashboardPage, setDashboardPage] = useState<string>('overview');
  const [isDark, setIsDark] = useState<boolean>(false);
  const [showcasePlatform, setShowcasePlatform] = useState<string>('google-meet');

  // Central Auth & Navigation State
  const [authModalOpen, setAuthModalOpen] = useState<boolean>(false);
  const [authModalMode, setAuthModalMode] = useState<AuthMode>('signin');
  const [noticeMessage, setNoticeMessage] = useState<string | null>(null);
  const [pendingDestination, setPendingDestination] = useState<'dashboard' | 'extension' | null>(null);

  // Theme Sync
  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);

  /**
   * Central Route Guard / Middleware
   * If a user tries to access protected views without an authenticated session,
   * intercept, redirect back to landing, and trigger authentication.
   */
  useEffect(() => {
    if (activeApp !== 'landing' && !auth.user) {
      const attempted = activeApp;
      setActiveApp('landing');
      setPendingDestination(attempted === 'extension' ? 'extension' : 'dashboard');
      setNoticeMessage(`Authentication required. Please sign in to access ${attempted === 'extension' ? 'the Chrome Extension' : 'your dashboard'}.`);
      setAuthModalMode('signin');
      setAuthModalOpen(true);
    } else if (activeApp === 'admin' && auth.user && auth.user.role !== 'owner' && auth.user.role !== 'admin') {
      alert('Access Denied: Founder or Admin credentials required for Admin Panel.');
      setActiveApp('dashboard');
    }
  }, [activeApp, auth.user]);

  /**
   * Browser URL / Parameter Guard & Open-Redirect Protection
   */
  useEffect(() => {
    try {
      if (typeof window === 'undefined') return;
      const params = new URLSearchParams(window.location.search);
      const redirectParam = params.get('redirect');
      const appQuery = params.get('app');

      if (redirectParam) {
        const safeTarget = sanitizeInternalRedirect(redirectParam);
        if (auth.user) {
          if (safeTarget.includes('extension')) {
            setDashboardPage('chrome-extension');
            setActiveApp('dashboard');
          } else {
            setActiveApp('dashboard');
          }
        } else {
          setPendingDestination(safeTarget.includes('extension') ? 'extension' : 'dashboard');
          setNoticeMessage('Please sign in to continue to your requested page.');
          setAuthModalMode('signin');
          setAuthModalOpen(true);
        }
      } else if (appQuery) {
        if (appQuery === 'dashboard' || appQuery === 'extension') {
          if (auth.user) {
            setActiveApp(appQuery);
          } else {
            setPendingDestination(appQuery);
            setNoticeMessage(`Please sign in to open the ${appQuery === 'extension' ? 'Chrome Extension' : 'Web Dashboard'}.`);
            setAuthModalMode('signin');
            setAuthModalOpen(true);
          }
        }
      }
    } catch (e) {
      console.warn('URL guard check skipped:', e);
    }
  }, [auth.user]);

  /**
   * Central Gated CTA Action Handler
   * All dashboard and extension CTAs across the entire application route through here.
   */
  const handleGatedAction = (
    destination: 'dashboard' | 'extension',
    preferredMode: 'signin' | 'signup' = 'signin'
  ) => {
    if (auth.user) {
      // 1. User is authenticated -> proceed directly to destination
      if (destination === 'dashboard') {
        setDashboardPage('overview');
        setActiveApp('dashboard');
      } else if (destination === 'extension') {
        setDashboardPage('chrome-extension');
        setActiveApp('dashboard');
      }
    } else {
      // 2. User is unauthenticated -> gate destination behind AuthModal
      setPendingDestination(destination);
      setNoticeMessage(
        destination === 'extension'
          ? 'Please sign in or create a free account to download the Chrome Extension.'
          : 'Please sign in or create a free account to access your personalized dashboard.'
      );
      setAuthModalMode(preferredMode);
      setAuthModalOpen(true);
    }
  };

  /**
   * On successful authentication, fulfill the user's pending intention
   */
  const handleAuthSuccess = (user: AuthUser) => {
    setAuthModalOpen(false);
    setNoticeMessage(null);
    const destination = pendingDestination || 'dashboard';
    setPendingDestination(null);

    const safeTarget = sanitizeInternalRedirect('/' + destination);
    if (safeTarget.includes('extension')) {
      setDashboardPage('chrome-extension');
      setActiveApp('dashboard');
    } else {
      setDashboardPage('overview');
      setActiveApp('dashboard');
    }
  };

  const handleOpenAuth = (mode: AuthMode = 'signin', notice?: string) => {
    setAuthModalMode(mode);
    setNoticeMessage(notice || null);
    setAuthModalOpen(true);
  };

  return (
    <div className="min-h-screen bg-slate-100 dark:bg-slate-950 flex flex-col font-sans">
      {/* 
        FOUNDER-ONLY WORKBENCH CONTROL BAR ("Step 2 / Workbench / v1.0 Release")
        Strictly guarded: If auth.isOwner is false (or logged out), this component 
        is COMPLETELY ABSENT from the DOM (not hidden by CSS, but null in JSX).
      */}
      {auth.isOwner && (
        <div className="bg-slate-900 text-white px-4 py-2 flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 z-50 text-xs shadow-md">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 font-bold tracking-tight">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
              <span>Step 02 Workbench</span>
              <span className="ml-1.5 px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 font-bold text-[10px] border border-amber-400/30 flex items-center gap-1">
                <Crown className="w-3 h-3 text-amber-400 inline" /> Owner Role
              </span>
            </div>

            <div className="h-4 w-px bg-slate-700" />

            {/* App Switcher Tabs for Founder */}
            <div className="flex items-center bg-slate-800 rounded-lg p-0.5 border border-slate-700">
              <button
                onClick={() => setActiveApp('landing')}
                className={`flex items-center gap-1.5 px-3 py-1 rounded-md transition-colors ${
                  activeApp === 'landing' ? 'bg-indigo-600 text-white font-semibold shadow-sm' : 'text-slate-300 hover:text-white'
                }`}
              >
                <Globe className="w-3.5 h-3.5 text-amber-300" />
                <span>Landing Page</span>
              </button>

              <button
                onClick={() => setActiveApp('dashboard')}
                className={`flex items-center gap-1.5 px-3 py-1 rounded-md transition-colors ${
                  activeApp === 'dashboard' ? 'bg-indigo-600 text-white font-semibold' : 'text-slate-300 hover:text-white'
                }`}
              >
                <LayoutDashboard className="w-3.5 h-3.5" />
                <span>Web Dashboard (21)</span>
              </button>

              <button
                onClick={() => setActiveApp('extension')}
                className={`flex items-center gap-1.5 px-3 py-1 rounded-md transition-colors ${
                  activeApp === 'extension' ? 'bg-indigo-600 text-white font-semibold' : 'text-slate-300 hover:text-white'
                }`}
              >
                <Puzzle className="w-3.5 h-3.5" />
                <span>Chrome Extension (15)</span>
              </button>

              <button
                onClick={() => setActiveApp('admin')}
                className={`flex items-center gap-1.5 px-3 py-1 rounded-md transition-colors ${
                  activeApp === 'admin' ? 'bg-rose-600 text-white font-semibold' : 'text-slate-300 hover:text-white'
                }`}
              >
                <ShieldAlert className="w-3.5 h-3.5" />
                <span>Admin Panel (13)</span>
              </button>

              <button
                onClick={() => setActiveApp('design-system')}
                className={`flex items-center gap-1.5 px-3 py-1 rounded-md transition-colors ${
                  activeApp === 'design-system' ? 'bg-indigo-600 text-white font-semibold' : 'text-slate-300 hover:text-white'
                }`}
              >
                <Palette className="w-3.5 h-3.5" />
                <span>Design System</span>
              </button>
            </div>

            {/* Quick Direct Link to Download Center */}
            <button
              onClick={() => {
                setDashboardPage('chrome-extension');
                setActiveApp('dashboard');
              }}
              className="flex items-center gap-1.5 px-3 py-1 rounded-md transition-colors bg-emerald-600 hover:bg-emerald-500 text-white font-semibold shadow-sm"
              title="Open Chrome Extension Download Center"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download Extension</span>
            </button>
          </div>

          {/* Theme and Status Controls */}
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsDark(!isDark)}
              className="p-1.5 rounded-lg bg-slate-800 border border-slate-700 hover:bg-slate-700 transition-colors"
              title="Toggle Light/Dark Theme"
            >
              {isDark ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-300" />}
            </button>

            {/* Screen Tracker Counter Badge */}
            <div className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-emerald-950/80 border border-emerald-500/50 text-emerald-300 font-bold text-[11px]">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span>49 / 49 Screens Ready</span>
            </div>
          </div>
        </div>
      )}

      {/* Main Full-Width Application Container */}
      <div className="flex-1 w-full bg-white dark:bg-slate-900 flex flex-col min-h-[calc(100vh-48px)]">
        {activeApp === 'landing' && (
          <LandingPage
            isDark={isDark}
            onToggleTheme={() => setIsDark(!isDark)}
            onGatedAction={handleGatedAction}
            auth={auth}
            authModalOpen={authModalOpen}
            authModalMode={authModalMode}
            noticeMessage={noticeMessage}
            onOpenAuth={handleOpenAuth}
            onCloseAuth={() => {
              setAuthModalOpen(false);
              setNoticeMessage(null);
            }}
            onAuthSuccess={handleAuthSuccess}
          />
        )}

        {activeApp === 'dashboard' && (
          <DashboardApp
            key={dashboardPage}
            initialPage={dashboardPage as any}
            isDark={isDark}
            onToggleTheme={() => setIsDark(!isDark)}
          />
        )}

        {activeApp === 'extension' && (
          <div className="p-8 flex flex-col items-center justify-center min-h-[640px] bg-slate-100 dark:bg-slate-950">
            {/* Direct Download Banner for users on the Simulator view */}
            <div className="w-full max-w-md mb-6 bg-gradient-to-r from-indigo-50 to-blue-50 dark:from-indigo-950/60 dark:to-slate-900 border border-indigo-200 dark:border-indigo-800 rounded-2xl p-4 shadow-sm flex items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <div className="p-2.5 bg-indigo-600 text-white rounded-xl shadow-sm shrink-0">
                  <Download className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">
                    Need the installable Extension?
                  </h3>
                  <p className="text-xs text-slate-600 dark:text-slate-400">
                    Download v1.0.0 ZIP or Load Unpacked in Chrome
                  </p>
                </div>
              </div>
              <button
                onClick={() => {
                  setDashboardPage('chrome-extension');
                  setActiveApp('dashboard');
                }}
                className="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-lg shadow-sm transition-all flex items-center gap-1.5 shrink-0"
              >
                <span>Download Page</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="text-center mb-4">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
                Chrome Extension Simulator (Manifest V3 Side Panel API)
              </span>
              <p className="text-xs text-slate-500">
                Operates at 360–400px fixed width in browser side panel without blocking video calls
              </p>
            </div>
            <ExtensionApp isDark={isDark} />
          </div>
        )}

        {activeApp === 'admin' && (
          <AdminApp isDark={isDark} />
        )}

        {activeApp === 'design-system' && (
          <div className="p-8 max-w-5xl mx-auto space-y-8">
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
                Design System Component Showcase
              </h1>
              <p className="text-xs text-slate-500 mt-1">
                Living component library adhering to 4px spacing, CSS tokens, and WCAG 2.1 AA accessibility standards
              </p>
            </div>

            {/* Color Tokens Showcase */}
            <Card className="space-y-4">
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Primary & Semantic Tokens</h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-3 text-xs">
                <div className="p-3 rounded-lg bg-indigo-600 text-white font-medium text-center">Primary 500 (#6366F1)</div>
                <div className="p-3 rounded-lg bg-indigo-700 text-white font-medium text-center">Primary 600 (#4F46E5)</div>
                <div className="p-3 rounded-lg bg-emerald-600 text-white font-medium text-center">Success (#16A34A)</div>
                <div className="p-3 rounded-lg bg-amber-600 text-white font-medium text-center">Warning (#D97706)</div>
                <div className="p-3 rounded-lg bg-rose-600 text-white font-medium text-center">Danger (#DC2626)</div>
                <div className="p-3 rounded-lg bg-sky-600 text-white font-medium text-center">Info (#2563EB)</div>
              </div>
            </Card>

            {/* Buttons Showcase */}
            <Card className="space-y-4">
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Buttons & States</h3>
              <div className="flex flex-wrap items-center gap-3">
                <Button variant="primary">Primary</Button>
                <Button variant="secondary">Secondary</Button>
                <Button variant="outline">Outline</Button>
                <Button variant="ghost">Ghost</Button>
                <Button variant="destructive">Destructive</Button>
                <Button variant="primary" disabled>Disabled</Button>
              </div>
            </Card>

            {/* Score Indicators Showcase */}
            <Card className="space-y-4">
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white">CEFR Fluency Score Indicators</h3>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4">
                <ScoreIndicator score={42} label="A2 Elementary" size="md" />
                <ScoreIndicator score={58} label="B1 Intermediate" size="md" />
                <ScoreIndicator score={74} label="B2 Upper Int" size="md" />
                <ScoreIndicator score={86} label="C1 Advanced" size="md" />
                <ScoreIndicator score={95} label="C2 Mastery" size="md" />
                <ScoreIndicator score={88} label="Overall Score" size="lg" />
              </div>
            </Card>

            {/* Platform Indicators Showcase */}
            <Card className="space-y-4">
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Platform Indicators & Dropdowns</h3>
              <div className="flex flex-wrap items-center gap-4">
                <PlatformBadge platform="google-meet" />
                <PlatformBadge platform="zoom" />
                <PlatformBadge platform="teams" />
                <div className="w-56">
                  <PlatformSelect
                    value={showcasePlatform}
                    onChange={setShowcasePlatform}
                  />
                </div>
              </div>
            </Card>

            {/* Live Audio Transcript Segment Showcase */}
            <Card className="space-y-4">
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Transcript & Mistake Highlighting</h3>
              <div className="space-y-3">
                <TranscriptSegment
                  speakerName="Alex Chen"
                  timestamp="04:12"
                  text="We should discuss about the budget allocation before deployment."
                />
                <GrammarErrorCard
                  errorCategory="Preposition redundancy"
                  originalSentence="We should discuss about the budget."
                  correctedSentence="We should discuss the budget."
                  explanation="'Discuss' is a transitive verb that directly takes an object. Do not use 'about'."
                />
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};
