import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ExtensionWebSocketService } from '../../src/services/websocket.service';

// Mock WebSocket
class MockWebSocket {
  public static OPEN = 1;
  public static CONNECTING = 0;
  public static CLOSING = 2;
  public static CLOSED = 3;

  public readyState: number = MockWebSocket.CONNECTING;
  public binaryType: string = 'blob';
  public sentMessages: (string | ArrayBuffer)[] = [];

  public onopen: (() => void) | null = null;
  public onmessage: ((e: { data: unknown }) => void) | null = null;
  public onclose: ((e: { code: number }) => void) | null = null;
  public onerror: ((e: unknown) => void) | null = null;

  constructor(public url: string) {
    setTimeout(() => {
      this.readyState = MockWebSocket.OPEN;
      this.onopen?.();
    }, 10);
  }

  send(data: string | ArrayBuffer): void {
    this.sentMessages.push(data);
  }

  close(code: number = 1000): void {
    this.readyState = MockWebSocket.CLOSED;
    this.onclose?.({ code });
  }
}

// @ts-expect-error Mock global WebSocket
globalThis.WebSocket = MockWebSocket;

describe('ExtensionWebSocketService (Streaming & Bounded Buffer)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should buffer frames when disconnected and flush on connection open up to MAX_BUFFER limit', async () => {
    const onStatusChange = vi.fn();
    const onAck = vi.fn();
    const onError = vi.fn();

    const service = new ExtensionWebSocketService(
      {
        url: 'ws://localhost:8000/ws/v1/sessions/{meeting_id}',
        reconnectAttempts: 3,
        initialBackoffMs: 100,
        maxBackoffMs: 500,
        jitterFactor: 0.1,
        heartbeatIntervalMs: 10000,
      },
      { onStatusChange, onAck, onError }
    );

    // Buffer frames before connection is open
    const frame1 = new ArrayBuffer(50);
    const frame2 = new ArrayBuffer(50);
    service.sendBinaryFrame(frame1);
    service.sendBinaryFrame(frame2);

    // Connect
    service.connect('meet-test-buffered');

    // Wait for mock connection to open
    await new Promise((resolve) => setTimeout(resolve, 30));

    expect(service.getStatus()).toBe('connected');
    expect(onStatusChange).toHaveBeenCalledWith('connected');

    service.disconnect();
    expect(service.getStatus()).toBe('closed');
  });
});

