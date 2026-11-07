/**
 * FluentMeet AI - WebSocket Communication Protocol Types
 * Specification: Step 05 - Section 12
 */

import { AudioSourceId } from './audio.types';
import { ParticipantMetadata } from './extension.types';

export type ClientWebSocketMessageType =
  | 'session_init'
  | 'audio_chunk'
  | 'audio_source_started'
  | 'audio_source_stopped'
  | 'capture_paused'
  | 'capture_resumed'
  | 'participant_metadata'
  | 'heartbeat'
  | 'session_stop';

export type ServerWebSocketMessageType =
  | 'session_ready'
  | 'audio_ack'
  | 'connection_status'
  | 'participant_update'
  | 'processing_status'
  | 'session_error'
  | 'session_completed'
  | 'pong';

export interface BaseWebSocketMessage {
  type: ClientWebSocketMessageType | ServerWebSocketMessageType;
  sessionId: string;
  timestamp: string;
}

export interface SessionInitMessage extends BaseWebSocketMessage {
  type: 'session_init';
  meetingId: string;
  platform: string;
  audioSources: AudioSourceId[];
  sampleRate: number;
  channels: number;
  encoding: string;
  clientVersion: string;
}

export interface AudioAckMessage extends BaseWebSocketMessage {
  type: 'audio_ack';
  sourceId: AudioSourceId;
  sequenceNumber: number;
  receivedAt: string;
}

export interface ParticipantMetadataMessage extends BaseWebSocketMessage {
  type: 'participant_metadata';
  participants: ParticipantMetadata[];
}

export interface SessionErrorMessage extends BaseWebSocketMessage {
  type: 'session_error';
  errorCode: string;
  message: string;
  retryable: boolean;
}

export interface WebSocketConfig {
  url: string;
  token?: string;
  reconnectAttempts: number;
  initialBackoffMs: number;
  maxBackoffMs: number;
  jitterFactor: number;
  heartbeatIntervalMs: number;
}

