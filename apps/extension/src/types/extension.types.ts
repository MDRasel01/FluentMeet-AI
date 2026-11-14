/**
 * FluentMeet AI - Core Extension Type Definitions
 * Specification: Step 05 - Chrome Extension Architecture
 */

export type SessionState =
  | 'IDLE'
  | 'PLATFORM_DETECTED'
  | 'MEETING_DETECTED'
  | 'CONSENT_REQUIRED'
  | 'PERMISSION_REQUIRED'
  | 'READY'
  | 'STARTING'
  | 'CAPTURING'
  | 'PAUSED'
  | 'RECONNECTING'
  | 'STOPPING'
  | 'PROCESSING'
  | 'COMPLETED'
  | 'FAILED';

export type MeetingPlatform = 'google-meet' | 'zoom' | 'teams' | 'unknown';

export interface ParticipantMetadata {
  participantId: string;
  meetingId: string;
  platform: MeetingPlatform;
  displayName: string;
  avatarUrl?: string;
  platformUserId?: string;
  isLocalUser: boolean;
  firstSeenAt: string;
  lastSeenAt: string;
  metadataSource: 'dom_selector' | 'mutation_observer' | 'user_profile';
  confidence: number;
  mappingStatus: 'mapped' | 'unknown' | 'provisional';
}

export interface ExtensionSessionData {
  sessionId: string;
  meetingId: string;
  title: string;
  platform: MeetingPlatform;
  meetingUrl: string;
  state: SessionState;
  tabId?: number;
  streamId?: string;
  consentConfirmed: boolean;
  consentTimestamp?: string;
  startedAt?: number; // Monotonic performance.now() or timestamp
  pausedAt?: number;
  totalPausedDurationMs: number;
  micMuted: boolean;
  tabAudioMuted: boolean;
  participantCount: number;
  participants: ParticipantMetadata[];
  error?: string;
  errorCode?: string;
}

export interface StoredSessionState {
  version: number;
  activeSession: ExtensionSessionData | null;
  lastKnownTabId?: number;
  lastKnownPlatform?: MeetingPlatform;
  updatedAt: number;
}

