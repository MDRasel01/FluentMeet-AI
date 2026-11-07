/**
 * FluentMeet AI - Offscreen Audio Manager
 * Orchestrates dual audio capture pipelines, resampling, binary framing, and WebSocket streaming.
 * Specification: Step 05 - Section 4.2.C, Section 9, 10 & 12
 */

import { AudioSourceId } from '../types/audio.types';
import { TabAudioCapture } from './tab-audio-capture';
import { MicrophoneCapture } from './microphone-capture';
import { AudioResampler } from './audio-resampler';
import { AudioFrameEncoder, PROTOCOL_VERSION } from '../utils/audio-encoder';
import { MonotonicSessionClock } from '../utils/monotonic-clock';

export interface AudioManagerConfig {
  targetSampleRate: number; // 16000
  workletUrl: string;
  meetingId: string;
  onBinaryFrameReady: (frame: ArrayBuffer) => void;
  onMetricsUpdate: (metrics: {
    sourceId: AudioSourceId;
    rmsVolume: number;
    peakVolume: number;
    isClipping: boolean;
    isSilent: boolean;
  }) => void;
  onError: (sourceId: AudioSourceId, error: Error) => void;
}

export class AudioManager {
  private tabCapture: TabAudioCapture = new TabAudioCapture();
  private micCapture: MicrophoneCapture = new MicrophoneCapture();
  private clock: MonotonicSessionClock = new MonotonicSessionClock();

  private tabSequenceNumber: number = 0;
  private micSequenceNumber: number = 0;
  private isPaused: boolean = false;
  private config: AudioManagerConfig;

  constructor(config: AudioManagerConfig) {
    this.config = config;
  }

  public async start(streamId: string): Promise<void> {
    this.clock.start();
    this.tabSequenceNumber = 0;
    this.micSequenceNumber = 0;
    this.isPaused = false;

    // Start Tab Audio Capture
    await this.tabCapture.startCapture(streamId, this.config.workletUrl, {
      onChunk: (samples, sampleRate) => this.processAudioChunk(AudioSourceId.REMOTE_TAB, samples, sampleRate),
      onError: (err) => this.config.onError(AudioSourceId.REMOTE_TAB, err),
      onEnded: () => {
        chrome.runtime.sendMessage({
          type: 'OFFSCREEN_AUDIO_STOPPED',
          sourceId: AudioSourceId.REMOTE_TAB,
        }).catch(() => {});
      },
    });

    // Start Microphone Capture
    await this.micCapture.startCapture(this.config.workletUrl, {
      onChunk: (samples, sampleRate) => this.processAudioChunk(AudioSourceId.LOCAL_MIC, samples, sampleRate),
      onError: (err) => this.config.onError(AudioSourceId.LOCAL_MIC, err),
      onEnded: () => {
        chrome.runtime.sendMessage({
          type: 'OFFSCREEN_AUDIO_STOPPED',
          sourceId: AudioSourceId.LOCAL_MIC,
        }).catch(() => {});
      },
    });
  }

  public pause(): void {
    this.isPaused = true;
  }

  public resume(): void {
    this.isPaused = false;
  }

  public stop(): void {
    this.isPaused = false;
    this.tabCapture.stopCapture();
    this.micCapture.stopCapture();
    this.clock.reset();
  }

  private processAudioChunk(
    sourceId: AudioSourceId,
    rawSamples: Float32Array,
    inputSampleRate: number
  ): void {
    if (this.isPaused) {
      return; // Do not emit or transmit audio chunks while paused per Section 7
    }

    // 1. Calculate VU & health metrics on original samples
    const metrics = AudioResampler.calculateMetrics(rawSamples);
    this.config.onMetricsUpdate({
      sourceId,
      rmsVolume: metrics.rmsVolume,
      peakVolume: metrics.peakVolume,
      isClipping: metrics.isClipping,
      isSilent: metrics.isSilent,
    });

    // 2. Resample to target rate (16 kHz)
    const targetRate = this.config.targetSampleRate || 16000;
    const resampled = AudioResampler.resample(rawSamples, inputSampleRate, targetRate);

    // 3. Convert to Signed 16-bit PCM (S16LE)
    const pcmData = AudioResampler.floatToPcmS16LE(resampled);

    // 4. Sequence number allocation
    const sequenceNumber = sourceId === AudioSourceId.REMOTE_TAB
      ? this.tabSequenceNumber++
      : this.micSequenceNumber++;

    // 5. Session relative timestamp
    const timestampMs = this.clock.getSessionRelativeMs();

    // 6. Encode into binary frame
    const binaryFrame = AudioFrameEncoder.encode(
      {
        protocolVersion: PROTOCOL_VERSION,
        meetingId: this.config.meetingId,
        sourceId,
        sequenceNumber,
        sessionRelativeTimestampMs: timestampMs,
        sampleRate: targetRate,
        channels: 1,
        sampleCount: pcmData.length,
      },
      pcmData
    );

    // 7. Dispatch frame
    this.config.onBinaryFrameReady(binaryFrame);
  }
}

