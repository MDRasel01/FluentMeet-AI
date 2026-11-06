/**
 * Shared Constants for FluentMeet AI
 */

export const SUPPORTED_PLATFORMS = {
  GOOGLE_MEET: 'google-meet',
  ZOOM: 'zoom',
  TEAMS: 'teams',
} as const;

export const MEETING_DOMAINS = [
  'meet.google.com',
  'app.zoom.us',
  'teams.microsoft.com',
] as const;

export const WS_EVENTS = {
  CONNECT: 'connect',
  DISCONNECT: 'disconnect',
  START_STREAM: 'start_stream',
  AUDIO_CHUNK: 'audio_chunk',
  PAUSE_STREAM: 'pause_stream',
  RESUME_STREAM: 'resume_stream',
  STOP_STREAM: 'stop_stream',
  STATUS_UPDATE: 'status_update',
  HEARTBEAT: 'heartbeat',
  ERROR: 'error',
} as const;

export const RETENTION_TIERS = {
  EPHEMERAL: 0,
  SEVEN_DAYS: 7,
  THIRTY_DAYS: 30,
  NINETY_DAYS: 90,
} as const;

export const API_ENDPOINTS = {
  HEALTH_LIVE: '/api/v1/health/live',
  HEALTH_READY: '/api/v1/health/ready',
  AUTH_REGISTER: '/api/v1/auth/register',
  AUTH_LOGIN: '/api/v1/auth/login',
  AUTH_REFRESH: '/api/v1/auth/refresh',
  AUTH_LOGOUT: '/api/v1/auth/logout',
  USERS_ME: '/api/v1/users/me',
  MEETINGS: '/api/v1/meetings',
} as const;

