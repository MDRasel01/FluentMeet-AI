/**
 * FluentMeet AI - Zoom Web Client Adapter
 * Specification: Step 05 - Section 6.2
 */

import { PlatformAdapter, MeetingPlatformMetadata } from '../platform-interface';
import { ParticipantMetadata } from '../../types/extension.types';

export class ZoomWebAdapter implements PlatformAdapter {
  public platform = 'zoom' as const;
  private observer: MutationObserver | null = null;

  public matchesUrl(url: string): boolean {
    return /zoom\.us\/(wc|j)\/[0-9]+/.test(url);
  }

  public async detectMeeting(documentContext: Document): Promise<boolean> {
    const url = documentContext.location.href;
    if (!this.matchesUrl(url)) return false;

    // Look for footer controls, participant button, or leave button in Zoom Web UI
    const controls = documentContext.querySelector('.footer, .meeting-control, [aria-label*="Leave"], button.leave-meeting');
    return Boolean(controls);
  }

  public async getMeetingMetadata(documentContext: Document): Promise<MeetingPlatformMetadata> {
    const url = documentContext.location.href;
    const match = url.match(/zoom\.us\/(?:wc|j)\/([0-9]+)/);
    const meetingCode = match ? match[1] : 'unknown-zoom';

    const title = documentContext.title.replace(' - Zoom', '') || 'Zoom Web Meeting';
    const participants = await this.getParticipantMetadata(documentContext);

    return {
      platform: 'zoom',
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
    const match = meetingUrl.match(/zoom\.us\/(?:wc|j)\/([0-9]+)/);
    const meetingId = match ? match[1] : 'zoom';

    // Search Zoom participant sidebar or speaker cards
    const participantElements = documentContext.querySelectorAll(
      '.participants-item__display-name, .speaker-name, [class*="participant-name"]'
    );
    const seen = new Set<string>();

    participantElements.forEach((el, index) => {
      const name = el.textContent?.trim() || '';
      if (name && !seen.has(name)) {
        seen.add(name);
        const isSelf = name.toLowerCase().includes('(me)') || name.toLowerCase().includes('(host, me)');
        participants.push({
          participantId: `zoom-${meetingId}-${index}`,
          meetingId,
          platform: 'zoom',
          displayName: name.replace(/\(me\)|\(host\)/gi, '').trim(),
          isLocalUser: isSelf,
          firstSeenAt: new Date().toISOString(),
          lastSeenAt: new Date().toISOString(),
          metadataSource: 'dom_selector',
          confidence: 0.85,
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
      if (documentContext.querySelector('.meeting-ended, .leave-dialog')) {
        onMeetingEnd();
        return;
      }

      this.getParticipantMetadata(documentContext).then((parts) => {
        if (parts.length > 0) {
          onParticipantChange(parts);
        }
      }).catch(() => {});
    });

    this.observer.observe(documentContext.body, { childList: true, subtree: true });
    return () => this.cleanup();
  }

  public cleanup(): void {
    if (this.observer) {
      this.observer.disconnect();
      this.observer = null;
    }
  }
}

