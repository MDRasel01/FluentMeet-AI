import { describe, it, expect } from 'vitest';
import { AudioFrameEncoder, PROTOCOL_VERSION } from '../../src/utils/audio-encoder';
import { AudioSourceId } from '../../src/types/audio.types';

describe('AudioFrameEncoder (Binary Audio Protocol)', () => {
  it('should encode and decode binary audio frame accurately preserving all metadata and PCM samples', () => {
    const meetingId = 'meet-test-xyz';
    const sampleRate = 16000;
    const channels = 1;
    const sequenceNumber = 105;
    const timestampMs = 3450.5;

    // Create 100 mock S16LE PCM samples
    const pcmSamples = new Int16Array(100);
    for (let i = 0; i < 100; i++) {
      pcmSamples[i] = (i * 300) - 15000;
    }

    const encodedBuffer = AudioFrameEncoder.encode(
      {
        protocolVersion: PROTOCOL_VERSION,
        meetingId,
        sourceId: AudioSourceId.REMOTE_TAB,
        sequenceNumber,
        sessionRelativeTimestampMs: timestampMs,
        sampleRate,
        channels,
        sampleCount: pcmSamples.length,
      },
      pcmSamples
    );

    expect(encodedBuffer).toBeInstanceOf(ArrayBuffer);
    expect(encodedBuffer.byteLength).toBe(23 + meetingId.length + pcmSamples.byteLength);

    // Decode frame
    const decoded = AudioFrameEncoder.decode(encodedBuffer);
    expect(decoded.protocolVersion).toBe(PROTOCOL_VERSION);
    expect(decoded.meetingId).toBe(meetingId);
    expect(decoded.sourceId).toBe(AudioSourceId.REMOTE_TAB);
    expect(decoded.sequenceNumber).toBe(sequenceNumber);
    expect(decoded.sessionRelativeTimestampMs).toBe(timestampMs);
    expect(decoded.sampleRate).toBe(sampleRate);
    expect(decoded.channels).toBe(channels);
    expect(decoded.sampleCount).toBe(pcmSamples.length);

    // Verify PCM data matches exactly
    const decodedPcm = new Int16Array(decoded.data);
    expect(decodedPcm.length).toBe(pcmSamples.length);
    for (let i = 0; i < 100; i++) {
      expect(decodedPcm[i]).toBe(pcmSamples[i]);
    }
  });

  it('should correctly distinguish local microphone from remote tab audio source IDs', () => {
    const pcmSamples = new Int16Array([100, 200, 300]);
    const tabBuffer = AudioFrameEncoder.encode(
      {
        protocolVersion: PROTOCOL_VERSION,
        meetingId: 'meet-1',
        sourceId: AudioSourceId.REMOTE_TAB,
        sequenceNumber: 1,
        sessionRelativeTimestampMs: 100,
        sampleRate: 16000,
        channels: 1,
        sampleCount: 3,
      },
      pcmSamples
    );

    const micBuffer = AudioFrameEncoder.encode(
      {
        protocolVersion: PROTOCOL_VERSION,
        meetingId: 'meet-1',
        sourceId: AudioSourceId.LOCAL_MIC,
        sequenceNumber: 1,
        sessionRelativeTimestampMs: 100,
        sampleRate: 16000,
        channels: 1,
        sampleCount: 3,
      },
      pcmSamples
    );

    const decodedTab = AudioFrameEncoder.decode(tabBuffer);
    const decodedMic = AudioFrameEncoder.decode(micBuffer);

    expect(decodedTab.sourceId).toBe(AudioSourceId.REMOTE_TAB);
    expect(decodedMic.sourceId).toBe(AudioSourceId.LOCAL_MIC);
    expect(decodedTab.sourceId).not.toBe(decodedMic.sourceId);
  });
});

