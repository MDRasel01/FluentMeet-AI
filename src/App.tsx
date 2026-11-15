import React, { useState, useEffect, Suspense, lazy } from 'react';
import { DashboardApp } from '../apps/dashboard/DashboardApp';
import { ExtensionApp } from '../apps/extension/ExtensionApp';
import { AdminApp } from '../apps/admin/AdminApp';
import { LandingPage } from './features/landing/LandingPage';
import { useAuth } from './features/landing/useAuth';
import { AuthMode, AuthUser } from './features/landing/types';
import { sanitizeInternalRedirect } from './lib/validation';
import { NotFoundPage } from './features/founder/NotFoundPage';
import { Download, ExternalLink } from 'lucide-react';

// Lazy-load founder modules only after owner verification passes
// Hard Rule (§0): Non-owner users must never receive founder markup, data or bundles
const FounderLayout = lazy(() =>
  import('./features/founder/FounderLayout').then((m) => ({ default: m.FounderLayout }))
);
const DesignSystemShowcase = lazy(() =>
  import('./features/founder/DesignSystemShowcase').then((m) => ({ default: m.DesignSystemShowcase }))
);
const ForcePasswordChangeModal = lazy(() =>
  import('./features/founder/ForcePasswordChangeModal').then((m) => ({ default: m.ForcePasswordChangeModal }))
);

type ActiveApp = 'landing' | 'dashboard' | 'extension' | 'admin' | 'design-system';
type ViewRoute = 'public' | 'founder' | 'not-found';

export const App: React.FC = () => {
  const auth = useAuth();
  const [activeApp, setActiveApp] = useState<ActiveApp>('landing');
  const [dashboardPage, setDashboardPage] = useState<string>('overview');
  const [isDark, setIsDark] = useState<boolean>(false);
  const [isDemoMode, setIsDemoMode] = useState<boolean>(true);
  const [currentRoute, setCurrentRoute] = useState<ViewRoute>('public');

  // Central Auth & Navigation State
  const [authModalOpen, setAuthModalOpen] = useState<boolean>(false);
  const [authModalMode, setAuthModalMode] = useState<AuthMode>('signin');
  const [noticeMessage, setNoticeMessage] = useState<string | null>(null);
  const [pendingDestination, setPendingDestination] = useState<'dashboard' | 'extension' | 'founder' | null>(null);
  const [forcePasswordModalOpen, setForcePasswordModalOpen] = useState<boolean>(false);

  // Theme Sync
  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);

  // Route & URL Guard Inspection
  useEffect(() => {
    try {
      if (typeof window === 'undefined') return;
      const pathname = window.location.pathname.toLowerCase();
      const params = new URLSearchParams(window.location.search);
      const redirectParam = params.get('redirect');
      const appQuery = params.get('app');

      // 1. Direct /founder/* route navigation check
      if (pathname.startsWith('/founder')) {
        if (!auth.user) {
          // Unauthenticated: return 404 (not 403) to hide route existence
          setCurrentRoute('not-found');
          return;
        }
        if (!auth.isOwner) {
          // Authenticated non-owner: return 404 (not 403)
          setCurrentRoute('not-found');
          return;
        }

        // Authenticated owner: grant founder area
        setCurrentRoute('founder');
        if (pathname.includes('/design-system')) {
          setActiveApp('design-system');
        } else if (pathname.includes('/admin')) {
          setActiveApp('admin');
        } else if (pathname.includes('/extension')) {
          setActiveApp('extension');
        } else {
          setActiveApp('dashboard');
        }
        return;
      }

      // 2. Safe Redirect & App Param Handling
      if (redirectParam) {
        const safeTarget = sanitizeInternalRedirect(redirectParam);
        if (auth.user) {
          if (auth.isOwner && safeTarget.includes('founder')) {
            setCurrentRoute('founder');
            setActiveApp('dashboard');
          } else if (safeTarget.includes('extension')) {
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
  }, [auth.user, auth.isOwner]);

  // Route Guard: enforce that protected apps require an active session
  useEffect(() => {
    if (activeApp !== 'landing' && currentRoute === 'public' && !auth.user) {
      const attempted = activeApp;
      setActiveApp('landing');
      setPendingDestination(attempted === 'extension' ? 'extension' : 'dashboard');
      setNoticeMessage(`Authentication required. Please sign in to access ${attempted === 'extension' ? 'the Chrome Extension' : 'your dashboard'}.`);
      setAuthModalMode('signin');
      setAuthModalOpen(true);
    } else if (activeApp === 'admin' && currentRoute === 'public' && auth.user && !auth.isOwner && auth.user.role !== 'admin') {
      alert('Access Denied: Founder or Admin credentials required for Admin Panel.');
      setActiveApp('dashboard');
    }
  }, [activeApp, currentRoute, auth.user, auth.isOwner]);

  /**
   * Central Gated CTA Action Handler (/go/dashboard)
   * All CTAs route through here.
   */
  const handleGatedAction = (
    destination: 'dashboard' | 'extension',
    preferredMode: 'signin' | 'signup' = 'signin'
  ) => {
    if (auth.user) {
      if (destination === 'dashboard') {
        if (auth.isOwner) {
          setCurrentRoute('founder');
          setActiveApp('dashboard');
        } else {
          setCurrentRoute('public');
          setDashboardPage('overview');
          setActiveApp('dashboard');
        }
      } else if (destination === 'extension') {
        if (auth.isOwner) {
          setCurrentRoute('founder');
          setActiveApp('extension');
        } else {
          setDashboardPage('chrome-extension');
          setActiveApp('dashboard');
        }
      }
    } else {
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
   * On successful authentication:
   * Owner -> /founder; otherwise -> /dashboard.
   * If mustChangePassword is true -> prompt password update.
   */
  const handleAuthSuccess = (authenticatedUser: AuthUser) => {
    setAuthModalOpen(false);
    setNoticeMessage(null);
    const dest = pendingDestination || 'dashboard';
    setPendingDestination(null);

    if (authenticatedUser.mustChangePassword) {
      setForcePasswordModalOpen(true);
    }

    if (authenticatedUser.role === 'owner') {
      setCurrentRoute('founder');
      if (dest === 'extension') {
        setActiveApp('extension');
      } else {
        setDashboardPage('overview');
        setActiveApp('dashboard');
      }
    } else {
      setCurrentRoute('public');
      const safeTarget = sanitizeInternalRedirect('/' + dest);
      if (safeTarget.includes('extension')) {
        setDashboardPage('chrome-extension');
        setActiveApp('dashboard');
      } else {
        setDashboardPage('overview');
        setActiveApp('dashboard');
      }
    }
  };

  const handleOpenAuth = (mode: AuthMode = 'signin', notice?: string) => {
    setAuthModalMode(mode);
    setNoticeMessage(notice || null);
    setAuthModalOpen(true);
  };

  // 1. If 404 Route triggered (unauthorized attempt on /founder/*)
  if (currentRoute === 'not-found') {
    return (
      <NotFoundPage
        onGoHome={() => {
          setCurrentRoute('public');
          setActiveApp('landing');
          if (typeof window !== 'undefined' && window.history) {
            window.history.pushState({}, '', '/');
          }
        }}
      />
    );
  }

  // 2. If Founder Route (/founder/*) active for verified owner
  if (currentRoute === 'founder' && auth.isOwner) {
    return (
      <Suspense fallback={<div className="min-h-screen bg-slate-950 flex items-center justify-center text-xs text-slate-500 font-mono">Loading Founder Workbench…</div>}>
        <FounderLayout
          activeSpace={activeApp as any}
          onSelectSpace={(space) => {
            setActiveApp(space as ActiveApp);
            if (space === 'landing') {
              setCurrentRoute('public');
            }
          }}
          isDark={isDark}
          onToggleTheme={() => {
            const next = !isDark;
            setIsDark(next);
            auth.setThemePreference(next ? 'dark' : 'light');
          }}
          isDemoMode={isDemoMode}
          onToggleDemoMode={() => setIsDemoMode(!isDemoMode)}
        >
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
              onCloseAuth={() => setAuthModalOpen(false)}
              onAuthSuccess={handleAuthSuccess}
            />
          )}

          {activeApp === 'dashboard' && (
            <DashboardApp
              key={dashboardPage + String(isDemoMode)}
              initialPage={dashboardPage as any}
              isDark={isDark}
              onToggleTheme={() => setIsDark(!isDark)}
            />
          )}

          {activeApp === 'extension' && (
            <div className="p-8 flex flex-col items-center justify-center min-h-[640px] bg-slate-100 dark:bg-slate-950">
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
            <DesignSystemShowcase />
          )}
        </FounderLayout>

        {/* First Login Forced Password Change Modal */}
        <ForcePasswordChangeModal
          isOpen={forcePasswordModalOpen}
          onSuccess={(newPass) => {
            auth.updatePassword(newPass);
            setForcePasswordModalOpen(false);
          }}
        />
      </Suspense>
    );
  }

  // 3. Public / Regular Member Views (Landing, Dashboard, Auth)
  // Non-owner accounts never render founder markup in the DOM
  return (
    <div className="min-h-screen bg-slate-100 dark:bg-slate-950 flex flex-col font-sans">
      <div className="flex-1 w-full bg-white dark:bg-slate-900 flex flex-col min-h-screen">
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
      </div>

      {/* First Login Forced Password Change Modal (if owner logged in on public view) */}
      <Suspense fallback={null}>
        <ForcePasswordChangeModal
          isOpen={forcePasswordModalOpen}
          onSuccess={(newPass) => {
            auth.updatePassword(newPass);
            setForcePasswordModalOpen(false);
          }}
        />
      </Suspense>
    </div>
  );
};
