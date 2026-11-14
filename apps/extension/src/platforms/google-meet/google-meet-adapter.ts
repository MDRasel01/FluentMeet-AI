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
    const seenNames = new Set<string>();

    const cleanMeetName = (rawText: string): string => {
      if (!rawText) return '';
      let text = rawText;

      // Strip common Google Meet action strings & material icons names
      text = text.replace(/keep_off|keep_outline|volume_off|volume_up|more_vert|zoom_in|open_in_new|open_in_full|devices/gi, ' ');
      text = text.replace(/Unpin\s+.*?\s+from your main screen/gi, ' ');
      text = text.replace(/Pin\s+.*?\s+to your main screen/gi, ' ');
      text = text.replace(/More options for\s+.*?/gi, ' ');
      text = text.replace(/You can't unmute someone else's presentation/gi, ' ');
      text = text.replace(/You can't unmute someone else/gi, ' ');
      text = text.replace(/\bpresentation\b/gi, ' ');
      text = text.replace(/\(you\)/gi, ' ');
      text = text.replace(/\s+/g, ' ').trim();

      // De-duplicate if the name is repeated (e.g. "Rafi KhanRafi Khan" -> "Rafi Khan")
      const words = text.split(' ').filter(Boolean);
      if (words.length >= 2 && words.length % 2 === 0) {
        const half = words.length / 2;
        const firstHalf = words.slice(0, half).join(' ');
        const secondHalf = words.slice(half).join(' ');
        if (firstHalf.toLowerCase() === secondHalf.toLowerCase()) {
          text = firstHalf;
        }
      }

      return text.trim();
    };

    // 1. Primary Targeted Selectors for Clean Names (Google Meet DOM)
    // span.zWGUib: Name in the People / Participant roster panel
    // span.ZjFb7c: Name on the Video Tile badge
    // [data-self-name]: Local speaker name attribute
    const candidateNodes = documentContext.querySelectorAll(
      'span.zWGUib, span.ZjFb7c, [data-self-name], div[data-participant-id]'
    );

    candidateNodes.forEach((node, index) => {
      let rawName = '';
      let isSelf = false;
      let avatarUrl: string | undefined = undefined;

      // Extract name directly
      if (node.hasAttribute('data-self-name')) {
        rawName = node.getAttribute('data-self-name') || '';
        isSelf = true;
      } else {
        // Prefer child clean name span if inside a container
        const innerNameEl = node.querySelector('span.zWGUib, span.ZjFb7c, .notranslate');
        if (innerNameEl) {
          rawName = innerNameEl.textContent || '';
        } else {
          rawName = node.textContent || '';
        }
      }

      const cleanedName = cleanMeetName(rawName);

      // Validate name
      if (
        cleanedName &&
        cleanedName.length >= 2 &&
        !seenNames.has(cleanedName.toLowerCase()) &&
        !cleanedName.toLowerCase().includes('presentation') &&
        !cleanedName.toLowerCase().includes('meeting details')
      ) {
        seenNames.add(cleanedName.toLowerCase());

        // Extract Google Profile Avatar / Photo if available
        const container = node.closest('[data-participant-id], div[role="listitem"], div.dwss8b, div[jscontroller]') || node;
        const imgEl = container.querySelector('img[src*="googleusercontent.com"], img[src*="profile"], img') as HTMLImageElement | null;
        if (imgEl && imgEl.src && !imgEl.src.startsWith('data:image/svg')) {
          avatarUrl = imgEl.src;
        }

        if (cleanedName.toLowerCase().includes('(you)')) {
          isSelf = true;
        }

        participants.push({
          participantId: `gmeet-${meetingId}-${index}`,
          meetingId,
          platform: 'google-meet',
          displayName: cleanedName,
          avatarUrl,
          isLocalUser: isSelf,
          firstSeenAt: new Date().toISOString(),
          lastSeenAt: new Date().toISOString(),
          metadataSource: 'dom_selector',
          confidence: 0.95,
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

