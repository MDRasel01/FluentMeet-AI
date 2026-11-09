/**
 * FluentMeet AI - Step 10 Frontend Types: Report Generation & Analytics
 */

export interface ReportSnapshot {
  id: string;
  meeting_id: string;
  tenant_id?: string | null;
  report_type: 'meeting_summary' | 'individual_participant';
  participant_id?: string | null;
  speaker_label?: string | null;
  report_version: number;
  report_status: string;
  overall_score?: number | null;
  confidence_score?: number | null;
  word_count: number;
  speaking_duration_seconds: number;
  source_analysis_version: string;
  scoring_rubric_version: string;
  report_payload: Record<string, any>;
  generated_at: string;
  created_at: string;
}

export interface ParticipantSummaryItem {
  participant_id?: string | null;
  speaker_label: string;
  display_name: string;
  overall_score?: number | null;
  status_label: string;
  word_count: number;
  duration_seconds: number;
  talk_time_percentage: number;
  ielts_band?: number | null;
}

export interface MeetingSummaryPayload {
  metadata: {
    meeting_id: string;
    title: string;
    meeting_date?: string | null;
    report_type: string;
    scoring_rubric_version: string;
  };
  summary_metrics: {
    participant_count: number;
    total_duration_seconds: number;
    total_words: number;
    average_overall_score?: number | null;
    calibrated_participants_count: number;
  };
  participants: ParticipantSummaryItem[];
  communication_balance: {
    distribution: Array<{ speaker: string; percentage: number }>;
  };
  highlights: string[];
  areas_for_team_growth: string[];
  disclaimers: {
    summary: string;
    ielts: string;
  };
}

export interface GrammarIssueItem {
  id?: string;
  rule_type: string;
  severity?: string;
  offending_text: string;
  corrected_text: string;
  explanation: string;
}

export interface MispronouncedWordItem {
  word: string;
  accuracy_score: number;
  phonemes_expected: string;
  phonemes_produced: string;
}

export interface RecommendationItem {
  source: string;
  category: string;
  priority: string;
  recommendation_text: string;
  practice_text?: string | null;
}

export interface ParticipantReportPayload {
  metadata: {
    meeting_id: string;
    participant_id?: string | null;
    speaker_label: string;
    display_name: string;
    scoring_rubric_version: string;
    report_type: string;
  };
  overall_performance: {
    overall_score?: number | null;
    confidence_score?: number | null;
    status_label: string;
    report_status: string;
    is_calibrated: boolean;
    missing_components: string[];
    validation_notes: string[];
  };
  speaking_metrics: {
    total_words: number;
    speaking_duration_seconds: number;
    words_per_minute: number;
  };
  grammar_analysis: {
    score?: number | null;
    issues_count: number;
    issues: GrammarIssueItem[];
  };
  vocabulary_analysis: {
    score?: number | null;
    insights: {
      lexical_diversity?: number | null;
      high_impact_words: string[];
      repetitive_words: string[];
    };
  };
  fluency_analysis: {
    score?: number | null;
    metrics: {
      words_per_minute: number;
      filler_word_count: number;
      pause_count: number;
      speech_rate_category: string;
    };
  };
  pronunciation_analysis: {
    score?: number | null;
    confidence?: number | null;
    mispronounced_words: MispronouncedWordItem[];
    prosody: Record<string, any>;
  };
  ielts_estimate?: {
    overall_band_estimate?: number;
    fluency_coherence_band?: number;
    lexical_resource_band?: number;
    grammatical_range_band?: number;
    pronunciation_band?: number;
    cefr_level?: string;
    band_descriptor_summary?: string;
    disclaimer: string;
  } | null;
  recommendations: RecommendationItem[];
  disclaimers: {
    ielts: string;
    scoring: string;
  };
}

export interface HistoricalPoint {
  meeting_id: string;
  meeting_date: string;
  report_id: string;
  overall_score?: number | null;
  grammar_score?: number | null;
  vocabulary_score?: number | null;
  fluency_score?: number | null;
  pronunciation_score?: number | null;
  ielts_overall_band?: number | null;
  word_count: number;
}

export interface HistoricalComparisonData {
  participant_id: string;
  speaker_name?: string | null;
  total_meetings: number;
  history_points: HistoricalPoint[];
  trends: {
    status: string;
    trajectory?: string;
    overall_delta?: number | null;
    message?: string;
  };
  recurring_mistakes: Array<{ rule_type: string; frequency: number }>;
  persistent_strengths: string[];
}
