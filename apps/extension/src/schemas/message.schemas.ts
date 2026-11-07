/**
 * FluentMeet AI - Runtime Communication Validation Schemas (Zod)
 * Specification: Step 05 - Section 3, Section 7, Section 18
 */

import { z } from 'zod';

export const MeetingPlatformSchema = z.enum(['google-meet', 'zoom', 'teams', 'unknown']);

export const ParticipantMetadataSchema = z.object({
  participantId: z.string(),
  meetingId: z.string(),
  platform: MeetingPlatformSchema,
  displayName: z.string(),
  platformUserId: z.string().optional(),
  isLocalUser: z.boolean(),
  firstSeenAt: z.string(),
  lastSeenAt: z.string(),
  metadataSource: z.enum(['dom_selector', 'mutation_observer', 'user_profile']),
  confidence: z.number().min(0).max(1),
  mappingStatus: z.enum(['mapped', 'unknown', 'provisional']),
});

export const RuntimeMessageSchema = z.discriminatedUnion('type', [
  z.object({
    type: z.literal('CHECK_MEETING_STATUS'),
  }),
  z.object({
    type: z.literal('MEETING_PAGE_DETECTED'),
    platform: MeetingPlatformSchema,
    url: z.string(),
    title: z.string().optional(),
  }),
  z.object({
    type: z.literal('START_CAPTURE_COMMAND'),
    meetingId: z.string(),
    title: z.string(),
    platform: MeetingPlatformSchema,
    url: z.string(),
  }),
  z.object({
    type: z.literal('PAUSE_CAPTURE_COMMAND'),
    meetingId: z.string(),
  }),
  z.object({
    type: z.literal('RESUME_CAPTURE_COMMAND'),
    meetingId: z.string(),
  }),
  z.object({
    type: z.literal('STOP_CAPTURE_COMMAND'),
    meetingId: z.string(),
  }),
  z.object({
    type: z.literal('OFFSCREEN_AUDIO_STARTED'),
    sourceId: z.number(),
    streamId: z.string().optional(),
  }),
  z.object({
    type: z.literal('OFFSCREEN_AUDIO_STOPPED'),
    sourceId: z.number(),
  }),
  z.object({
    type: z.literal('OFFSCREEN_AUDIO_METRICS'),
    sourceId: z.number(),
    rmsVolume: z.number(),
    peakVolume: z.number(),
    isClipping: z.boolean(),
    isSilent: z.boolean(),
  }),
  z.object({
    type: z.literal('PARTICIPANTS_UPDATED'),
    meetingId: z.string(),
    participants: z.array(ParticipantMetadataSchema),
  }),
  z.object({
    type: z.literal('SESSION_STATE_CHANGED'),
    state: z.string(),
    sessionId: z.string(),
    error: z.string().optional(),
  }),
  z.object({
    type: z.literal('PING'),
  }),
]);

export type RuntimeMessage = z.infer<typeof RuntimeMessageSchema>;

