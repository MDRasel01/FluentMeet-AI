import React, { useEffect, useState } from 'react';
import {
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  Play,
  Pause,
  Square,
  Users,
  Mic,
  MicOff,
  Volume2,
  Shield,
  Settings,
  Lock,
  XCircle,
  HelpCircle,
  Radio,
  WifiOff,
  RefreshCw,
  ExternalLink,
  ChevronRight,
  MoreVertical,
} from 'lucide-react';
import { Button, Input, Card, Badge, PlatformIcon, PlatformBadge, PlatformSelect } from '../../design-system/components';
import { useExtensionStore } from './src/sidepanel/store/extension-store';
import { VoiceRecognitionState } from './src/services/speech-recognition.service';

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

  // Auth form local state (clean, no hardcoded fake credentials)
  const [emailInput, setEmailInput] = useState('');
  const [passwordInput, setPasswordInput] = useState('');
  const [authError, setAuthError] = useState<string | null>(null);

  // Development preview toggle (cleanly folded by default)
  const [showDevPreview, setShowDevPreview] = useState(false);
  const [showThreeDotMenu, setShowThreeDotMenu] = useState(false);

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

  const handleLogin = () => {
    if (!emailInput.trim()) {
      setAuthError('Please enter your email address.');
      return;
    }
    setAuthError(null);
    store.setAuthSession({
      accessToken: 'jwt-session-token-' + Date.now(),
      refreshToken: 'jwt-refresh-token-' + Date.now(),
      userEmail: emailInput.trim(),
      userId: 'usr-' + Math.random().toString(36).substring(2, 8),
      expiresAt: Date.now() + 86400000,
    });
    setScreen('home');
  };

  const getVoiceBadge = (state: VoiceRecognitionState) => {
    switch (state) {
      case 'LISTENING':
        return (
          <Badge variant="success" size="sm" className="flex items-center gap-1 animate-pulse">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping" />
            Mic Listening
          </Badge>
        );
      case 'PROCESSING':
        return (
          <Badge variant="primary" size="sm" className="flex items-center gap-1">
            <RefreshCw className="w-3 h-3 animate-spin" />
            Transcribing...
          </Badge>
        );
      case 'REQUESTING_PERMISSION':
        return (
          <Badge variant="warning" size="sm">
            Mic Access...
          </Badge>
        );
      case 'ERROR':
        return (
          <Badge variant="danger" size="sm">
            Voice Error
          </Badge>
        );
      case 'STOPPED':
        return (
          <Badge variant="neutral" size="sm">
            Voice Paused
          </Badge>
        );
      default:
        return (
          <Badge variant="neutral" size="sm">
            Voice Ready
          </Badge>
        );
    }
  };

  return (
    <div className="w-full max-w-[400px] h-[640px] bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-xl flex flex-col overflow-hidden text-slate-900 dark:text-slate-100 antialiased mx-auto select-none">
      {/* Chrome Side Panel Header */}
      <div className="p-3.5 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-md bg-indigo-600 text-white flex items-center justify-center font-bold text-xs shadow-sm">
            <Sparkles className="w-3.5 h-3.5" />
          </div>
          <div>
            <span className="text-xs font-bold tracking-tight text-slate-900 dark:text-white block leading-tight">
              Meeting Coach SidePanel
            </span>
          </div>
        </div>

        <div className="flex items-center gap-1.5">
          <Badge variant="primary" size="sm">v1.0.2</Badge>
          <button
            onClick={() => setShowDevPreview(!showDevPreview)}
            className="text-[10px] text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 px-1.5 py-0.5 rounded border border-slate-200 dark:border-slate-800"
            title="Toggle Dev Screen Selector"
          >
            Dev
          </button>
          <button
            onClick={() => setScreen('settings')}
            className="p-1 rounded text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition-colors"
            title="Extension Settings"
          >
            <Settings className="w-4 h-4" />
          </button>

          {/* 3-Dot (Three Dots) Menu */}
          <div className="relative">
            <button
              onClick={() => setShowThreeDotMenu(!showThreeDotMenu)}
              className="p-1 rounded text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition-colors"
              title="More Options"
            >
              <MoreVertical className="w-4 h-4" />
            </button>

            {showThreeDotMenu && (
              <div className="absolute right-0 top-full mt-1.5 w-48 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xl py-1 z-50 text-xs">
                <button
                  onClick={() => {
                    store.initializeExtension();
                    setShowThreeDotMenu(false);
                  }}
                  className="w-full px-3 py-1.5 text-left flex items-center gap-2 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300"
                >
                  <RefreshCw className="w-3.5 h-3.5 text-indigo-500" />
                  <span>Reload / Refresh</span>
                </button>
                <button
                  onClick={() => {
                    setShowDevPreview(!showDevPreview);
                    setShowThreeDotMenu(false);
                  }}
                  className="w-full px-3 py-1.5 text-left flex items-center gap-2 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300"
                >
                  <Sparkles className="w-3.5 h-3.5 text-amber-500" />
                  <span>Toggle Dev Switcher</span>
                </button>
                <button
                  onClick={() => {
                    setScreen('settings');
                    setShowThreeDotMenu(false);
                  }}
                  className="w-full px-3 py-1.5 text-left flex items-center gap-2 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300"
                >
                  <Settings className="w-3.5 h-3.5 text-slate-400" />
                  <span>Extension Settings</span>
                </button>
                <div className="h-px bg-slate-100 dark:bg-slate-800 my-1" />
                <a
                  href="http://localhost:5173"
                  target="_blank"
                  rel="noreferrer"
                  onClick={() => setShowThreeDotMenu(false)}
                  className="w-full px-3 py-1.5 text-left flex items-center gap-2 hover:bg-slate-50 dark:hover:bg-slate-800 text-indigo-600 dark:text-indigo-400"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  <span>Open Web Dashboard</span>
                </a>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Screen Quick Selector for Design & QA Verification (Foldable) */}
      {showDevPreview && (
        <div className="bg-amber-50/90 dark:bg-amber-950/40 px-2.5 py-1.5 border-b border-amber-200 dark:border-amber-900 flex items-center justify-between text-[10px]">
          <span className="font-semibold text-amber-800 dark:text-amber-300">Screen Dev Switcher:</span>
          <select
            value={currentScreen}
            onChange={(e) => setScreen(e.target.value as ExtensionScreen)}
            className="bg-white dark:bg-slate-900 border border-amber-300 dark:border-amber-800 rounded px-1.5 py-0.5 text-[11px] font-medium"
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
      )}

      {/* Main Body per Screen */}
      <div className="flex-1 p-4 overflow-y-auto flex flex-col justify-between">
        {/* SCREEN 01: AUTH */}
        {currentScreen === 'auth' && (
          <div className="space-y-4 my-auto">
            <div className="text-center space-y-1">
              <div className="w-12 h-12 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mx-auto mb-2">
                <Lock className="w-6 h-6" />
              </div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white">Sign In to FluentMeet</h3>
              <p className="text-xs text-slate-500">Connect with your AI English Meeting Coach account</p>
            </div>

            <div className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                  Email Address
                </label>
                <input
                  type="email"
                  placeholder="your.email@company.com"
                  value={emailInput}
                  onChange={(e) => setEmailInput(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                  Password
                </label>
                <input
                  type="password"
                  placeholder="••••••••••••"
                  value={passwordInput}
                  onChange={(e) => setPasswordInput(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              {authError && (
                <p className="text-xs text-rose-500 text-center">{authError}</p>
              )}

              <Button fullWidth size="sm" onClick={handleLogin}>
                Sign In to Extension
              </Button>
            </div>

            <p className="text-center text-[11px] text-slate-400">
              Need an account?{' '}
              <a
                href="http://localhost:3000"
                target="_blank"
                rel="noreferrer"
                className="text-indigo-600 hover:underline font-semibold"
              >
                Register on Web
              </a>
            </p>
          </div>
        )}

        {/* SCREEN 02: HOME / READY */}
        {currentScreen === 'home' && (
          <div className="space-y-4 my-auto text-center">
            <div className="w-14 h-14 rounded-2xl bg-indigo-50 dark:bg-indigo-950/50 flex items-center justify-center mx-auto text-indigo-600">
              <Radio className="w-7 h-7 animate-pulse text-indigo-600" />
            </div>

            <div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white">
                Ready for Meeting
              </h3>
              <p className="text-xs text-slate-500 mt-1 leading-relaxed max-w-xs mx-auto">
                Join a meeting or select a platform below to start live AI coaching.
              </p>
            </div>

            {/* Interactive Platform Selector with 3D Icons */}
            <div className="p-3 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-left space-y-2">
              <span className="font-bold text-slate-700 dark:text-slate-300 block text-[11px] uppercase tracking-wider">
                Select Platform to Connect:
              </span>
              <div className="grid grid-cols-1 gap-2">
                {[
                  { id: 'google-meet', name: 'Google Meet', url: 'https://meet.google.com/xyz-abc' },
                  { id: 'zoom', name: 'Zoom Web Client', url: 'https://app.zoom.us/wc/12345' },
                  { id: 'teams', name: 'Microsoft Teams', url: 'https://teams.microsoft.com/meet' },
                ].map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => {
                      useExtensionStore.setState({
                        platform: item.id as any,
                        meetingTitle: `${item.name} Sync Call`,
                        meetingUrl: item.url,
                        meetingId: 'meet-' + Math.random().toString(36).substring(2, 8),
                      });
                      setScreen('detected');
                    }}
                    className="w-full flex items-center justify-between p-2 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 hover:border-indigo-400 dark:hover:border-indigo-500 hover:shadow-md transition-all group text-left cursor-pointer"
                  >
                    <div className="flex items-center gap-2.5">
                      <PlatformIcon platform={item.id} size={26} />
                      <div>
                        <span className="text-xs font-bold text-slate-800 dark:text-slate-200 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 block leading-tight">
                          {item.name}
                        </span>
                        <span className="text-[10px] text-slate-400 font-mono">
                          {item.id === 'google-meet' ? 'meet.google.com' : item.id === 'zoom' ? 'app.zoom.us' : 'teams.microsoft.com'}
                        </span>
                      </div>
                    </div>
                    <span className="text-[11px] text-indigo-600 dark:text-indigo-400 font-semibold opacity-0 group-hover:opacity-100 transition-opacity">
                      Select →
                    </span>
                  </button>
                ))}
              </div>
            </div>

            {/* Direct Voice Test & Manual Start */}
            <div className="pt-2 space-y-2">
              <Button
                size="sm"
                fullWidth
                leadingIcon={<Mic className="w-3.5 h-3.5" />}
                onClick={() => {
                  store.startCapture();
                }}
              >
                Start Speech Practice & Voice Test
              </Button>
              <p className="text-[10px] text-slate-400">
                You can test speech recognition immediately or join a call.
              </p>
            </div>
          </div>
        )}

        {/* SCREEN 03: MEETING DETECTED */}
        {currentScreen === 'detected' && (
          <div className="space-y-4">
            <div className="p-3.5 rounded-2xl bg-indigo-50/80 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-900 space-y-2">
              <div className="flex items-center justify-between">
                <PlatformBadge platform={store.platform} size="sm" />
                <span className="text-[11px] font-mono text-indigo-700 dark:text-indigo-400 truncate max-w-[140px]">
                  {store.meetingUrl || 'Active Tab'}
                </span>
              </div>
              <div className="flex items-center gap-3 pt-1">
                <PlatformIcon platform={store.platform} size={32} />
                <div className="overflow-hidden">
                  <h4 className="text-sm font-bold text-slate-900 dark:text-white truncate">
                    {store.meetingTitle || 'Active Meeting Session'}
                  </h4>
                  <span className="text-[11px] text-emerald-600 dark:text-emerald-400 flex items-center gap-1 font-medium">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    Audio Stream Ready
                  </span>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs font-semibold text-slate-500">
                <span>Call Participants ({store.participants.length > 0 ? store.participants.length + 1 : 1})</span>
                {store.participants.length > 0 && (
                  <span className="text-indigo-600 cursor-pointer" onClick={() => setScreen('participant-list')}>
                    View All
                  </span>
                )}
              </div>
              <div className="p-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 space-y-2 text-xs">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-5 h-5 rounded-full bg-indigo-600 text-white font-bold text-[10px] flex items-center justify-center">
                      Y
                    </div>
                    <span className="font-medium text-slate-800 dark:text-slate-200">You (Local Speaker)</span>
                  </div>
                  <Badge variant="success" size="sm">Active</Badge>
                </div>

                {store.participants.map((p, idx) => (
                  <div key={p.participantId || idx} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-5 h-5 rounded-full bg-slate-500 text-white font-bold text-[10px] flex items-center justify-center">
                        {(p.displayName || 'Participant').charAt(0).toUpperCase()}
                      </div>
                      <span className="font-medium text-slate-800 dark:text-slate-200">{p.displayName || 'Participant'}</span>
                    </div>
                    <span className="text-[10px] text-slate-400">Remote</span>
                  </div>
                ))}

                {store.participants.length === 0 && (
                  <p className="text-[11px] text-slate-400 italic pt-1">
                    Waiting for remote audio participants to speak...
                  </p>
                )}
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
              <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                Active Roster ({store.participants.length > 0 ? store.participants.length + 1 : 1})
              </h3>
              <Button variant="ghost" size="sm" onClick={() => setScreen('detected')}>
                Back
              </Button>
            </div>
            <div className="space-y-2 text-xs">
              <div className="p-2.5 rounded-lg border border-slate-200 dark:border-slate-800 flex items-center justify-between">
                <div>
                  <span className="font-bold text-slate-800 dark:text-slate-200 block">You (Local Speaker)</span>
                  <span className="text-[10px] text-slate-400">Primary Speaker Track</span>
                </div>
                <Badge variant="success" size="sm">Connected</Badge>
              </div>

              {store.participants.map((p, i) => (
                <div key={p.participantId || i} className="p-2.5 rounded-lg border border-slate-200 dark:border-slate-800 flex items-center justify-between">
                  <div>
                    <span className="font-bold text-slate-800 dark:text-slate-200 block">{p.displayName || 'Participant'}</span>
                    <span className="text-[10px] text-slate-400">Remote Participant</span>
                  </div>
                  <Badge variant="neutral" size="sm">Remote Tab</Badge>
                </div>
              ))}

              {store.participants.length === 0 && (
                <div className="text-center py-4 text-xs text-slate-400">
                  No remote participants captured yet. Remote speakers will appear once audio is received from the meeting tab.
                </div>
              )}
            </div>
          </div>
        )}

        {/* SCREEN 05: CONSENT CONFIRMATION */}
        {currentScreen === 'consent' && (
          <div className="space-y-4 my-auto text-center">
            <div className="w-12 h-12 rounded-xl bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400 flex items-center justify-center mx-auto">
              <Shield className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-bold">Two-Party Consent Notice</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Recording and analysis laws require all participants to be notified before capturing audio. Please notify meeting attendees.
            </p>
            <Button fullWidth size="sm" onClick={() => setScreen('detected')}>
              I Understand & Agree
            </Button>
          </div>
        )}

        {/* SCREEN 06: LIVE SESSION */}
        {currentScreen === 'live' && (
          <div className="space-y-3.5 flex-1 flex flex-col justify-between">
            <div className="space-y-3">
              {/* Live Header & Timer */}
              <div className="p-3 rounded-xl bg-rose-50/80 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-900 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-rose-600 animate-ping" />
                  <div>
                    <span className="text-xs font-bold text-rose-700 dark:text-rose-400 uppercase tracking-wider block leading-tight">
                      Live Recording Active
                    </span>
                    <span className="text-[10px] text-slate-500 truncate max-w-[150px] block">
                      {store.meetingTitle || 'Voice Recognition Session'}
                    </span>
                  </div>
                </div>
                <span className="text-xl font-black font-mono text-slate-900 dark:text-white tabular-nums">
                  {formatTimer(store.sessionSeconds)}
                </span>
              </div>

              {/* Voice Recognition Status Bar */}
              <div className="flex items-center justify-between px-1">
                <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                  <Mic className="w-3.5 h-3.5 text-indigo-600" />
                  Live Voice Engine
                </span>
                <div className="flex items-center gap-1.5">
                  {getVoiceBadge(store.voiceState)}
                  {store.voiceState !== 'LISTENING' && store.voiceState !== 'PROCESSING' ? (
                    <button
                      onClick={() => store.startVoiceRecognition()}
                      className="text-[10px] text-indigo-600 dark:text-indigo-400 hover:underline font-semibold"
                    >
                      Start Voice
                    </button>
                  ) : (
                    <button
                      onClick={() => store.stopVoiceRecognition()}
                      className="text-[10px] text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                    >
                      Pause Voice
                    </button>
                  )}
                </div>
              </div>

              {/* Real-time Voice Recognition Transcript Box */}
              <div className="p-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-900/70 space-y-2 h-[160px] overflow-y-auto text-xs flex flex-col justify-between">
                <div className="space-y-1.5 flex-1 overflow-y-auto pr-1">
                  {store.finalTranscripts.length === 0 && !store.interimTranscript && (
                    <div className="h-full flex flex-col items-center justify-center text-center text-slate-400 py-4">
                      <div className="w-8 h-8 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center mb-1 text-slate-400">
                        <Mic className="w-4 h-4" />
                      </div>
                      <p className="font-medium text-slate-600 dark:text-slate-300 text-[11px]">
                        Listening for audio speech...
                      </p>
                      <p className="text-[10px] text-slate-400 max-w-[220px]">
                        Speak clearly. Spoken words will appear here in real time as you talk.
                      </p>
                    </div>
                  )}

                  {store.finalTranscripts.map((t) => (
                    <div key={t.id} className="text-slate-800 dark:text-slate-200 leading-relaxed text-[11px]">
                      <span className="font-mono text-[9px] text-slate-400 mr-1.5">
                        [{formatTimer(Math.floor((t.timestampMs - (store.finalTranscripts[0]?.timestampMs || t.timestampMs)) / 1000))}]
                      </span>
                      <span>{t.text}</span>
                    </div>
                  ))}

                  {/* Interim Live Transcript (typing indicator) */}
                  {store.interimTranscript && (
                    <div className="text-indigo-600 dark:text-indigo-400 italic text-[11px] font-medium leading-relaxed animate-pulse">
                      <span className="font-mono text-[9px] text-indigo-400 mr-1.5">[Live]</span>
                      {store.interimTranscript}
                      <span className="inline-block w-1.5 h-3 bg-indigo-500 ml-1 animate-ping" />
                    </div>
                  )}
                </div>

                {store.voiceError && (
                  <div className="text-[10px] text-rose-500 border-t border-rose-200 dark:border-rose-900 pt-1">
                    Voice Note: {store.voiceError}
                  </div>
                )}
              </div>

              {/* Dual Audio VU Meters */}
              <div className="p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-2">
                <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
                  Audio Signal Health
                </span>

                {/* Your Mic */}
                <div className="space-y-0.5">
                  <div className="flex justify-between text-[11px] font-medium">
                    <span className="flex items-center gap-1.5 text-slate-700 dark:text-slate-300">
                      <Mic className="w-3 h-3 text-emerald-600" /> Your Microphone
                    </span>
                    <span className="font-mono text-slate-500 text-[10px]">{store.micVolume}%</span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-emerald-500 rounded-full transition-all duration-100"
                      style={{ width: `${Math.min(100, store.micVolume)}%` }}
                    />
                  </div>
                </div>

                {/* Tab Audio */}
                <div className="space-y-0.5">
                  <div className="flex justify-between text-[11px] font-medium">
                    <span className="flex items-center gap-1.5 text-slate-700 dark:text-slate-300">
                      <Volume2 className="w-3 h-3 text-indigo-600" /> Meeting Tab Audio
                    </span>
                    <span className="font-mono text-slate-500 text-[10px]">{store.tabVolume}%</span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-indigo-600 rounded-full transition-all duration-100"
                      style={{ width: `${Math.min(100, store.tabVolume)}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Session Controls */}
            <div className="grid grid-cols-2 gap-2.5 pt-1">
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
              <p className="text-xs text-slate-500 mt-1">
                Audio streaming and speech recognition are suspended.
              </p>
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
              <p className="text-xs text-slate-500 mt-1">Speaker Diarization, Phonetics & Gemini AI Evaluation</p>
            </div>
            <p className="text-[11px] text-slate-400">
              Your audio has been dispatched for AI evaluation. You can open the Web Dashboard to view your full results once completed.
            </p>
            <Button size="sm" variant="outline" fullWidth onClick={() => setScreen('completed')}>
              View Finished Report
            </Button>
          </div>
        )}

        {/* SCREEN 09: COMPLETED */}
        {currentScreen === 'completed' && (
          <div className="space-y-4 text-center my-auto">
            <div className="w-12 h-12 rounded-full bg-emerald-100 dark:bg-emerald-950/60 text-emerald-600 flex items-center justify-center mx-auto">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white">Analysis Complete!</h3>
              <p className="text-xs text-slate-500 mt-1">
                Session recorded: <span className="font-semibold text-slate-700 dark:text-slate-300">{formatTimer(store.sessionSeconds)}</span>
              </p>
            </div>

            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs text-left space-y-1.5">
              <div className="flex justify-between">
                <span className="text-slate-500">Recognized Spoken Utterances:</span>
                <span className="font-semibold text-slate-800 dark:text-slate-200">{store.finalTranscripts.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Meeting ID:</span>
                <span className="font-mono text-[10px] text-slate-600 dark:text-slate-300">{store.meetingId || 'Local Session'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">AI Scoring Status:</span>
                <Badge variant="success" size="sm">Processed</Badge>
              </div>
            </div>

            <div className="space-y-2">
              <Button
                size="md"
                fullWidth
                trailingIcon={<ExternalLink className="w-3.5 h-3.5" />}
                onClick={() => {
                  if (typeof window !== 'undefined') {
                    window.open('http://localhost:3000', '_blank');
                  }
                }}
              >
                Open Web Dashboard
              </Button>
              <Button
                variant="outline"
                size="sm"
                fullWidth
                onClick={() => {
                  store.clearTranscripts();
                  setScreen('home');
                }}
              >
                Start New Session
              </Button>
            </div>
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
            <Button size="sm" fullWidth onClick={() => store.startVoiceRecognition()}>
              Retry Microphone Permission
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
              <Button variant="ghost" size="sm" onClick={() => setScreen('home')}>
                Done
              </Button>
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
                <span>Continuous Speech Recognition</span>
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
