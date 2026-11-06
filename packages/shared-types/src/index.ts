/**
 * Shared Type Definitions for FluentMeet AI
 */

export type UserRole = 'individual' | 'member' | 'manager' | 'org_admin' | 'super_admin';

export interface UserProfile {
  id: string;
  email: string;
  fullName: string;
  nativeLanguage?: string;
  role: UserRole;
  organizationId?: string;
  createdAt: string;
  updatedAt: string;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  seatLimit: number;
  retentionDays: number;
  createdAt: string;
}

export type MeetingPlatform = 'google-meet' | 'zoom' | 'teams';

export type SessionStatus = 'idle' | 'detected' | 'recording' | 'paused' | 'processing' | 'completed' | 'failed';

export interface MeetingSession {
  id: string;
  title: string;
  platform: MeetingPlatform;
  url: string;
  userId: string;
  organizationId?: string;
  status: SessionStatus;
  durationSeconds: number;
  startedAt: string;
  endedAt?: string;
}

export interface ParticipantInfo {
  name: string;
  avatarUrl?: string;
  isLocalUser: boolean;
  speakingTimeSeconds: number;
  speakingSharePercentage: number;
}

export interface WebSocketEvent<T = any> {
  event: string;
  sessionId: string;
  timestamp: number;
  payload: T;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any[];
  };
  requestId: string;
}

