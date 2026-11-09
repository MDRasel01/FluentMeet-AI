/**
 * FluentMeet AI - Step 10: Participant Report Detail View
 */

import React from 'react';
import {
  Award,
  BookOpen,
  Volume2,
  Activity,
  CheckCircle,
  AlertCircle,
  FileSpreadsheet,
  FileCode,
  ShieldAlert,
  ArrowRight,
  Sparkles,
} from 'lucide-react';
import { ReportSnapshot, ParticipantReportPayload } from './types';

interface ParticipantReportDetailProps {
  snapshot: ReportSnapshot;
  onBackToSummary?: () => void;
  onExportCsv?: () => void;
  onExportHtml?: () => void;
  isExporting?: boolean;
}

export const ParticipantReportDetail: React.FC<ParticipantReportDetailProps> = ({
  snapshot,
  onBackToSummary,
  onExportCsv,
  onExportHtml,
  isExporting = false,
}) => {
  const payload = (snapshot.report_payload || {}) as ParticipantReportPayload;
  const meta = payload.metadata || {
    speaker_label: snapshot.speaker_label || 'Speaker',
    display_name: snapshot.speaker_label || 'Participant',
  };
  const perf = payload.overall_performance || {
    overall_score: snapshot.overall_score,
    confidence_score: snapshot.confidence_score,
    status_label: 'Calibrated',
    is_calibrated: true,
    missing_components: [],
    validation_notes: [],
  };
  const metrics = payload.speaking_metrics || {
    total_words: snapshot.word_count,
    speaking_duration_seconds: snapshot.speaking_duration_seconds,
    words_per_minute: 0,
  };
  const grammar = payload.grammar_analysis || { score: null, issues_count: 0, issues: [] };
  const vocab = payload.vocabulary_analysis || { score: null, insights: { high_impact_words: [], repetitive_words: [] } };
  const fluency = payload.fluency_analysis || { score: null, metrics: { words_per_minute: 0, filler_word_count: 0, pause_count: 0, speech_rate_category: 'moderate' } };
  const pron = payload.pronunciation_analysis || { score: null, mispronounced_words: [], prosody: {} };
  const ielts = payload.ielts_estimate;
  const recommendations = payload.recommendations || [];

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          {onBackToSummary && (
            <button
              onClick={onBackToSummary}
              className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold mb-2 flex items-center gap-1 transition"
            >
              ← Back to Meeting Summary
            </button>
          )}
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-white">{meta.display_name}</h1>
            <span className="text-sm px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
              {meta.speaker_label}
            </span>
            <span
              className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                perf.is_calibrated
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                  : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
              }`}
            >
              {perf.status_label}
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            {metrics.total_words} words spoken • {metrics.speaking_duration_seconds}s active speaking • {metrics.words_per_minute} WPM
          </p>
        </div>

        {/* Export Buttons */}
        <div className="flex items-center gap-2">
          {onExportCsv && (
            <button
              onClick={onExportCsv}
              disabled={isExporting}
              className="flex items-center gap-2 px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium rounded-lg border border-slate-700 transition"
              title="Export CSV"
            >
              <FileSpreadsheet className="w-4 h-4 text-emerald-400" />
              <span>CSV</span>
            </button>
          )}
          {onExportHtml && (
            <button
              onClick={onExportHtml}
              disabled={isExporting}
              className="flex items-center gap-2 px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg transition shadow-sm"
              title="Print / HTML"
            >
              <FileCode className="w-4 h-4" />
              <span>Print / HTML</span>
            </button>
          )}
        </div>
      </div>

      {/* 4 Pillars Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Overall Score */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <div className="flex justify-between items-center">
            <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold">Overall English</span>
            <Award className="w-5 h-5 text-indigo-400" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white">
              {perf.overall_score !== null ? perf.overall_score : '--'}
            </span>
            <span className="text-xs text-slate-400">/ 100</span>
          </div>
          <div className="mt-2 text-xs text-slate-400">
            Confidence: {perf.confidence_score ? `${Math.round(perf.confidence_score * 100)}%` : '--'}
          </div>
        </div>

        {/* Grammar Score */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <div className="flex justify-between items-center">
            <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold">Grammar Accuracy</span>
            <BookOpen className="w-5 h-5 text-emerald-400" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white">
              {grammar.score !== null ? grammar.score : '--'}
            </span>
            <span className="text-xs text-slate-400">/ 100</span>
          </div>
          <div className="mt-2 text-xs text-slate-400">
            {grammar.issues_count} grammatical corrections
          </div>
        </div>

        {/* Vocabulary Score */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <div className="flex justify-between items-center">
            <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold">Vocabulary Range</span>
            <Sparkles className="w-5 h-5 text-sky-400" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white">
              {vocab.score !== null ? vocab.score : '--'}
            </span>
            <span className="text-xs text-slate-400">/ 100</span>
          </div>
          <div className="mt-2 text-xs text-slate-400">
            {vocab.insights?.high_impact_words?.length || 0} high-impact expressions
          </div>
        </div>

        {/* Pronunciation Score */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <div className="flex justify-between items-center">
            <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold">Pronunciation</span>
            <Volume2 className="w-5 h-5 text-amber-400" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white">
              {pron.score !== null ? pron.score : '--'}
            </span>
            <span className="text-xs text-slate-400">/ 100</span>
          </div>
          <div className="mt-2 text-xs text-slate-400">
            {pron.mispronounced_words.length} mispronounced words
          </div>
        </div>
      </div>

      {/* IELTS Practice Card with Mandatory Educational Disclaimer */}
      {ielts && (
        <div className="bg-gradient-to-r from-indigo-950/40 via-slate-900 to-slate-900 border border-indigo-500/20 rounded-xl p-6">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 rounded text-xs font-bold uppercase bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  IELTS Practice Estimate
                </span>
                <span className="text-xs text-slate-400">CEFR: <strong className="text-white">{ielts.cefr_level || 'B2'}</strong></span>
              </div>
              <div className="mt-2 text-2xl font-extrabold text-white">
                Band {ielts.overall_band_estimate} <span className="text-sm font-normal text-slate-400">Overall Estimate</span>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
              <div className="bg-slate-950/40 px-3 py-2 rounded-lg border border-slate-800">
                <div className="text-xs text-slate-400">Fluency</div>
                <div className="font-bold text-white text-base">Band {ielts.fluency_coherence_band || '--'}</div>
              </div>
              <div className="bg-slate-950/40 px-3 py-2 rounded-lg border border-slate-800">
                <div className="text-xs text-slate-400">Lexical</div>
                <div className="font-bold text-white text-base">Band {ielts.lexical_resource_band || '--'}</div>
              </div>
              <div className="bg-slate-950/40 px-3 py-2 rounded-lg border border-slate-800">
                <div className="text-xs text-slate-400">Grammar</div>
                <div className="font-bold text-white text-base">Band {ielts.grammatical_range_band || '--'}</div>
              </div>
              <div className="bg-slate-950/40 px-3 py-2 rounded-lg border border-slate-800">
                <div className="text-xs text-slate-400">Pronunciation</div>
                <div className="font-bold text-white text-base">Band {ielts.pronunciation_band || '--'}</div>
              </div>
            </div>
          </div>

          {ielts.band_descriptor_summary && (
            <p className="text-sm text-slate-300 italic mb-3">
              "{ielts.band_descriptor_summary}"
            </p>
          )}

          {/* Mandatory Educational Disclaimer */}
          <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg text-xs text-amber-300/90 flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 flex-shrink-0" />
            <span>
              <strong>Educational Practice Disclaimer:</strong> {ielts.disclaimer}
            </span>
          </div>
        </div>
      )}

      {/* Grammar Corrections Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-800">
          <h3 className="text-base font-semibold text-white">Grammar & Syntax Accuracy Analysis</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-950/60 text-slate-400 border-b border-slate-800 text-xs uppercase tracking-wider">
              <tr>
                <th className="py-3 px-6">Rule Type</th>
                <th className="py-3 px-6">Spoken Phrase</th>
                <th className="py-3 px-6">Suggested Correction</th>
                <th className="py-3 px-6">Linguistic Explanation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {grammar.issues && grammar.issues.length > 0 ? (
                grammar.issues.map((g, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/40">
                    <td className="py-3.5 px-6">
                      <span className="px-2 py-0.5 rounded text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                        {g.rule_type}
                      </span>
                    </td>
                    <td className="py-3.5 px-6 text-red-400 font-medium line-through">
                      {g.offending_text}
                    </td>
                    <td className="py-3.5 px-6 text-emerald-400 font-semibold">
                      {g.corrected_text}
                    </td>
                    <td className="py-3.5 px-6 text-slate-300 text-xs">
                      {g.explanation}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="py-6 text-center text-slate-500">
                    No grammar corrections detected for this speaker.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pronunciation Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-800">
          <h3 className="text-base font-semibold text-white">Acoustic Pronunciation & Phoneme Evaluation</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-950/60 text-slate-400 border-b border-slate-800 text-xs uppercase tracking-wider">
              <tr>
                <th className="py-3 px-6">Evaluated Word</th>
                <th className="py-3 px-6">Accuracy</th>
                <th className="py-3 px-6">Expected Phonemes (IPA)</th>
                <th className="py-3 px-6">Produced Acoustic Form</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {pron.mispronounced_words && pron.mispronounced_words.length > 0 ? (
                pron.mispronounced_words.map((w, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/40">
                    <td className="py-3.5 px-6 font-semibold text-white">
                      {w.word}
                    </td>
                    <td className="py-3.5 px-6">
                      <span className="font-bold text-amber-400">{Math.round(w.accuracy_score)}%</span>
                    </td>
                    <td className="py-3.5 px-6 text-slate-300 font-mono text-xs">
                      {w.phonemes_expected}
                    </td>
                    <td className="py-3.5 px-6 text-red-400 font-mono text-xs">
                      {w.phonemes_produced}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="py-6 text-center text-slate-500">
                    All evaluated spoken words aligned with standard pronunciation models.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recommendations & Actionable Drills */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-semibold text-white">Personalized English Improvement Drills</h3>
        </div>

        {recommendations.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recommendations.map((r, idx) => (
              <div
                key={idx}
                className="bg-slate-950/50 border border-slate-800 rounded-lg p-4 flex flex-col justify-between"
              >
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="px-2 py-0.5 rounded text-xs font-semibold bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                      {r.category}
                    </span>
                    <span className="text-xs uppercase font-bold text-slate-400">{r.priority} Priority</span>
                  </div>
                  <p className="text-sm text-slate-200">{r.recommendation_text}</p>
                  {r.practice_text && (
                    <div className="mt-2 p-2.5 bg-slate-900 border border-slate-700/60 rounded text-xs text-sky-300 font-mono">
                      <strong>Practice Drill:</strong> "{r.practice_text}"
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-500">No corrective drills suggested for this meeting.</p>
        )}
      </div>
    </div>
  );
};
