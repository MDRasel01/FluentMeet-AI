import React, { useEffect } from 'react';
import {
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  Play,
  Pause,
  Square,
  Users,
  Mic,
  Volume2,
  Shield,
  Settings,
  Lock,
  XCircle,
  HelpCircle,
  Radio,
  WifiOff
} from 'lucide-react';
import { Button, Input, Card, Badge } from '../../design-system/components';
import { useExtensionStore } from './src/sidepanel/store/extension-store';

export type ExtensionScreen =
  | 'auth'
  | 'home'
  | 'detected'
  | 'participant-list'
  | 'consent'
  | 'live'
  | 'paused'
  | 'processing'
  | 'completed'
  | 'error-permission'
  | 'error-audio'
  | 'error-connection'
  | 'error-unsupported'
  | 'error-interrupted'
  | 'settings';

interface ExtensionAppProps {
  initialScreen?: ExtensionScreen;
  onScreenChange?: (screen: ExtensionScreen) => void;
  isDark?: boolean;
}

export const ExtensionApp: React.FC<ExtensionAppProps> = ({
  initialScreen,
  onScreenChange,
  isDark = false,
}) => {
  const store = useExtensionStore();

  const currentScreen = initialScreen || store.screen;
  const setScreen = (s: ExtensionScreen) => {
    store.setScreen(s);
    if (onScreenChange) onScreenChange(s);
  };

  useEffect(() => {
    store.initializeExtension();
  }, []);

  // Timer ticker during active live session
  useEffect(() => {
    let interval: number;
    if (currentScreen === 'live') {
      interval = window.setInterval(() => {
        useExtensionStore.setState((prev) => ({ sessionSeconds: prev.sessionSeconds + 1 }));
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [currentScreen]);

  const formatTimer = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="w-full max-w-[400px] h-[640px] bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-xl flex flex-col overflow-hidden text-slate-900 dark:text-slate-100 antialiased mx-auto">
      {/* Chrome Side Panel Header */}
      <div className="p-3.5 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-md bg-indigo-600 text-white flex items-center justify-center font-bold text-xs">
            <Sparkles className="w-3.5 h-3.5" />
          </div>
          <span className="text-xs font-bold tracking-tight text-slate-900 dark:text-white">
            Meeting Coach SidePanel
          </span>
        </div>

        <div className="flex items-center gap-1.5">
          <Badge variant="primary" size="sm">v1.0.2</Badge>
          <button
            onClick={() => setScreen('settings')}
            className="p-1 rounded text-slate-400 hover:text-slate-700 dark:hover:text-slate-200"
            title="Extension Settings"
          >
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Screen Quick Selector for Design Testing */}
      <div className="bg-slate-100 dark:bg-slate-800/80 px-2 py-1.5 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between text-[10px]">
        <span className="font-semibold text-slate-500 uppercase tracking-wider">Screen Preview:</span>
        <select
          value={currentScreen}
          onChange={(e) => setScreen(e.target.value as ExtensionScreen)}
          className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded px-1.5 py-0.5 text-[11px] font-medium"
        >
          <option value="auth">1. Authentication</option>
          <option value="home">2. Home / Ready</option>
          <option value="detected">3. Meeting Detected</option>
          <option value="participant-list">4. Participant List</option>
          <option value="consent">5. Consent Confirmation</option>
          <option value="live">6. Live Session</option>
          <option value="paused">7. Paused Session</option>
          <option value="processing">8. Processing</option>
          <option value="completed">9. Completed</option>
          <option value="error-permission">10. Permission Denied</option>
          <option value="error-audio">11. Audio Capture Error</option>
          <option value="error-connection">12. Connection Lost</option>
          <option value="error-unsupported">13. Unsupported Platform</option>
          <option value="error-interrupted">14. Session Interrupted</option>
          <option value="settings">15. Settings</option>
        </select>
      </div>

      {/* Main Body per Screen */}
      <div className="flex-1 p-4 overflow-y-auto flex flex-col justify-between">
        {/* SCREEN 01: AUTH */}
        {currentScreen === 'auth' && (
          <div className="space-y-4 my-auto">
            <div className="text-center space-y-1">
              <div className="w-12 h-12 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mx-auto mb-2">
                <Lock className="w-6 h-6" />
              </div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white">Sign In to Continue</h3>
              <p className="text-xs text-slate-500">Pair with your AI Meeting English Coach SaaS account</p>
            </div>

            <div className="space-y-3">
              <Input label="Email Address" defaultValue="priya.sharma@acme.com" />
              <Input label="Password" type="password" defaultValue="••••••••••••" />
              <Button fullWidth size="sm" onClick={() => setScreen('home')}>
                Authenticate Extension
              </Button>
            </div>

            <p className="text-center text-[11px] text-slate-400">
              Need an account? <span className="text-indigo-600 font-semibold cursor-pointer">Register on Web</span>
            </p>
          </div>
        )}

        {/* SCREEN 02: HOME / READY */}
        {currentScreen === 'home' && (
          <div className="space-y-5 my-auto text-center">
            <div className="w-14 h-14 rounded-2xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center mx-auto text-slate-400">
              <Radio className="w-7 h-7 animate-pulse text-indigo-600" />
            </div>

            <div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white">
                Waiting for Online Meeting
              </h3>
              <p className="text-xs text-slate-500 mt-1 leading-relaxed max-w-xs mx-auto">
                Join a meeting on Google Meet, Zoom Web, or Microsoft Teams. Analysis will arm automatically.
              </p>
            </div>

            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-left space-y-1.5 text-xs">
              <span className="font-bold text-slate-700 dark:text-slate-300 block text-[11px] uppercase">Supported URLs:</span>
              <p className="text-slate-500 font-mono text-[11px]">• meet.google.com/*</p>
              <p className="text-slate-500 font-mono text-[11px]">• app.zoom.us/wc/*</p>
              <p className="text-slate-500 font-mono text-[11px]">• teams.microsoft.com/*</p>
            </div>

            <Button size="sm" variant="outline" fullWidth onClick={() => setScreen('detected')}>
              Simulate Meeting Join →
            </Button>
          </div>
        )}

        {/* SCREEN 03: MEETING DETECTED */}
        {currentScreen === 'detected' && (
          <div className="space-y-4">
            <div className="p-3.5 rounded-xl bg-indigo-50/80 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-900 space-y-1">
              <div className="flex items-center justify-between">
                <Badge variant="primary" size="sm">
                  {store.platform === 'google-meet' ? 'Google Meet' : store.platform === 'zoom' ? 'Zoom Web' : 'MS Teams'} Detected
                </Badge>
                <span className="text-[11px] font-mono text-indigo-700 dark:text-indigo-400">
                  {store.platform === 'google-meet' ? 'meet.google.com' : store.platform === 'zoom' ? 'zoom.us' : 'teams.microsoft.com'}
                </span>
              </div>
              <h4 className="text-sm font-bold text-slate-900 dark:text-white pt-1">
                {store.meetingTitle}
              </h4>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs font-semibold text-slate-500">
                <span>Discovered Participants ({store.participants.length || 3})</span>
                <span className="text-indigo-600 cursor-pointer" onClick={() => setScreen('participant-list')}>
                  View All
                </span>
              </div>
              <div className="p-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 space-y-2 text-xs">
                <div className="flex items-center gap-2">
                  <div className="w-5 h-5 rounded-full bg-indigo-600 text-white font-bold text-[10px] flex items-center justify-center">P</div>
                  <span className="font-medium text-slate-800 dark:text-slate-200">Priya Sharma (You)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-5 h-5 rounded-full bg-emerald-500 text-white font-bold text-[10px] flex items-center justify-center">A</div>
                  <span className="font-medium text-slate-800 dark:text-slate-200">Alex Miller</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-5 h-5 rounded-full bg-amber-500 text-white font-bold text-[10px] flex items-center justify-center">D</div>
                  <span className="font-medium text-slate-800 dark:text-slate-200">David Chen</span>
                </div>
              </div>
            </div>

            {/* Mandatory Consent Box */}
            <div className="p-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-2">
              <label className="flex items-start gap-2.5 text-xs text-slate-700 dark:text-slate-300 cursor-pointer">
                <input
                  type="checkbox"
                  checked={store.consentChecked}
                  onChange={(e) => store.setConsentChecked(e.target.checked)}
                  className="mt-0.5 rounded text-indigo-600 focus:ring-indigo-500"
                />
                <span className="leading-tight">
                  I confirm that all call participants have consented to AI audio analysis.
                </span>
              </label>
            </div>

            <Button
              fullWidth
              size="md"
              disabled={!store.consentChecked}
              onClick={() => store.startCapture()}
            >
              Start Analysis Session
            </Button>
          </div>
        )}

        {/* SCREEN 04: PARTICIPANT LIST */}
        {currentScreen === 'participant-list' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-2">
              <h3 className="text-sm font-bold text-slate-900 dark:text-white">Active Roster ({store.participants.length || 4})</h3>
              <Button variant="ghost" size="sm" onClick={() => setScreen('detected')}>Back</Button>
            </div>
            <div className="space-y-2 text-xs">
              {[
                { name: 'Priya Sharma (You)', role: 'Local Speaker', mic: true },
                { name: 'Alex Miller', role: 'Remote Participant', mic: false },
                { name: 'David Chen', role: 'Remote Participant', mic: true },
                { name: 'Sarah Jenkins', role: 'Remote Participant', mic: false },
              ].map((p, i) => (
                <div key={i} className="p-2.5 rounded-lg border border-slate-200 dark:border-slate-800 flex items-center justify-between">
                  <div>
                    <span className="font-bold text-slate-800 dark:text-slate-200 block">{p.name}</span>
                    <span className="text-[10px] text-slate-400">{p.role}</span>
                  </div>
                  <Badge variant={p.mic ? 'success' : 'neutral'} size="sm">
                    {p.mic ? 'Speaking' : 'Muted'}
                  </Badge>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* SCREEN 05: CONSENT CONFIRMATION */}
        {currentScreen === 'consent' && (
          <div className="space-y-4 my-auto text-center">
            <div className="w-12 h-12 rounded-xl bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400 flex items-center justify-center mx-auto">
              <Shield className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-bold">Two-Party Consent Mandate</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Recording laws require all participants to be notified before capturing audio.
            </p>
            <Button fullWidth size="sm" onClick={() => setScreen('detected')}>
              I Understand & Agree
            </Button>
          </div>
        )}

        {/* SCREEN 06: LIVE SESSION */}
        {currentScreen === 'live' && (
          <div className="space-y-5">
            {/* Live Indicator & Timer */}
            <div className="p-4 rounded-xl bg-rose-50/80 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-900 text-center space-y-1">
              <div className="inline-flex items-center gap-2 text-xs font-bold text-rose-600 dark:text-rose-400 uppercase tracking-wider">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-600 animate-ping" />
                Live Recording Active
              </div>
              <span className="text-3xl font-black font-mono text-slate-900 dark:text-white block tabular-nums">
                {formatTimer(store.sessionSeconds || 868)}
              </span>
            </div>

            {/* Dual Audio VU Meters */}
            <div className="p-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 space-y-3">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                Dual-Track Audio Signal Health
              </span>

              {/* Your Mic */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs font-medium">
                  <span className="flex items-center gap-1.5 text-slate-700 dark:text-slate-300">
                    <Mic className="w-3.5 h-3.5 text-emerald-600" /> Your Microphone
                  </span>
                  <span className="font-mono text-slate-500">{store.micVolume}%</span>
                </div>
                <div className="w-full h-2 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-emerald-500 rounded-full transition-all duration-150" style={{ width: `${store.micVolume}%` }} />
                </div>
              </div>

              {/* Tab Audio */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs font-medium">
                  <span className="flex items-center gap-1.5 text-slate-700 dark:text-slate-300">
                    <Volume2 className="w-3.5 h-3.5 text-indigo-600" /> Meeting Tab Audio
                  </span>
                  <span className="font-mono text-slate-500">{store.tabVolume}%</span>
                </div>
                <div className="w-full h-2 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-indigo-600 rounded-full transition-all duration-150" style={{ width: `${store.tabVolume}%` }} />
                </div>
              </div>
            </div>

            {/* Session Controls */}
            <div className="grid grid-cols-2 gap-3 pt-2">
              <Button
                variant="outline"
                size="sm"
                leadingIcon={<Pause className="w-3.5 h-3.5" />}
                onClick={() => store.pauseCapture()}
              >
                Pause Session
              </Button>
              <Button
                variant="destructive"
                size="sm"
                leadingIcon={<Square className="w-3.5 h-3.5" />}
                onClick={() => store.stopCapture()}
              >
                Stop & Analyze
              </Button>
            </div>
          </div>
        )}

        {/* SCREEN 07: PAUSED SESSION */}
        {currentScreen === 'paused' && (
          <div className="space-y-5 text-center my-auto">
            <div className="w-12 h-12 rounded-full bg-amber-100 dark:bg-amber-950/60 text-amber-600 flex items-center justify-center mx-auto">
              <Pause className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-amber-800 dark:text-amber-300">Recording Paused</h3>
              <p className="text-xs text-slate-500 mt-1">Audio buffering is suspended</p>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <Button size="sm" onClick={() => store.resumeCapture()}>
                Resume
              </Button>
              <Button size="sm" variant="destructive" onClick={() => store.stopCapture()}>
                Stop & Process
              </Button>
            </div>
          </div>
        )}

        {/* SCREEN 08: PROCESSING */}
        {currentScreen === 'processing' && (
          <div className="space-y-5 text-center my-auto">
            <div className="w-14 h-14 rounded-full border-4 border-indigo-200 border-t-indigo-600 animate-spin mx-auto" />
            <div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white">Analyzing Meeting Speech...</h3>
              <p className="text-xs text-slate-500 mt-1">Stage 2 of 3: Speaker Diarization & Gemini AI Evaluation</p>
            </div>
            <p className="text-[11px] text-slate-400">
              You can close this side panel. We will notify you once your report is ready.
            </p>
            <Button size="sm" variant="outline" fullWidth onClick={() => setScreen('completed')}>
              View Finished Report
            </Button>
          </div>
        )}

        {/* SCREEN 09: COMPLETED */}
        {currentScreen === 'completed' && (
          <div className="space-y-5 text-center my-auto">
            <div className="w-12 h-12 rounded-full bg-emerald-100 dark:bg-emerald-950/60 text-emerald-600 flex items-center justify-center mx-auto">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white">Analysis Ready!</h3>
              <p className="text-xs text-slate-500 mt-1">Spoken English Score: 82 / 100 (Proficient)</p>
            </div>
            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs text-left space-y-1">
              <p className="text-slate-700 dark:text-slate-300">• 4 Grammar suggestions identified</p>
              <p className="text-slate-700 dark:text-slate-300">• 3 Executive vocabulary upgrades</p>
              <p className="text-slate-700 dark:text-slate-300">• 142 WPM Pacing (Optimal)</p>
            </div>
            <Button size="md" fullWidth onClick={() => alert(`Opens Web Dashboard for session: ${store.meetingId}`)}>
              View Full Report in Dashboard →
            </Button>
          </div>
        )}

        {/* SCREEN 10: PERMISSION DENIED */}
        {currentScreen === 'error-permission' && (
          <div className="space-y-4 text-center my-auto">
            <div className="w-12 h-12 rounded-xl bg-rose-100 text-rose-600 flex items-center justify-center mx-auto">
              <AlertTriangle className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-bold text-rose-900 dark:text-rose-200">Microphone Permission Blocked</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Chrome blocked microphone access. Click the lock icon in the browser address bar to allow microphone permissions.
            </p>
            <Button size="sm" fullWidth onClick={() => setScreen('detected')}>
              Retry Permission Check
            </Button>
          </div>
        )}

        {/* SCREEN 11: AUDIO CAPTURE ERROR */}
        {currentScreen === 'error-audio' && (
          <div className="space-y-4 text-center my-auto">
            <div className="w-12 h-12 rounded-xl bg-amber-100 text-amber-600 flex items-center justify-center mx-auto">
              <Volume2 className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-bold text-amber-900 dark:text-amber-200">Tab Audio Stream Not Selected</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Please ensure "Also share tab audio" is checked when selecting the meeting window.
            </p>
            <Button size="sm" fullWidth onClick={() => setScreen('detected')}>
              Re-select Tab Audio
            </Button>
          </div>
        )}

        {/* SCREEN 12: CONNECTION LOST */}
        {currentScreen === 'error-connection' && (
          <div className="space-y-4 text-center my-auto">
            <div className="w-12 h-12 rounded-xl bg-slate-100 text-slate-600 flex items-center justify-center mx-auto">
              <WifiOff className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-white">Connection Lost. Buffering...</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              WebSocket disconnected. Audio is currently being safely buffered in bounded memory queue.
            </p>
            <Button size="sm" fullWidth onClick={() => store.startCapture()}>
              Reconnect Now
            </Button>
          </div>
        )}

        {/* SCREEN 13: UNSUPPORTED PLATFORM */}
        {currentScreen === 'error-unsupported' && (
          <div className="space-y-4 text-center my-auto">
            <div className="w-12 h-12 rounded-xl bg-slate-100 text-slate-600 flex items-center justify-center mx-auto">
              <HelpCircle className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-white">Unsupported Page</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Navigate to Google Meet, Zoom Web, or Microsoft Teams in your browser to begin.
            </p>
            <Button size="sm" variant="outline" fullWidth onClick={() => setScreen('home')}>
              Return to Ready Screen
            </Button>
          </div>
        )}

        {/* SCREEN 14: SESSION INTERRUPTED */}
        {currentScreen === 'error-interrupted' && (
          <div className="space-y-4 text-center my-auto">
            <div className="w-12 h-12 rounded-xl bg-amber-100 text-amber-600 flex items-center justify-center mx-auto">
              <XCircle className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-bold text-amber-900 dark:text-amber-200">Meeting Ended Abruptly</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              The meeting tab was closed. Would you like to process the audio captured up to that point?
            </p>
            <Button size="sm" fullWidth onClick={() => setScreen('processing')}>
              Process Captured Audio
            </Button>
          </div>
        )}

        {/* SCREEN 15: SETTINGS */}
        {currentScreen === 'settings' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-2">
              <h3 className="text-sm font-bold text-slate-900 dark:text-white">Extension Settings</h3>
              <Button variant="ghost" size="sm" onClick={() => setScreen('home')}>Done</Button>
            </div>
            <div className="space-y-3 text-xs">
              <label className="flex items-center justify-between p-2 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 cursor-pointer">
                <span>Auto-detect meeting URLs</span>
                <input type="checkbox" defaultChecked />
              </label>
              <label className="flex items-center justify-between p-2 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 cursor-pointer">
                <span>Prompt for consent on every call</span>
                <input type="checkbox" defaultChecked />
              </label>
              <label className="flex items-center justify-between p-2 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 cursor-pointer">
                <span>Stereo track separation mode</span>
                <input type="checkbox" defaultChecked />
              </label>
            </div>
          </div>
        )}
      </div>

      {/* Chrome Side Panel Footer */}
      <div className="p-3 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 flex items-center justify-between text-xs text-slate-500">
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-500" />
          <span>Connected</span>
        </span>
        <span className="hover:text-indigo-600 cursor-pointer" onClick={() => store.logout()}>
          Sign Out
        </span>
      </div>
    </div>
  );
};
