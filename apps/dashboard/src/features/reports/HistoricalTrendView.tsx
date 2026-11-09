/**
 * FluentMeet AI - Step 10: Participant Historical Trend View
 */

import React from 'react';
import {
  TrendingUp,
  Award,
  Calendar,
  AlertTriangle,
  CheckCircle,
  Clock,
  Sparkles,
} from 'lucide-react';
import { HistoricalComparisonData } from './types';

interface HistoricalTrendViewProps {
  data: HistoricalComparisonData;
}

export const HistoricalTrendView: React.FC<HistoricalTrendViewProps> = ({ data }) => {
  const points = data.history_points || [];
  const trends = data.trends || { status: 'no_data', message: 'No trend data' };
  const mistakes = data.recurring_mistakes || [];
  const strengths = data.persistent_strengths || [];

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h2 className="text-xl font-bold text-white">
              Historical Growth Trajectory: {data.speaker_name || 'Participant'}
            </h2>
            <p className="text-sm text-slate-400 mt-1">
              Cross-meeting progress tracking across {data.total_meetings} analyzed meetings
            </p>
          </div>

          <div className="flex items-center gap-3">
            <span
              className={`px-3 py-1 rounded-full text-xs font-bold uppercase ${
                trends.trajectory === 'improving'
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                  : trends.trajectory === 'declining'
                  ? 'bg-red-500/10 text-red-400 border border-red-500/30'
                  : 'bg-slate-800 text-slate-300 border border-slate-700'
              }`}
            >
              Trajectory: {trends.trajectory || 'Steady'}
            </span>
            {trends.overall_delta !== undefined && trends.overall_delta !== null && (
              <span className="text-sm font-extrabold text-indigo-400">
                {trends.overall_delta >= 0 ? `+${trends.overall_delta}` : trends.overall_delta} pts
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Meeting Progress Timeline */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <h3 className="text-base font-semibold text-white mb-4">Meeting Performance Timeline</h3>
        {points.length > 0 ? (
          <div className="space-y-4">
            {points.map((pt, idx) => (
              <div
                key={idx}
                className="bg-slate-950/40 border border-slate-800 rounded-lg p-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-3"
              >
                <div>
                  <div className="text-sm font-semibold text-white">
                    Meeting: {pt.meeting_id.slice(0, 8)}
                  </div>
                  <div className="text-xs text-slate-400 flex items-center gap-2 mt-0.5">
                    <Calendar className="w-3.5 h-3.5" />
                    <span>{new Date(pt.meeting_date).toLocaleDateString()}</span>
                    <span>•</span>
                    <span>{pt.word_count} spoken words</span>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <div className="text-xs text-slate-400">Overall Score</div>
                    <div className="text-base font-bold text-indigo-400">
                      {pt.overall_score !== null ? `${pt.overall_score}/100` : '--'}
                    </div>
                  </div>

                  <div className="text-right">
                    <div className="text-xs text-slate-400">Grammar</div>
                    <div className="text-sm font-semibold text-emerald-400">
                      {pt.grammar_score !== null ? pt.grammar_score : '--'}
                    </div>
                  </div>

                  <div className="text-right">
                    <div className="text-xs text-slate-400">Pronunciation</div>
                    <div className="text-sm font-semibold text-amber-400">
                      {pt.pronunciation_score !== null ? pt.pronunciation_score : '--'}
                    </div>
                  </div>

                  <div className="text-right">
                    <div className="text-xs text-slate-400">IELTS Band</div>
                    <div className="text-sm font-bold text-sky-400">
                      {pt.ielts_overall_band !== null ? `Band ${pt.ielts_overall_band}` : '--'}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-500">No previous meeting records found.</p>
        )}
      </div>

      {/* Recurring Mistakes & Persistent Strengths */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Recurring Mistakes */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            <h3 className="text-base font-semibold text-white">Recurring Linguistic Patterns</h3>
          </div>
          {mistakes.length > 0 ? (
            <ul className="space-y-3">
              {mistakes.map((m, i) => (
                <li
                  key={i}
                  className="flex justify-between items-center bg-slate-950/40 p-3 rounded-lg border border-slate-800"
                >
                  <span className="text-sm font-medium text-slate-200">{m.rule_type}</span>
                  <span className="text-xs px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20 font-bold">
                    {m.frequency} occurrences
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-slate-500">No recurring mistake patterns detected across meetings.</p>
          )}
        </div>

        {/* Persistent Strengths */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle className="w-5 h-5 text-emerald-400" />
            <h3 className="text-base font-semibold text-white">Consistent Core Strengths</h3>
          </div>
          {strengths.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {strengths.map((s, i) => (
                <span
                  key={i}
                  className="px-3 py-1.5 rounded-lg bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 text-sm font-medium flex items-center gap-1.5"
                >
                  <Sparkles className="w-4 h-4 text-emerald-400" />
                  <span>{s} (Consistently ≥ 80%)</span>
                </span>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-500">More meeting data needed to establish persistent strengths.</p>
          )}
        </div>
      </div>
    </div>
  );
};

