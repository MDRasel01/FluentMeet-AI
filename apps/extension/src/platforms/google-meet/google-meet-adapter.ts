/**
 * FluentMeet AI - Google Meet Adapter
 * Specification: Step 05 - Section 6.1
 */

import { PlatformAdapter, MeetingPlatformMetadata } from '../platform-interface';
import { ParticipantMetadata } from '../../types/extension.types';

export class GoogleMeetAdapter implements PlatformAdapter {
  public platform = 'google-meet' as const;
  private observer: MutationObserver | null = null;

  public matchesUrl(url: string): boolean {
    return /^https:\/\/meet\.google\.com\/[a-z]{3}-[a-z]{4}-[a-z]{3}/.test(url);
  }

  public async detectMeeting(documentContext: Document): Promise<boolean> {
    const url = documentContext.location.href;
    if (!this.matchesUrl(url)) return false;

    // Verify active call indicators (e.g. leave call button, bottom bar, or video grid)
    const leaveButton = documentContext.querySelector('[aria-label*="Leave call"], [data-call-ended]');
    const callControls = documentContext.querySelector('[data-call-ui], [aria-label*="Call controls"], div[jscontroller]');
    return Boolean(leaveButton || callControls);
  }

  public async getMeetingMetadata(documentContext: Document): Promise<MeetingPlatformMetadata> {
    const url = documentContext.location.href;
    const match = url.match(/meet\.google\.com\/([a-z]{3}-[a-z]{4}-[a-z]{3})/);
    const meetingCode = match ? match[1] : 'unknown-meet';

    const titleEl = documentContext.querySelector('[data-meeting-title]');
    const title = titleEl?.textContent?.trim() || documentContext.title.replace(' - Google Meet', '') || 'Google Meet Call';

    const participants = await this.getParticipantMetadata(documentContext);

    return {
      platform: 'google-meet',
      meetingId: meetingCode,
      meetingUrl: url,
      meetingTitle: title,
      isActive: true,
      participantCount: participants.length,
      detectedAt: Date.now(),
    };
  }

  public async getParticipantMetadata(documentContext: Document): Promise<ParticipantMetadata[]> {
    const participants: ParticipantMetadata[] = [];
    const meetingUrl = documentContext.location.href;
    const match = meetingUrl.match(/meet\.google\.com\/([a-z]{3}-[a-z]{4}-[a-z]{3})/);
    const meetingId = match ? match[1] : 'google-meet';

    // Query participant name cards defensively
    const nameElements = documentContext.querySelectorAll('[data-self-name], div[data-participant-id], span.ZjFb7c, div.dwss8b');
    const seenNames = new Set<string>();

    nameElements.forEach((el, index) => {
      const name = el.textContent?.trim() || '';
      if (name && !seenNames.has(name) && name.length > 1 && !name.includes(':')) {
        seenNames.add(name);
        const isSelf = el.hasAttribute('data-self-name') || name.toLowerCase().includes('(you)');
        participants.push({
          participantId: `gmeet-${meetingId}-${index}`,
          meetingId,
          platform: 'google-meet',
          displayName: name.replace(/\(you\)/i, '').trim(),
          isLocalUser: isSelf,
          firstSeenAt: new Date().toISOString(),
          lastSeenAt: new Date().toISOString(),
          metadataSource: 'dom_selector',
          confidence: 0.9,
          mappingStatus: isSelf ? 'mapped' : 'unknown',
        });
      }
    });

    return participants;
  }

  public observeMeetingChanges(
    documentContext: Document,
    onParticipantChange: (participants: ParticipantMetadata[]) => void,
    onMeetingEnd: () => void
  ): () => void {
    this.cleanup();

    this.observer = new MutationObserver(() => {
      // Check if call ended
      if (documentContext.querySelector('[data-call-ended="true"]')) {
        onMeetingEnd();
        return;
      }

      this.getParticipantMetadata(documentContext).then((parts) => {
        if (parts.length > 0) {
          onParticipantChange(parts);
        }
      }).catch(() => {});
    });

    this.observer.observe(documentContext.body, {
      childList: true,
      subtree: true,
    });

    return () => this.cleanup();
  }

  public cleanup(): void {
    if (this.observer) {
      this.observer.disconnect();
      this.observer = null;
    }
  }
}

