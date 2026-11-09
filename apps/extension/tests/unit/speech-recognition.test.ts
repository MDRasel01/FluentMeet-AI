import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { SpeechRecognitionService } from '../../src/services/speech-recognition.service';

describe('SpeechRecognitionService', () => {
  let service: SpeechRecognitionService;
  let activeMockInstance: any;
  let mockMediaStream: any;
  let mockTrack: any;

  class MockSpeechRecognition {
    continuous = false;
    interimResults = false;
    lang = 'en-US';
    maxAlternatives = 1;
    start = vi.fn();
    stop = vi.fn();
    abort = vi.fn();
    onstart: any = null;
    onaudiostart: any = null;
    onresult: any = null;
    onerror: any = null;
    onend: any = null;

    constructor() {
      activeMockInstance = this;
    }
  }

  beforeEach(() => {
    service = new SpeechRecognitionService();
    activeMockInstance = null;

    mockTrack = {
      stop: vi.fn(),
    };

    mockMediaStream = {
      getTracks: vi.fn().mockReturnValue([mockTrack]),
    };

    // Attach mock constructor to window
    (window as any).webkitSpeechRecognition = MockSpeechRecognition;

    // Mock navigator.mediaDevices.getUserMedia
    Object.defineProperty(navigator, 'mediaDevices', {
      value: {
        getUserMedia: vi.fn().mockResolvedValue(mockMediaStream),
      },
      writable: true,
      configurable: true,
    });
  });

  afterEach(() => {
    service.stop();
    delete (window as any).SpeechRecognition;
    delete (window as any).webkitSpeechRecognition;
    vi.restoreAllMocks();
  });

  it('correctly reports browser support', () => {
    expect(service.isSupported()).toBe(true);

    delete (window as any).SpeechRecognition;
    delete (window as any).webkitSpeechRecognition;
    expect(service.isSupported()).toBe(false);
  });

  it('starts recognition and transitions to LISTENING onstart event', async () => {
    const onStateChange = vi.fn();
    const onError = vi.fn();
    const onFinalResult = vi.fn();
    const onInterimResult = vi.fn();
    const onEnd = vi.fn();

    await service.start({
      onStateChange,
      onError,
      onFinalResult,
      onInterimResult,
      onEnd,
    });

    expect(navigator.mediaDevices.getUserMedia).toHaveBeenCalledWith({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
      },
      video: false,
    });

    expect(activeMockInstance).toBeDefined();
    expect(activeMockInstance.start).toHaveBeenCalled();

    // Trigger onstart event
    activeMockInstance.onstart();
    expect(service.getState()).toBe('LISTENING');
    expect(onStateChange).toHaveBeenCalledWith('LISTENING');
  });

  it('dispatches interim results correctly', async () => {
    const onInterimResult = vi.fn();
    const onFinalResult = vi.fn();

    await service.start({
      onStateChange: vi.fn(),
      onError: vi.fn(),
      onFinalResult,
      onInterimResult,
      onEnd: vi.fn(),
    });

    activeMockInstance.onstart();

    // Simulate interim result event
    const mockEvent = {
      resultIndex: 0,
      results: [
        [
          {
            transcript: 'hello world',
          },
        ],
      ],
    };
    (mockEvent.results[0] as any).isFinal = false;

    activeMockInstance.onresult(mockEvent);

    expect(onInterimResult).toHaveBeenCalledWith('hello world');
    expect(onFinalResult).not.toHaveBeenCalled();
  });

  it('dispatches finalized transcript items on final result', async () => {
    const onInterimResult = vi.fn();
    const onFinalResult = vi.fn();

    await service.start({
      onStateChange: vi.fn(),
      onError: vi.fn(),
      onFinalResult,
      onInterimResult,
      onEnd: vi.fn(),
    });

    activeMockInstance.onstart();

    // Simulate final result event
    const mockEvent = {
      resultIndex: 0,
      results: [
        [
          {
            transcript: 'Let us begin the architecture review.',
            confidence: 0.95,
          },
        ],
      ],
    };
    (mockEvent.results[0] as any).isFinal = true;

    activeMockInstance.onresult(mockEvent);

    expect(onFinalResult).toHaveBeenCalledWith(
      expect.objectContaining({
        text: 'Let us begin the architecture review.',
        isFinal: true,
        confidence: 0.95,
      })
    );
    expect(onInterimResult).toHaveBeenCalledWith('');
    expect(service.getState()).toBe('LISTENING');
  });

  it('handles microphone permission denial error', async () => {
    const permissionError = new Error('Permission denied');
    permissionError.name = 'NotAllowedError';
    (navigator.mediaDevices.getUserMedia as any).mockRejectedValueOnce(permissionError);

    const onError = vi.fn();

    await service.start({
      onStateChange: vi.fn(),
      onError,
      onFinalResult: vi.fn(),
      onInterimResult: vi.fn(),
      onEnd: vi.fn(),
    });

    expect(service.getState()).toBe('ERROR');
    expect(onError).toHaveBeenCalledWith(
      expect.stringContaining('Microphone permission was denied'),
      'PERMISSION_DENIED'
    );
  });

  it('stops recognition cleanly and releases media tracks', async () => {
    const onEnd = vi.fn();

    await service.start({
      onStateChange: vi.fn(),
      onError: vi.fn(),
      onFinalResult: vi.fn(),
      onInterimResult: vi.fn(),
      onEnd,
    });

    const instanceToStop = activeMockInstance;
    service.stop();

    expect(instanceToStop.stop).toHaveBeenCalled();
    expect(mockTrack.stop).toHaveBeenCalled();
    expect(service.getState()).toBe('STOPPED');
    expect(onEnd).toHaveBeenCalled();
  });
});
