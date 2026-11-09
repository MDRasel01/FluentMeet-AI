/**
 * FluentMeet AI - Isolated Demo Datasets Provider
 * Centralized, read-only repository of mock demonstration data.
 * STRICT ARCHITECTURAL RULE: This dataset is only accessible when a tab is explicitly set to DEMO mode.
 * Real mode must NEVER fall back to this data.
 */

import {
  DEMO_MEETINGS,
  DEMO_TRANSCRIPT_SEGMENTS,
  DEMO_MISTAKES,
  DEMO_VOCABULARY_SUGGESTIONS,
  DEMO_TEAM_ANALYTICS,
  DEMO_ADMIN_DATA,
  DemoMeeting,
} from '../../../demoData';
import {
  ReportSnapshot,
  HistoricalComparisonData,
} from '../features/reports';

export {
  DEMO_MEETINGS,
  DEMO_TRANSCRIPT_SEGMENTS,
  DEMO_MISTAKES,
  DEMO_VOCABULARY_SUGGESTIONS,
  DEMO_TEAM_ANALYTICS,
  DEMO_ADMIN_DATA,
};
export type { DemoMeeting };

export const DEMO_MEETING_SUMMARY_SNAPSHOT: ReportSnapshot = {
  id: 'rep-snap-sum-001',
  meeting_id: 'm-101',
  report_type: 'meeting_summary',
  report_version: 1,
  report_status: 'completed',
  overall_score: 83.5,
  confidence_score: 0.94,
  word_count: 1840,
  speaking_duration_seconds: 620.0,
  source_analysis_version: '1.0',
  scoring_rubric_version: '1.0',
  generated_at: '2026-11-09T08:00:00Z',
  created_at: '2026-11-09T08:00:00Z',
  report_payload: {
    metadata: {
      meeting_id: 'm-101',
      title: 'Q3 Enterprise Architecture & Strategy Review',
      report_type: 'meeting_summary',
      scoring_rubric_version: '1.0',
    },
    summary_metrics: {
      participant_count: 3,
      total_duration_seconds: 620.0,
      total_words: 1840,
      average_overall_score: 83.5,
      calibrated_participants_count: 3,
    },
    participants: [
      {
        speaker_label: 'speaker_priya',
        display_name: 'Priya Sharma (Host)',
        overall_score: 85.0,
        status_label: 'Calibrated',
        word_count: 820,
        duration_seconds: 252.0,
        talk_time_percentage: 40.6,
        ielts_band: 7.5,
      },
      {
        speaker_label: 'speaker_alex',
        display_name: 'Alex Chen',
        overall_score: 82.0,
        status_label: 'Calibrated',
        word_count: 610,
        duration_seconds: 210.0,
        talk_time_percentage: 33.9,
        ielts_band: 7.0,
      },
      {
        speaker_label: 'speaker_marcus',
        display_name: 'Marcus Vance',
        overall_score: 83.5,
        status_label: 'Calibrated',
        word_count: 410,
        duration_seconds: 158.0,
        talk_time_percentage: 25.5,
        ielts_band: 7.5,
      },
    ],
    highlights: [
      'High conversational engagement across all 3 participants (Average: 83.5/100).',
      'Strong technical vocabulary and precise architectural expressions observed.',
    ],
    areas_for_team_growth: [
      'Preposition and tense agreement refinement recommended during status transitions.',
    ],
    disclaimers: {
      summary: 'Meeting summary is aggregated strictly from validated participant spoken contributions.',
      ielts: 'Educational practice estimate only. This is not an official IELTS score, certified assessment, or substitute for an IELTS examiner.',
    },
  },
};

export const DEMO_PARTICIPANT_SNAPSHOT: ReportSnapshot = {
  id: 'rep-snap-part-001',
  meeting_id: 'm-101',
  report_type: 'individual_participant',
  participant_id: 'part-priya-01',
  speaker_label: 'speaker_priya',
  report_version: 1,
  report_status: 'completed',
  overall_score: 85.0,
  confidence_score: 0.94,
  word_count: 820,
  speaking_duration_seconds: 252.0,
  source_analysis_version: '1.0',
  scoring_rubric_version: '1.0',
  generated_at: '2026-11-09T08:00:00Z',
  created_at: '2026-11-09T08:00:00Z',
  report_payload: {
    metadata: {
      meeting_id: 'm-101',
      participant_id: 'part-priya-01',
      speaker_label: 'speaker_priya',
      display_name: 'Priya Sharma',
      scoring_rubric_version: '1.0',
      report_type: 'individual_participant',
    },
    overall_performance: {
      overall_score: 85.0,
      confidence_score: 0.94,
      status_label: 'Calibrated',
      report_status: 'completed',
      is_calibrated: true,
      missing_components: [],
      validation_notes: ['All four assessment pillars validated and calibrated.'],
    },
    speaking_metrics: {
      total_words: 820,
      speaking_duration_seconds: 252.0,
      words_per_minute: 142.0,
    },
    grammar_analysis: {
      score: 84.0,
      issues_count: 2,
      issues: [
        {
          rule_type: 'preposition_usage',
          offending_text: 'discuss about the timeline',
          corrected_text: 'discuss the timeline',
          explanation: '"Discuss" is a transitive verb; omit the unnecessary preposition "about".',
          severity: 'minor',
        },
        {
          rule_type: 'conditional_tense',
          offending_text: 'If we will deploy early, we see bugs',
          corrected_text: 'If we deploy early, we will see bugs',
          explanation: 'In first conditional clauses, use present simple in the "if" clause.',
          severity: 'moderate',
        },
      ],
    },
    vocabulary_analysis: {
      score: 86.0,
      insights: {
        lexical_diversity: 0.72,
        high_impact_words: ['bottleneck', 'resilience', 'milestone', 'scalable'],
        repetitive_words: ['basically', 'actually'],
      },
    },
    fluency_analysis: {
      score: 82.0,
      metrics: {
        words_per_minute: 142.0,
        filler_word_count: 8,
        pause_count: 5,
        speech_rate_category: 'moderate',
      },
    },
    pronunciation_analysis: {
      score: 88.0,
      confidence: 0.92,
      mispronounced_words: [
        {
          word: 'architecture',
          accuracy_score: 72.0,
          phonemes_expected: 'ɑː k ɪ t ɛ k tʃ ə',
          phonemes_produced: 'ɑː tʃ ɪ t ɛ k tʃ ə',
        },
      ],
      prosody: {
        speaking_rate_wpm: 142.0,
        pitch_range_hz: 95.0,
        sentence_stress_accuracy: 88.0,
        intonation_naturalness: 86.0,
      },
    },
    ielts_estimate: {
      overall_band_estimate: 7.5,
      fluency_coherence_band: 7.5,
      lexical_resource_band: 8.0,
      grammatical_range_band: 7.5,
      pronunciation_band: 7.5,
      cefr_level: 'C1',
      band_descriptor_summary: 'Effective operational command of the language with occasional inaccuracies and minor mother-tongue influence.',
      disclaimer: 'Educational practice estimate only. This is not an official IELTS score, certified assessment, or substitute for an IELTS examiner.',
    },
    recommendations: [
      {
        source: 'grammar',
        category: 'Grammar: Prepositions',
        priority: 'medium',
        recommendation_text: 'Eliminate redundant prepositions after transitive verbs like discuss, consider, mention.',
        practice_text: 'Let us discuss the quarterly deployment roadmap directly with the stakeholders.',
      },
      {
        source: 'pronunciation',
        category: 'Pronunciation: Minimal Pairs',
        priority: 'high',
        recommendation_text: 'Velar plosive /k/ precision in words of Greek origin (architecture, technique).',
        practice_text: 'The architecture team presented an archetype of the new cloud infrastructure.',
      },
    ],
    disclaimers: {
      ielts: 'Educational practice estimate only. This is not an official IELTS score, certified assessment, or substitute for an IELTS examiner.',
      scoring: 'Scores reflect spoken English communication patterns observed during this recording.',
    },
  },
};

export const DEMO_HISTORICAL_DATA: HistoricalComparisonData = {
  participant_id: 'part-priya-01',
  speaker_name: 'Priya Sharma',
  total_meetings: 3,
  history_points: [
    {
      meeting_id: 'm-098',
      meeting_date: '2026-10-24T10:00:00Z',
      report_id: 'rep-098',
      overall_score: 78.0,
      grammar_score: 76.0,
      vocabulary_score: 80.0,
      fluency_score: 76.0,
      pronunciation_score: 80.0,
      ielts_overall_band: 7.0,
      word_count: 650,
    },
    {
      meeting_id: 'm-099',
      meeting_date: '2026-10-31T14:30:00Z',
      report_id: 'rep-099',
      overall_score: 81.5,
      grammar_score: 80.0,
      vocabulary_score: 84.0,
      fluency_score: 79.0,
      pronunciation_score: 83.0,
      ielts_overall_band: 7.0,
      word_count: 720,
    },
    {
      meeting_id: 'm-101',
      meeting_date: '2026-11-08T09:15:00Z',
      report_id: 'rep-101',
      overall_score: 85.0,
      grammar_score: 84.0,
      vocabulary_score: 86.0,
      fluency_score: 82.0,
      pronunciation_score: 88.0,
      ielts_overall_band: 7.5,
      word_count: 820,
    },
  ],
  trends: {
    status: 'active',
    trajectory: 'improving',
    overall_delta: 7.0,
    message: 'Consistent upward trajectory across 3 meetings (+7.0 pts)',
  },
  recurring_mistakes: [
    { rule_type: 'Preposition after transitive verb (discuss about)', frequency: 2 },
    { rule_type: 'First conditional clause structure', frequency: 2 },
  ],
  persistent_strengths: [
    'Vocabulary Range & Professional Collocations',
    'Acoustic Clarity & Intelligibility',
    'Conversational Pace Stability',
  ],
};
