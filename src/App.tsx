import React, { useState, useEffect } from 'react';
import { DashboardApp } from '../apps/dashboard/DashboardApp';
import { ExtensionApp } from '../apps/extension/ExtensionApp';
import { AdminApp } from '../apps/admin/AdminApp';
import { LandingPage } from './features/landing/LandingPage';
import {
  LayoutDashboard,
  Puzzle,
  ShieldAlert,
  Palette,
  Monitor,
  Smartphone,
  Tablet,
  CheckCircle2,
  Moon,
  Sun,
  Sparkles,
  Download,
  ExternalLink,
  Globe
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
  const [activeApp, setActiveApp] = useState<ActiveApp>('landing');
  const [dashboardPage, setDashboardPage] = useState<string>('overview');
  const [viewportWidth, setViewportWidth] = useState<string>('100%');
  const [isDark, setIsDark] = useState<boolean>(false);
  const [showcasePlatform, setShowcasePlatform] = useState<string>('google-meet');

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);

  return (
    <div className="min-h-screen bg-slate-100 dark:bg-slate-950 flex flex-col font-sans">
      {/* Top Universal Workbench Control Bar */}
      <div className="bg-slate-900 text-white px-4 py-2 flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 z-50 text-xs shadow-md">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 font-bold tracking-tight">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
            <span>Step 02 Workbench</span>
          </div>

          <div className="h-4 w-px bg-slate-700" />

          {/* App Switcher Tabs */}
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

        {/* Viewport & Theme Resizer Controls */}
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-1 bg-slate-800 rounded-lg p-0.5 border border-slate-700 text-[11px]">
            <span className="px-2 text-slate-400">Viewport:</span>
            {[
              { label: '320px', width: '320px', icon: <Smartphone className="w-3 h-3" /> },
              { label: '375px', width: '375px', icon: <Smartphone className="w-3 h-3" /> },
              { label: '430px', width: '430px', icon: <Smartphone className="w-3 h-3" /> },
              { label: '768px', width: '768px', icon: <Tablet className="w-3 h-3" /> },
              { label: '1024px', width: '1024px', icon: <Monitor className="w-3 h-3" /> },
              { label: '1280px', width: '1280px', icon: <Monitor className="w-3 h-3" /> },
              { label: '1440px', width: '1440px', icon: <Monitor className="w-3 h-3" /> },
              { label: 'Fluid', width: '100%', icon: <Monitor className="w-3 h-3" /> },
            ].map((vp) => (
              <button
                key={vp.label}
                onClick={() => setViewportWidth(vp.width)}
                className={`px-2 py-0.5 rounded transition-colors flex items-center gap-1 ${
                  viewportWidth === vp.width ? 'bg-slate-700 text-white font-bold' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {vp.label}
              </button>
            ))}
          </div>

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

      {/* Main Viewport Container */}
      <div className="flex-1 overflow-auto flex items-start justify-center p-0 sm:p-2 bg-slate-200/60 dark:bg-slate-950">
        <div
          className="transition-all duration-300 bg-white dark:bg-slate-900 shadow-2xl rounded-none sm:rounded-xl overflow-hidden min-h-[calc(100vh-60px)]"
          style={{ width: viewportWidth, maxWidth: '100%' }}
        >
          {activeApp === 'landing' && (
            <LandingPage
              isDark={isDark}
              onToggleTheme={() => setIsDark(!isDark)}
              onNavigateApp={(app) => {
                if (app === 'dashboard') {
                  setDashboardPage('overview');
                  setActiveApp('dashboard');
                } else if (app === 'extension') {
                  setDashboardPage('chrome-extension');
                  setActiveApp('dashboard');
                }
              }}
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
                  <Button variant="primary" loading>Loading</Button>
                  <Button variant="primary" disabled>Disabled</Button>
                </div>
              </Card>

              {/* Inputs Showcase */}
              <Card className="space-y-4">
                <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Form Inputs</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Input label="Standard Input" placeholder="Type here..." />
                  <Input label="With Helper Text" placeholder="example@domain.com" helperText="We never share your email." />
                  <Input label="With Error State" defaultValue="invalid text" error="Invalid format" />
                </div>
              </Card>

              {/* Score Indicators Showcase */}
              <Card className="space-y-4">
                <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Score Indicators</h3>
                <div className="flex items-center gap-6">
                  <ScoreIndicator score={92} size="md" label="C2 Mastery" />
                  <ScoreIndicator score={81} size="md" label="C1 Proficient" />
                  <ScoreIndicator score={64} size="md" label="B2 Intermediate" />
                  <ScoreIndicator score={42} size="md" label="B1 Basic" />
                  <ScoreIndicator score={0} insufficientData size="md" label="Insufficient Data" />
                </div>
              </Card>

              {/* Audio Player Component */}
              <Card className="space-y-4">
                <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Audio Player & Waveform Sync</h3>
                <AudioPlayer currentTime={252} duration={2520} />
              </Card>

              {/* 3D Platform Icons & Platform Select Component */}
              <Card className="space-y-6">
                <div>
                  <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
                    3D Platform Icons & Platform Selectors
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    High-definition 3D vector platform icons with volumetric depth, authentic brand gradients, and interactive selection states
                  </p>
                </div>

                {/* 3D Icons Showcase */}
                <div className="space-y-3">
                  <span className="text-xs font-bold text-slate-700 dark:text-slate-300 block uppercase tracking-wider">
                    High-Definition 3D Brand Icons (All Sizes):
                  </span>
                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
                    {[
                      { id: 'google-meet', name: 'Google Meet', desc: 'Emerald & Google quaternary 3D camera' },
                      { id: 'zoom', name: 'Zoom Web', desc: 'Oceanic blue glossy squircle with bevel' },
                      { id: 'teams', name: 'Microsoft Teams', desc: 'Layered violet tiles & embossed 3D T' },
                      { id: 'all', name: 'All Platforms', desc: 'Universal holographic multi-ring sphere' },
                    ].map((p) => (
                      <div
                        key={p.id}
                        className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 space-y-3 text-center"
                      >
                        <div className="flex items-center justify-center py-2">
                          <PlatformIcon platform={p.id} size="xl" />
                        </div>
                        <div>
                          <span className="text-xs font-bold text-slate-900 dark:text-white block">{p.name}</span>
                          <span className="text-[10px] text-slate-400 block">{p.desc}</span>
                        </div>
                        <div className="flex items-center justify-center gap-2 pt-1 border-t border-slate-200 dark:border-slate-800">
                          <PlatformIcon platform={p.id} size="xs" />
                          <PlatformIcon platform={p.id} size="sm" />
                          <PlatformIcon platform={p.id} size="md" />
                          <PlatformIcon platform={p.id} size="lg" />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Interactive PlatformSelect Components */}
                <div className="space-y-4 pt-2 border-t border-slate-200 dark:border-slate-800">
                  <span className="text-xs font-bold text-slate-700 dark:text-slate-300 block uppercase tracking-wider">
                    Interactive Select Variants:
                  </span>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <span className="text-xs font-semibold text-slate-500 block">Pill / Segmented Tabs Variant:</span>
                      <PlatformSelect
                        value={showcasePlatform}
                        onChange={setShowcasePlatform}
                        variant="pills"
                        size="md"
                      />
                    </div>
                    <div className="space-y-2">
                      <span className="text-xs font-semibold text-slate-500 block">Floating Dropdown Select Variant:</span>
                      <PlatformSelect
                        value={showcasePlatform}
                        onChange={setShowcasePlatform}
                        variant="dropdown"
                        size="md"
                      />
                    </div>
                  </div>
                </div>

                {/* Platform Badges */}
                <div className="space-y-2 pt-2 border-t border-slate-200 dark:border-slate-800">
                  <span className="text-xs font-bold text-slate-700 dark:text-slate-300 block uppercase tracking-wider">
                    Platform Badges with 3D Icons:
                  </span>
                  <div className="flex flex-wrap items-center gap-3">
                    <PlatformBadge platform="google-meet" size="md" />
                    <PlatformBadge platform="zoom" size="md" />
                    <PlatformBadge platform="teams" size="md" />
                    <PlatformBadge platform="all" size="md" />
                  </div>
                </div>
              </Card>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
