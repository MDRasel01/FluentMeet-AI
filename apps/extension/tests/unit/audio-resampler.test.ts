import { describe, it, expect } from 'vitest';
import { AudioResampler } from '../../src/offscreen/audio-resampler';

describe('AudioResampler (Signal Processing)', () => {
  it('should resample 48 kHz float audio to 16 kHz accurately', () => {
    // Generate 480 samples at 48 kHz (10 ms of audio)
    const input = new Float32Array(480);
    for (let i = 0; i < input.length; i++) {
      input[i] = Math.sin((2 * Math.PI * 440 * i) / 48000); // 440 Hz sine wave
    }

    const resampled = AudioResampler.resample(input, 48000, 16000);

    // 480 / 3 = 160 samples at 16 kHz
    expect(resampled.length).toBe(160);
    expect(resampled[0]).toBeCloseTo(input[0], 2);
  });

  it('should convert Float32 [-1.0, 1.0] to Signed 16-bit PCM (S16LE) with clamping', () => {
    const input = new Float32Array([-1.5, -1.0, 0.0, 0.5, 1.0, 1.5]);
    const pcm = AudioResampler.floatToPcmS16LE(input);

    expect(pcm[0]).toBe(-32768); // Clamped to -1.0 min
    expect(pcm[1]).toBe(-32768);
    expect(pcm[2]).toBe(0);
    expect(pcm[3]).toBe(16383);
    expect(pcm[4]).toBe(32767);
    expect(pcm[5]).toBe(32767); // Clamped to +1.0 max
  });

  it('should calculate signal metrics: silence, clipping, and RMS levels', () => {
    // 1. Silent samples
    const silentSamples = new Float32Array(100).fill(0);
    const silentMetrics = AudioResampler.calculateMetrics(silentSamples);
    expect(silentMetrics.isSilent).toBe(true);
    expect(silentMetrics.isClipping).toBe(false);
    expect(silentMetrics.rmsVolume).toBe(0);

    // 2. Normal speech samples
    const normalSamples = new Float32Array(100).fill(0.25);
    const normalMetrics = AudioResampler.calculateMetrics(normalSamples);
    expect(normalMetrics.isSilent).toBe(false);
    expect(normalMetrics.isClipping).toBe(false);
    expect(normalMetrics.rmsVolume).toBeGreaterThan(0);

    // 3. Clipping samples
    const clippingSamples = new Float32Array(100).fill(1.0);
    const clippingMetrics = AudioResampler.calculateMetrics(clippingSamples);
    expect(clippingMetrics.isClipping).toBe(true);
  });
});

