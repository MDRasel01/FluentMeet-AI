/**
 * FluentMeet AI - Side Panel Extension State Store (Zustand)
 * Specification: Step 05 - Section 3, Section 7 & Section 15
 */

import { create } from 'zustand';
import { ExtensionScreen } from '../../../ExtensionApp';
import { AudioSourceId } from '../../types/audio.types';
import { MeetingPlatform, ParticipantMetadata, SessionState } from '../../types/extension.types';
import { ExtensionAuthAdapter, StoredAuthSession } from '../../utils/auth-adapter';

interface ExtensionStoreState {
  // Navigation & Screen
  screen: ExtensionScreen;
  setScreen: (screen: ExtensionScreen) => void;

  // Authentication
  authSession: StoredAuthSession | null;
  setAuthSession: (session: StoredAuthSession | null) => void;
  logout: () => Promise<void>;

  // Session & Platform
  sessionState: SessionState;
  meetingId: string;
  meetingTitle: string;
  platform: MeetingPlatform;
  meetingUrl: string;
  consentChecked: boolean;
  setConsentChecked: (checked: boolean) => void;

  // Real-time Metrics (Dual VU meters)
  micVolume: number; // 0-100%
  tabVolume: number; // 0-100%
  sessionSeconds: number;
  participants: ParticipantMetadata[];

  // Actions
  initializeExtension: () => Promise<void>;
  startCapture: () => Promise<void>;
  pauseCapture: () => Promise<void>;
  resumeCapture: () => Promise<void>;
  stopCapture: () => Promise<void>;
  updateAudioMetrics: (sourceId: AudioSourceId, volume: number) => void;
}

export const useExtensionStore = create<ExtensionStoreState>((set, get) => ({
  screen: 'home',
  setScreen: (screen) => set({ screen }),

  authSession: null,
  setAuthSession: (authSession) => set({ authSession, screen: authSession ? 'home' : 'auth' }),
  logout: async () => {
    await ExtensionAuthAdapter.clearSession();
    set({ authSession: null, screen: 'auth', sessionState: 'IDLE' });
  },

  sessionState: 'IDLE',
  meetingId: 'meet-' + Math.random().toString(36).substring(2, 9),
  meetingTitle: 'Team Sync Call',
  platform: 'google-meet',
  meetingUrl: '',
  consentChecked: false,
  setConsentChecked: (consentChecked) => set({ consentChecked }),

  micVolume: 0,
  tabVolume: 0,
  sessionSeconds: 0,
  participants: [],

  initializeExtension: async () => {
    // 1. Check auth session
    const session = await ExtensionAuthAdapter.getSession();
    if (session) {
      set({ authSession: session });
    }

    // 2. Query meeting status from background
    if (typeof chrome !== 'undefined' && chrome.runtime?.sendMessage) {
      try {
        const response = await chrome.runtime.sendMessage({ type: 'CHECK_MEETING_STATUS' });
        if (response?.isMeetingActive) {
          set({
            platform: response.platform,
            meetingUrl: response.url,
            screen: 'detected',
            sessionState: 'MEETING_DETECTED',
          });
        }
      } catch (_) {}

      // 3. Listen for runtime messages from offscreen & background
      chrome.runtime.onMessage.addListener((msg) => {
        if (msg.type === 'OFFSCREEN_AUDIO_METRICS') {
          if (msg.sourceId === AudioSourceId.LOCAL_MIC) {
            set({ micVolume: msg.rmsVolume });
          } else if (msg.sourceId === AudioSourceId.REMOTE_TAB) {
            set({ tabVolume: msg.rmsVolume });
          }
        } else if (msg.type === 'SESSION_STATE_CHANGED') {
          if (msg.state === 'CAPTURING') {
            set({ screen: 'live', sessionState: 'CAPTURING' });
          } else if (msg.state === 'PAUSED') {
            set({ screen: 'paused', sessionState: 'PAUSED' });
          } else if (msg.state === 'COMPLETED') {
            set({ screen: 'completed', sessionState: 'COMPLETED' });
          } else if (msg.state === 'FAILED') {
            set({ screen: 'error-connection', sessionState: 'FAILED' });
          }
        } else if (msg.type === 'PARTICIPANTS_UPDATED') {
          set({ participants: msg.participants });
        }
      });
    }
  },

  startCapture: async () => {
    const { meetingId, meetingTitle, platform, meetingUrl } = get();
    if (typeof chrome !== 'undefined' && chrome.runtime?.sendMessage) {
      const resp = await chrome.runtime.sendMessage({
        type: 'START_CAPTURE_COMMAND',
        meetingId,
        title: meetingTitle,
        platform,
        url: meetingUrl,
      });

      if (resp?.success) {
        set({ screen: 'live', sessionState: 'CAPTURING', sessionSeconds: 0 });
      } else {
        set({ screen: 'error-audio', sessionState: 'FAILED' });
      }
    } else {
      // Mock / Preview Mode
      set({ screen: 'live', sessionState: 'CAPTURING' });
    }
  },

  pauseCapture: async () => {
    if (typeof chrome !== 'undefined' && chrome.runtime?.sendMessage) {
      await chrome.runtime.sendMessage({ type: 'PAUSE_CAPTURE_COMMAND' });
    }
    set({ screen: 'paused', sessionState: 'PAUSED' });
  },

  resumeCapture: async () => {
    if (typeof chrome !== 'undefined' && chrome.runtime?.sendMessage) {
      await chrome.runtime.sendMessage({ type: 'RESUME_CAPTURE_COMMAND' });
    }
    set({ screen: 'live', sessionState: 'CAPTURING' });
  },

  stopCapture: async () => {
    if (typeof chrome !== 'undefined' && chrome.runtime?.sendMessage) {
      await chrome.runtime.sendMessage({ type: 'STOP_CAPTURE_COMMAND' });
    }
    set({ screen: 'completed', sessionState: 'COMPLETED' });
  },

  updateAudioMetrics: (sourceId, volume) => {
    if (sourceId === AudioSourceId.LOCAL_MIC) set({ micVolume: volume });
    else set({ tabVolume: volume });
  },
}));
