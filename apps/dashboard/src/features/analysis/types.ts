export interface CategoryScoreUI {
  category: string;
  score: number | null;
  status: "available" | "insufficient_data" | "unavailable";
  evidence_count: number;
  confidence?: number | null;
}

export interface GrammarIssueUI {
  id: string;
  transcript_segment_id?: string | null;
  category: string;
  original_text: string;
  corrected_text: string;
  explanation: string;
  rule_name?: string | null;
  suggested_alternative?: string | null;
  severity: "minor" | "moderate" | "major";
  confidence?: number | null;
  evidence_status: string;
}

export interface VocabularyInsightUI {
  id: string;
  transcript_segment_id?: string | null;
  original_expression: string;
  suggested_expression: string;
  explanation: string;
  insight_type: string;
  context_note?: string | null;
  example_sentence?: string | null;
  confidence?: number | null;
}

export interface FluencyMetricUI {
  id: string;
  metric_name: string;
  metric_value: number;
  unit: string;
  evidence_count: number;
  confidence?: number | null;
}

export interface CommunicationInsightUI {
  id: string;
  insight_type: string;
  title: string;
  description: string;
  evidence?: string | null;
  confidence?: number | null;
}

export interface RecommendationUI {
  id: string;
  skill_category: string;
  priority: "high" | "medium" | "low";
  title: string;
  actionable_suggestion: string;
  evidence_reference?: string | null;
  example?: string | null;
  expected_outcome?: string | null;
  status: string;
}

export interface ParticipantSummaryUI {
  id: string;
  speaker_id?: string | null;
  participant_id?: string | null;
  speaker_label: string;
  overall_score: number | null;
  score_status: "available" | "insufficient_data" | "unavailable";
  evidence_coverage: number;
  analysis_confidence?: number | null;
  status: string;
  category_scores: CategoryScoreUI[];
}

export interface AnalysisSessionUI {
  id: string;
  meeting_id: string;
  status: "queued" | "processing" | "completed" | "insufficient_data" | "failed";
  requested_at: string;
  started_at?: string | null;
  completed_at?: string | null;
  error_code?: string | null;
  error_message_safe?: string | null;
  participants: ParticipantSummaryUI[];
}

export interface ParticipantDetailedAnalysisUI extends ParticipantSummaryUI {
  analysis_session_id: string;
  grammar_issues: GrammarIssueUI[];
  vocabulary_insights: VocabularyInsightUI[];
  fluency_metrics: FluencyMetricUI[];
  communication_insights: CommunicationInsightUI[];
  recommendations: RecommendationUI[];
}

