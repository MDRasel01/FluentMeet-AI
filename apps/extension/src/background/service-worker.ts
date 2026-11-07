/**
 * FluentMeet AI - Background Service Worker (Manifest V3)
 * Orchestrates extension lifecycle, tab capture stream acquisition, offscreen lifecycle,
 * and state persistence across worker terminations.
 * Specification: Step 05 - Section 4.2.B & Section 9.1
 */

import { SessionController } from './session-controller';
import { OffscreenManager } from './offscreen-manager';
import { platformDetector } from '../platforms/platform-detector';
import { ExtensionAuthAdapter } from '../utils/auth-adapter';

const sessionController = new SessionController();

// 1. Enable opening side panel when clicking the extension icon
chrome.sidePanel
  ?.setPanelBehavior({ openPanelOnActionClick: true })
  .catch((error: unknown) => console.error('Error setting side panel behavior:', error));

// 2. Track tab URL updates to detect supported meetings
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url) {
    const platform = platformDetector.detectPlatformType(tab.url);
    if (platform !== 'unknown') {
      sessionController.setPlatformDetected(platform, tab.url, tab.title);
    }
  }
});

// 3. Central message dispatcher
chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  const handleMessage = async () => {
    switch (message.type) {
      case 'CHECK_MEETING_STATUS': {
        const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true });
        const url = activeTab?.url || '';
        const platform = platformDetector.detectPlatformType(url);
        const currentSession = sessionController.getSession();

        return {
          isMeetingActive: platform !== 'unknown',
          platform,
          tabId: activeTab?.id,
          url,
          session: currentSession,
        };
      }

      case 'MEETING_PAGE_DETECTED': {
        sessionController.setPlatformDetected(message.platform, message.url, message.title);
        return { success: true };
      }

      case 'PARTICIPANTS_UPDATED': {
        sessionController.updateParticipants(message.participants);
        return { success: true };
      }

      case 'START_CAPTURE_COMMAND': {
        // Enforce user-initiated capture and valid session transition
        const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true });
        if (!activeTab || !activeTab.id) {
          throw new Error('No active meeting tab found to capture.');
        }

        sessionController.transition('STARTING', {
          meetingId: message.meetingId,
          title: message.title,
          platform: message.platform,
          meetingUrl: message.url,
          tabId: activeTab.id,
          consentConfirmed: true,
          startedAt: Date.now(),
        });

        // Step A: Ensure offscreen document exists (USER_MEDIA reason)
        await OffscreenManager.ensureOffscreenDocument();

        // Step B: Obtain Tab Media Stream ID (Chrome 116+)
        const streamId = await new Promise<string>((resolve, reject) => {
          chrome.tabCapture.getMediaStreamId({ targetTabId: activeTab.id }, (id) => {
            if (chrome.runtime.lastError || !id) {
              reject(new Error(chrome.runtime.lastError?.message || 'Failed to acquire tab stream ID.'));
            } else {
              resolve(id);
            }
          });
        });

        // Step C: Retrieve Auth Token for WebSocket connection
        const authSession = await ExtensionAuthAdapter.getSession();
        const token = authSession?.accessToken;

        // Step D: Instruct offscreen document to start dual capture & stream
        const offscreenResponse = await chrome.runtime.sendMessage({
          type: 'START_OFFSCREEN_CAPTURE',
          streamId,
          meetingId: message.meetingId,
          token,
          wsUrl: `ws://localhost:8000/ws/v1/sessions/${message.meetingId}`,
        });

        if (!offscreenResponse?.success) {
          sessionController.transition('FAILED', { error: offscreenResponse?.error || 'Capture failed' });
          throw new Error(offscreenResponse?.error || 'Offscreen capture failed to initialize.');
        }

        sessionController.transition('CAPTURING', { streamId });
        return { success: true, streamId };
      }

      case 'PAUSE_CAPTURE_COMMAND': {
        await chrome.runtime.sendMessage({ type: 'PAUSE_OFFSCREEN_CAPTURE' });
        sessionController.transition('PAUSED');
        return { success: true };
      }

      case 'RESUME_CAPTURE_COMMAND': {
        await chrome.runtime.sendMessage({ type: 'RESUME_OFFSCREEN_CAPTURE' });
        sessionController.transition('CAPTURING');
        return { success: true };
      }

      case 'STOP_CAPTURE_COMMAND': {
        sessionController.transition('STOPPING');
        await chrome.runtime.sendMessage({ type: 'STOP_OFFSCREEN_CAPTURE' }).catch(() => {});
        await OffscreenManager.closeOffscreenDocument();
        sessionController.transition('COMPLETED');
        return { success: true };
      }

      case 'SESSION_STATE_CHANGED': {
        if (message.state === 'FAILED') {
          sessionController.transition('FAILED', { error: message.error });
        }
        return { success: true };
      }

      case 'PING': {
        return { status: 'PONG', timestamp: Date.now() };
      }

      default:
        return { status: 'IGNORED' };
    }
  };

  handleMessage()
    .then((result) => sendResponse(result))
    .catch((err) => sendResponse({ success: false, error: err.message }));

  return true; // Keep message channel open for async response
});

console.log('[FluentMeet Service Worker] Initialized with Offscreen & Dual Pipeline orchestration.');
