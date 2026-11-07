/**
 * FluentMeet AI - Extension WebSocket Manager
 * Manages real-time binary audio streaming, acknowledgement tracking, and jittered backoff reconnection.
 * Specification: Step 05 - Section 12
 */

import { AudioAckMessage, BaseWebSocketMessage, SessionInitMessage, WebSocketConfig } from '../types/websocket.types';
import { AudioSourceId } from '../types/audio.types';

export type WebSocketStatus = 'disconnected' | 'connecting' | 'connected' | 'reconnecting' | 'closed';

export interface WebSocketServiceCallbacks {
  onStatusChange: (status: WebSocketStatus) => void;
  onAck: (ack: AudioAckMessage) => void;
  onError: (error: Error) => void;
  onSessionReady?: () => void;
  onSessionCompleted?: () => void;
}

export class ExtensionWebSocketService {
  private socket: WebSocket | null = null;
  private config: WebSocketConfig;
  private callbacks: WebSocketServiceCallbacks;
  private status: WebSocketStatus = 'disconnected';
  private reconnectAttempt: number = 0;
  private reconnectTimer: number | null = null;
  private heartbeatTimer: number | null = null;

  // Bounded buffer for temporary network interruptions (Section 12.3)
  private readonly MAX_BUFFERED_FRAMES = 100;
  private bufferedFrames: ArrayBuffer[] = [];

  constructor(config: WebSocketConfig, callbacks: WebSocketServiceCallbacks) {
    this.config = config;
    this.callbacks = callbacks;
  }

  public connect(meetingId: string, token?: string): void {
    if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
      return;
    }

    this.setStatus('connecting');
    const wsUrl = token
      ? `${this.config.url.replace('{meeting_id}', meetingId)}?token=${encodeURIComponent(token)}`
      : this.config.url.replace('{meeting_id}', meetingId);

    try {
      this.socket = new WebSocket(wsUrl);
      this.socket.binaryType = 'arraybuffer';

      this.socket.onopen = () => {
        this.reconnectAttempt = 0;
        this.setStatus('connected');
        this.startHeartbeat();

        // Send session_init handshake
        const initMsg: SessionInitMessage = {
          type: 'session_init',
          sessionId: meetingId,
          meetingId,
          platform: 'browser',
          audioSources: [AudioSourceId.REMOTE_TAB, AudioSourceId.LOCAL_MIC],
          sampleRate: 16000,
          channels: 1,
          encoding: 'pcm_s16le',
          clientVersion: '1.0.0',
          timestamp: new Date().toISOString(),
        };
        this.sendMessage(initMsg);

        // Flush bounded buffer
        this.flushBuffer();
      };

      this.socket.onmessage = (event: MessageEvent) => {
        if (typeof event.data === 'string') {
          try {
            const data = JSON.parse(event.data);
            if (data.type === 'audio_ack') {
              this.callbacks.onAck(data as AudioAckMessage);
            } else if (data.type === 'session_ready') {
              this.callbacks.onSessionReady?.();
            } else if (data.type === 'session_completed') {
              this.callbacks.onSessionCompleted?.();
            }
          } catch (e) {
            console.error('Failed to parse WebSocket JSON message:', e);
          }
        }
      };

      this.socket.onerror = (event) => {
        console.error('WebSocket connection error:', event);
        this.callbacks.onError(new Error('WebSocket connection error'));
      };

      this.socket.onclose = (event) => {
        this.stopHeartbeat();
        if (this.status === 'closed') {
          return;
        }
        if (event.code !== 1000) {
          this.scheduleReconnect(meetingId, token);
        } else {
          this.setStatus('disconnected');
        }
      };
    } catch (err: unknown) {
      this.callbacks.onError(err instanceof Error ? err : new Error(String(err)));
      this.scheduleReconnect(meetingId, token);
    }
  }

  public sendBinaryFrame(frame: ArrayBuffer): boolean {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(frame);
      return true;
    } else {
      // Buffer frame up to limit
      if (this.bufferedFrames.length < this.MAX_BUFFERED_FRAMES) {
        this.bufferedFrames.push(frame);
      } else {
        // Drop oldest frame to maintain bounded memory per Section 17
        this.bufferedFrames.shift();
        this.bufferedFrames.push(frame);
      }
      return false;
    }
  }

  public sendMessage(message: BaseWebSocketMessage | Record<string, unknown>): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    }
  }

  public disconnect(): void {
    this.setStatus('closed');
    this.stopHeartbeat();
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.socket) {
      try {
        if (this.socket.readyState === WebSocket.OPEN) {
          this.socket.send(JSON.stringify({ type: 'session_stop', timestamp: new Date().toISOString() }));
        }
        this.socket.close(1000, 'Normal extension disconnect');
      } catch (_) {}
      this.socket = null;
    }
    this.bufferedFrames = [];
  }

  public getStatus(): WebSocketStatus {
    return this.status;
  }

  private setStatus(status: WebSocketStatus): void {
    this.status = status;
    this.callbacks.onStatusChange(status);
  }

  private scheduleReconnect(meetingId: string, token?: string): void {
    if (this.reconnectAttempt >= this.config.reconnectAttempts) {
      this.setStatus('disconnected');
      this.callbacks.onError(new Error('Max WebSocket reconnect attempts reached.'));
      return;
    }

    this.setStatus('reconnecting');
    this.reconnectAttempt++;

    // Exponential backoff with jitter (Section 12.3)
    const baseBackoff = Math.min(
      this.config.maxBackoffMs,
      this.config.initialBackoffMs * Math.pow(2, this.reconnectAttempt - 1)
    );
    const jitter = baseBackoff * this.config.jitterFactor * (Math.random() - 0.5) * 2;
    const delay = Math.max(500, Math.round(baseBackoff + jitter));

    this.reconnectTimer = window.setTimeout(() => {
      this.connect(meetingId, token);
    }, delay);
  }

  private flushBuffer(): void {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) return;
    while (this.bufferedFrames.length > 0) {
      const frame = this.bufferedFrames.shift();
      if (frame) {
        this.socket.send(frame);
      }
    }
  }

  private startHeartbeat(): void {
    this.stopHeartbeat();
    this.heartbeatTimer = window.setInterval(() => {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.socket.send(JSON.stringify({ type: 'heartbeat', timestamp: new Date().toISOString() }));
      }
    }, this.config.heartbeatIntervalMs || 15000);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }
}
