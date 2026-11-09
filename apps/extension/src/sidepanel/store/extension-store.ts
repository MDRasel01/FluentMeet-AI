/**
 * FluentMeet AI - Side Panel Extension State Store (Zustand)
 * Specification: Step 05 - Section 3, Section 7 & Section 15
 */

import { create } from 'zustand';
import { ExtensionScreen } from '../../../ExtensionApp';
import { AudioSourceId } from '../../types/audio.types';
import { MeetingPlatform, ParticipantMetadata, SessionState } from '../../types/extension.types';
import { ExtensionAuthAdapter, StoredAuthSession } from '../../utils/auth-adapter';
import {
  speechRecognitionService,
  VoiceRecognitionState,
  RecognizedTranscriptItem,
} from '../../services/speech-recognition.service';

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

  // Voice Recognition & Live Transcripts
  voiceState: VoiceRecognitionState;
  interimTranscript: string;
  finalTranscripts: RecognizedTranscriptItem[];
  voiceError: string | null;

  // Actions
  initializeExtension: () => Promise<void>;
  startCapture: () => Promise<void>;
  pauseCapture: () => Promise<void>;
  resumeCapture: () => Promise<void>;
  stopCapture: () => Promise<void>;
  startVoiceRecognition: () => Promise<void>;
  stopVoiceRecognition: () => void;
  clearTranscripts: () => void;
  updateAudioMetrics: (sourceId: AudioSourceId, volume: number) => void;
}

export const useExtensionStore = create<ExtensionStoreState>((set, get) => ({
  screen: 'home',
  setScreen: (screen) => set({ screen }),

  authSession: null,
  setAuthSession: (authSession) => set({ authSession, screen: authSession ? 'home' : 'auth' }),
  logout: async () => {
    await ExtensionAuthAdapter.clearSession();
    speechRecognitionService.stop();
    set({
      authSession: null,
      screen: 'auth',
      sessionState: 'IDLE',
      voiceState: 'IDLE',
      interimTranscript: '',
      finalTranscripts: [],
    });
  },

  sessionState: 'IDLE',
  meetingId: '',
  meetingTitle: '',
  platform: 'unknown',
  meetingUrl: '',
  consentChecked: false,
  setConsentChecked: (consentChecked) => set({ consentChecked }),

  micVolume: 0,
  tabVolume: 0,
  sessionSeconds: 0,
  participants: [],

  // Voice recognition initial state
  voiceState: 'IDLE',
  interimTranscript: '',
  finalTranscripts: [],
  voiceError: null,

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
            meetingId: response.meetingId || 'meet-' + Math.random().toString(36).substring(2, 9),
            meetingTitle: response.title || (response.platform === 'google-meet' ? 'Google Meet Call' : 'Online Meeting'),
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
          set({ participants: msg.participants || [] });
        }
      });
    }
  },

  startVoiceRecognition: async () => {
    set({ voiceState: 'INITIALIZING', voiceError: null });
    await speechRecognitionService.start({
      onStateChange: (state) => set({ voiceState: state }),
      onInterimResult: (text) => set({ interimTranscript: text }),
      onFinalResult: (item) => {
        set((prev) => ({
          finalTranscripts: [...prev.finalTranscripts, item],
          interimTranscript: '',
        }));
      },
      onError: (err) => set({ voiceState: 'ERROR', voiceError: err }),
      onEnd: () => set({ voiceState: 'STOPPED', interimTranscript: '' }),
    });
  },

  stopVoiceRecognition: () => {
    speechRecognitionService.stop();
    set({ voiceState: 'STOPPED', interimTranscript: '' });
  },

  clearTranscripts: () => {
    set({ finalTranscripts: [], interimTranscript: '', voiceError: null });
  },

  startCapture: async () => {
    let { meetingId, meetingTitle, platform, meetingUrl } = get();
    if (!meetingId) {
      meetingId = 'meet-' + Math.random().toString(36).substring(2, 9);
      set({ meetingId });
    }
    if (!meetingTitle) {
      meetingTitle = 'Active Meeting Session';
      set({ meetingTitle });
    }

    // Also start live speech recognition for immediate spoken transcript
    get().startVoiceRecognition().catch((e) => console.warn('Speech recognition warning:', e));

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
      set({ screen: 'live', sessionState: 'CAPTURING', sessionSeconds: 0 });
    }
  },

  pauseCapture: async () => {
    speechRecognitionService.stop();
    if (typeof chrome !== 'undefined' && chrome.runtime?.sendMessage) {
      await chrome.runtime.sendMessage({ type: 'PAUSE_CAPTURE_COMMAND' });
    }
    set({ screen: 'paused', sessionState: 'PAUSED', voiceState: 'STOPPED' });
  },

  resumeCapture: async () => {
    get().startVoiceRecognition().catch((e) => console.warn('Speech recognition resume warning:', e));
    if (typeof chrome !== 'undefined' && chrome.runtime?.sendMessage) {
      await chrome.runtime.sendMessage({ type: 'RESUME_CAPTURE_COMMAND' });
    }
    set({ screen: 'live', sessionState: 'CAPTURING' });
  },

  stopCapture: async () => {
    speechRecognitionService.stop();
    if (typeof chrome !== 'undefined' && chrome.runtime?.sendMessage) {
      await chrome.runtime.sendMessage({ type: 'STOP_CAPTURE_COMMAND' });
    }
    set({ screen: 'completed', sessionState: 'COMPLETED', voiceState: 'STOPPED' });
  },

  updateAudioMetrics: (sourceId, volume) => {
    if (sourceId === AudioSourceId.LOCAL_MIC) set({ micVolume: volume });
    else set({ tabVolume: volume });
  },
}));
