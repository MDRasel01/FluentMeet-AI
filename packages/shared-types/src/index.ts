/**
 * Shared Type Definitions for FluentMeet AI
 */

export type PlatformRole = 'individual' | 'super_admin' | 'support_admin' | 'platform_analyst';
export type OrgRole = 'owner' | 'admin' | 'manager' | 'member';
export type UserStatus = 'pending_verification' | 'active' | 'suspended' | 'deactivated' | 'deleted';

export interface UserProfile {
  id: string;
  email: string;
  fullName: string;
  nativeLanguage?: string;
  role: PlatformRole;
  status: UserStatus;
  isActive: boolean;
  isVerified: boolean;
  emailVerifiedAt?: string;
  timezone: string;
}

export interface UserDetail extends UserProfile {
  avatarUrl?: string;
  phoneNumber?: string;
  bio?: string;
  jobTitle?: string;
  englishLearningGoal?: string;
  targetSpeakingScore?: number;
  createdAt: string;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
  expiresInSeconds: number;
  user?: UserProfile;
}

export interface AuthSession {
  id: string;
  sessionName?: string;
  deviceType: string;
  ipAddress?: string;
  userAgent?: string;
  createdAt: string;
  lastUsedAt: string;
  expiresAt: string;
  isCurrent?: boolean;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  orgType: string;
  timezone: string;
  defaultLanguage: string;
  seatLimit: number;
  retentionDays: number;
  myRole?: OrgRole;
  createdAt: string;
}

export interface OrganizationSettings {
  allowManagerInvites: boolean;
  require2fa: boolean;
  enforceRecordingConsent: boolean;
}

export interface OrganizationMember {
  id: string;
  userId: string;
  email: string;
  fullName: string;
  role: OrgRole;
  status: string;
  joinedAt: string;
}

export interface OrganizationInvitation {
  id: string;
  organizationId: string;
  invitedEmail: string;
  role: OrgRole;
  invitedByName?: string;
  expiresAt: string;
  createdAt: string;
  isExpired: boolean;
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

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any[];
  };
  message?: string;
  requestId?: string;
}
