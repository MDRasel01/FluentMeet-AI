/**
 * FluentMeet AI - Meeting Session Controller & State Machine
 * Implements centralized FSM with state recovery across Service Worker restarts.
 * Specification: Step 05 - Section 7 & Section 15
 */

import { ExtensionSessionData, MeetingPlatform, ParticipantMetadata, SessionState } from '../types/extension.types';

export class SessionController {
  private static STORAGE_KEY = 'fluentmeet_active_session';

  private session: ExtensionSessionData = {
    sessionId: '',
    meetingId: '',
    title: '',
    platform: 'unknown',
    meetingUrl: '',
    state: 'IDLE',
    consentConfirmed: false,
    totalPausedDurationMs: 0,
    micMuted: false,
    tabAudioMuted: false,
    participantCount: 0,
    participants: [],
  };

  private static VALID_TRANSITIONS: Record<SessionState, SessionState[]> = {
    IDLE: ['PLATFORM_DETECTED'],
    PLATFORM_DETECTED: ['MEETING_DETECTED', 'IDLE'],
    MEETING_DETECTED: ['CONSENT_REQUIRED', 'IDLE'],
    CONSENT_REQUIRED: ['PERMISSION_REQUIRED', 'IDLE'],
    PERMISSION_REQUIRED: ['READY', 'FAILED', 'IDLE'],
    READY: ['STARTING', 'IDLE'],
    STARTING: ['CAPTURING', 'FAILED', 'IDLE'],
    CAPTURING: ['PAUSED', 'RECONNECTING', 'STOPPING', 'FAILED'],
    PAUSED: ['CAPTURING', 'STOPPING', 'FAILED'],
    RECONNECTING: ['CAPTURING', 'FAILED', 'STOPPING'],
    STOPPING: ['PROCESSING', 'COMPLETED', 'FAILED', 'IDLE'],
    PROCESSING: ['COMPLETED', 'FAILED'],
    COMPLETED: ['IDLE'],
    FAILED: ['IDLE', 'READY', 'RECONNECTING'],
  };

  constructor() {
    this.restoreState();
  }

  public async restoreState(): Promise<void> {
    try {
      const storage = chrome.storage?.session || chrome.storage?.local;
      if (storage) {
        const result = await storage.get(SessionController.STORAGE_KEY);
        if (result && result[SessionController.STORAGE_KEY]) {
          this.session = result[SessionController.STORAGE_KEY];
        }
      }
    } catch (e) {
      console.warn('Failed to restore session state:', e);
    }
  }

  public async persistState(): Promise<void> {
    try {
      const storage = chrome.storage?.session || chrome.storage?.local;
      if (storage) {
        await storage.set({ [SessionController.STORAGE_KEY]: this.session });
      }
    } catch (e) {
      console.warn('Failed to persist session state:', e);
    }
  }

  public getState(): SessionState {
    return this.session.state;
  }

  public getSession(): ExtensionSessionData {
    return { ...this.session };
  }

  public transition(newState: SessionState, payload?: Partial<ExtensionSessionData>): boolean {
    const currentState = this.session.state;
    const allowed = SessionController.VALID_TRANSITIONS[currentState] || [];

    if (!allowed.includes(newState) && newState !== 'IDLE' && newState !== 'FAILED') {
      console.warn(`[SessionController] Disallowed transition from ${currentState} to ${newState}`);
      return false;
    }

    this.session.state = newState;
    if (payload) {
      this.session = { ...this.session, ...payload };
    }

    if (newState === 'PAUSED') {
      this.session.pausedAt = Date.now();
    } else if (newState === 'CAPTURING' && this.session.pausedAt) {
      this.session.totalPausedDurationMs += Date.now() - this.session.pausedAt;
      this.session.pausedAt = undefined;
    } else if (newState === 'IDLE' || newState === 'COMPLETED') {
      this.session.streamId = undefined;
    }

    this.persistState();

    // Broadcast change
    chrome.runtime.sendMessage({
      type: 'SESSION_STATE_CHANGED',
      state: newState,
      sessionId: this.session.sessionId,
      error: this.session.error,
    }).catch(() => {});

    return true;
  }

  public updateParticipants(participants: ParticipantMetadata[]): void {
    this.session.participants = participants;
    this.session.participantCount = participants.length;
    this.persistState();
  }

  public setPlatformDetected(platform: MeetingPlatform, url: string, title?: string): void {
    if (this.session.state === 'IDLE' || this.session.state === 'PLATFORM_DETECTED') {
      this.transition('PLATFORM_DETECTED', {
        platform,
        meetingUrl: url,
        title: title || `${platform} meeting`,
      });
      this.transition('MEETING_DETECTED');
    }
  }
}

