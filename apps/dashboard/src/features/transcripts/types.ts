export interface TranscriptWordUI {
  word: string;
  start_time_ms: number;
  end_time_ms: number;
  confidence_score?: number | null;
  is_overlapping?: boolean;
}

export interface TranscriptSegmentUI {
  id: string;
  meeting_id: string;
  speaker_id?: string | null;
  speaker_label?: string | null;
  speaker_name?: string | null;
  source_id: number;
  start_time_ms: number;
  end_time_ms: number;
  duration_ms: number;
  text: string;
  language: string;
  confidence_score?: number | null;
  status: "partial" | "provisional" | "final" | "corrected";
  revision_number: number;
  words?: TranscriptWordUI[];
  created_at?: string;
}

export interface MeetingSpeakerUI {
  id: string;
  meeting_id: string;
  speaker_label: string;
  display_name?: string | null;
  is_identified: boolean;
  confidence_score?: number | null;
  source_id?: number | null;
}

export interface SpeechOverlapUI {
  id: string;
  meeting_id: string;
  start_time_ms: number;
  end_time_ms: number;
  duration_ms: number;
  overlapping_speaker_ids: string[];
  confidence_score?: number | null;
}

