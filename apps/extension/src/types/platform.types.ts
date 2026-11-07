/**
 * FluentMeet AI - Meeting Platform Adapter Types
 * Specification: Step 05 - Section 4.2.E & Section 6
 */

import { MeetingPlatform, ParticipantMetadata } from './extension.types';

export interface MeetingPlatformMetadata {
  platform: MeetingPlatform;
  meetingId: string;
  meetingUrl: string;
  meetingTitle?: string;
  isActive: boolean;
  participantCount: number;
  detectedAt: number;
}

export interface PlatformAdapter {
  platform: MeetingPlatform;
  matchesUrl(url: string): boolean;
  detectMeeting(documentContext: Document): Promise<boolean>;
  getMeetingMetadata(documentContext: Document): Promise<MeetingPlatformMetadata>;
  getParticipantMetadata(documentContext: Document): Promise<ParticipantMetadata[]>;
  observeMeetingChanges(
    documentContext: Document,
    onParticipantChange: (participants: ParticipantMetadata[]) => void,
    onMeetingEnd: () => void
  ): () => void; // Returns unsubscribe / cleanup callback
  cleanup(): void;
}

