/**
 * FluentMeet AI - Microsoft Teams Web Adapter
 * Specification: Step 05 - Section 6.3
 */

import { PlatformAdapter, MeetingPlatformMetadata } from '../platform-interface';
import { ParticipantMetadata } from '../../types/extension.types';

export class MicrosoftTeamsAdapter implements PlatformAdapter {
  public platform = 'teams' as const;
  private observer: MutationObserver | null = null;

  public matchesUrl(url: string): boolean {
    return /^https:\/\/teams\.microsoft\.com\/.*meet/i.test(url) ||
           url.includes('teams.microsoft.com/_#/modern-calling') ||
           url.includes('teams.live.com/meet');
  }

  public async detectMeeting(documentContext: Document): Promise<boolean> {
    const url = documentContext.location.href;
    if (!this.matchesUrl(url) && !url.includes('teams.microsoft.com')) return false;

    // Detect Teams meeting calling bar, hangup button, or roster
    const callingBar = documentContext.querySelector('#hangup-button, [data-tid="hangup-button"], [data-tid="call-roster-button"], [aria-label*="Leave"]');
    return Boolean(callingBar);
  }

  public async getMeetingMetadata(documentContext: Document): Promise<MeetingPlatformMetadata> {
    const url = documentContext.location.href;
    const titleEl = documentContext.querySelector('[data-tid="calling-title"], h1, [data-tid="chat-title"]');
    const title = titleEl?.textContent?.trim() || documentContext.title.replace(' | Microsoft Teams', '') || 'Teams Meeting';

    const participants = await this.getParticipantMetadata(documentContext);

    return {
      platform: 'teams',
      meetingId: `teams-${Date.now()}`,
      meetingUrl: url,
      meetingTitle: title,
      isActive: true,
      participantCount: participants.length,
      detectedAt: Date.now(),
    };
  }

  public async getParticipantMetadata(documentContext: Document): Promise<ParticipantMetadata[]> {
    const participants: ParticipantMetadata[] = [];
    const meetingId = 'teams-session';

    // Query Teams roster or video tile labels
    const rosterItems = documentContext.querySelectorAll(
      '[data-tid="roster-participant"], [data-tid="calling-roster-name"], [class*="participant-name"]'
    );
    const seen = new Set<string>();

    rosterItems.forEach((el, index) => {
      const name = el.textContent?.trim() || '';
      if (name && !seen.has(name)) {
        seen.add(name);
        const isSelf = name.toLowerCase().includes('(you)') || el.getAttribute('data-is-self') === 'true';
        participants.push({
          participantId: `teams-${index}`,
          meetingId,
          platform: 'teams',
          displayName: name.replace(/\(you\)/gi, '').trim(),
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
      if (documentContext.querySelector('[data-tid="call-ended-screen"], .call-ended')) {
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

