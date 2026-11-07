/**
 * FluentMeet AI - Meeting Platform Content Script
 * Embedded safely into Google Meet, Zoom Web, and MS Teams.
 * Tracks meeting state and participant changes without accessing private meeting data.
 * Specification: Step 05 - Section 4.2.E & Section 6
 */

import { platformDetector } from '../platforms/platform-detector';

const adapter = platformDetector.getActiveAdapter(document);

if (adapter) {
  adapter.detectMeeting(document).then((isActive) => {
    if (isActive) {
      adapter.getMeetingMetadata(document).then((meta) => {
        chrome.runtime.sendMessage({
          type: 'MEETING_PAGE_DETECTED',
          platform: meta.platform,
          url: meta.meetingUrl,
          title: meta.meetingTitle,
        }).catch(() => { });
      });

      // Observe participants and call termination
      adapter.observeMeetingChanges(
        document,
        (participants) => {
          chrome.runtime.sendMessage({
            type: 'PARTICIPANTS_UPDATED',
            meetingId: adapter.platform,
            participants,
          }).catch(() => { });
        },
        () => {
          chrome.runtime.sendMessage({
            type: 'SESSION_STATE_CHANGED',
            state: 'COMPLETED',
            sessionId: adapter.platform,
          }).catch(() => { });
        }
      );
    }
  }).catch(() => { });
}
