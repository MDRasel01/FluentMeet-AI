/**
 * FluentMeet AI - Audio Processing & Capture Types
 * Specification: Step 05 - Section 9 & 10
 */

export enum AudioSourceId {
  REMOTE_TAB = 0,
  LOCAL_MIC = 1,
}

export interface AudioCaptureConfig {
  targetSampleRate: number; // e.g. 16000 Hz
  channelCount: number;    // 1 (mono)
  chunkDurationMs: number; // 100-250ms (default 125ms = 2000 samples @ 16kHz)
  encoding: 'pcm_s16le';
}

export interface AudioChunkMetadata {
  protocolVersion: number;
  meetingId: string;
  sourceId: AudioSourceId;
  sequenceNumber: number;
  sessionRelativeTimestampMs: number;
  sampleRate: number;
  channels: number;
  sampleCount: number;
}

export interface AudioChunkPayload extends AudioChunkMetadata {
  data: ArrayBuffer; // S16LE PCM bytes
}

export interface AudioStreamHealth {
  sourceId: AudioSourceId;
  isActive: boolean;
  rmsVolume: number; // 0 to 100%
  peakVolume: number; // 0 to 100%
  isClipping: boolean;
  isSilent: boolean;
  framesCaptured: number;
  chunksEmitted: number;
  lastSequenceNumber: number;
  droppedFrames: number;
  bufferOverflowCount: number;
}

