/**
 * FluentMeet AI - Offscreen Document Controller
 * Consumes MediaStream, runs AudioWorklet, and streams binary audio to WebSocket.
 * Specification: Step 05 - Section 4.2.C
 */

import { AudioManager } from './audio-manager';
import { ExtensionWebSocketService } from '../services/websocket.service';
import { AudioSourceId } from '../types/audio.types';

let audioManager: AudioManager | null = null;
let wsService: ExtensionWebSocketService | null = null;

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.type === 'START_OFFSCREEN_CAPTURE') {
    const { streamId, meetingId, wsUrl, token } = message;

    // 1. Initialize WebSocket Service
    wsService = new ExtensionWebSocketService(
      {
        url: wsUrl || `ws://localhost:8000/ws/v1/sessions/${meetingId}`,
        token,
        reconnectAttempts: 5,
        initialBackoffMs: 1000,
        maxBackoffMs: 8000,
        jitterFactor: 0.25,
        heartbeatIntervalMs: 15000,
      },
      {
        onStatusChange: (status) => {
          chrome.runtime.sendMessage({
            type: 'SESSION_STATE_CHANGED',
            state: status === 'connected' ? 'CAPTURING' : status.toUpperCase(),
            sessionId: meetingId,
          }).catch(() => {});
        },
        onAck: (ack) => {
          // Acknowledged chunk received from backend
        },
        onError: (err) => {
          chrome.runtime.sendMessage({
            type: 'SESSION_STATE_CHANGED',
            state: 'FAILED',
            sessionId: meetingId,
            error: err.message,
          }).catch(() => {});
        },
      }
    );

    wsService.connect(meetingId, token);

    // 2. Initialize Audio Manager
    const workletUrl = chrome.runtime.getURL('src/offscreen/audio-worklet/pcm-processor.js');

    audioManager = new AudioManager({
      targetSampleRate: 16000,
      workletUrl,
      meetingId,
      onBinaryFrameReady: (frame) => {
        if (wsService) {
          wsService.sendBinaryFrame(frame);
        }
      },
      onMetricsUpdate: (metrics) => {
        chrome.runtime.sendMessage({
          type: 'OFFSCREEN_AUDIO_METRICS',
          sourceId: metrics.sourceId,
          rmsVolume: metrics.rmsVolume,
          peakVolume: metrics.peakVolume,
          isClipping: metrics.isClipping,
          isSilent: metrics.isSilent,
        }).catch(() => {});
      },
      onError: (sourceId, error) => {
        chrome.runtime.sendMessage({
          type: 'OFFSCREEN_AUDIO_STOPPED',
          sourceId,
          error: error.message,
        }).catch(() => {});
      },
    });

    audioManager
      .start(streamId)
      .then(() => {
        sendResponse({ success: true });
      })
      .catch((err) => {
        sendResponse({ success: false, error: err.message });
      });

    return true; // Keep response channel open
  }

  if (message.type === 'PAUSE_OFFSCREEN_CAPTURE') {
    if (audioManager) {
      audioManager.pause();
    }
    if (wsService) {
      wsService.sendMessage({ type: 'capture_paused', timestamp: new Date().toISOString() });
    }
    sendResponse({ success: true });
    return false;
  }

  if (message.type === 'RESUME_OFFSCREEN_CAPTURE') {
    if (audioManager) {
      audioManager.resume();
    }
    if (wsService) {
      wsService.sendMessage({ type: 'capture_resumed', timestamp: new Date().toISOString() });
    }
    sendResponse({ success: true });
    return false;
  }

  if (message.type === 'STOP_OFFSCREEN_CAPTURE') {
    if (audioManager) {
      audioManager.stop();
      audioManager = null;
    }
    if (wsService) {
      wsService.disconnect();
      wsService = null;
    }
    sendResponse({ success: true });
    return false;
  }
});

