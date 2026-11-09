/**
 * FluentMeet AI - Step 10: Meeting Report Summary View
 */

import React from 'react';
import {
  Award,
  Clock,
  MessageSquare,
  Users,
  TrendingUp,
  Download,
  AlertTriangle,
  CheckCircle2,
  FileSpreadsheet,
  FileCode,
} from 'lucide-react';
import { ReportSnapshot, MeetingSummaryPayload } from './types';

interface ReportSummaryViewProps {
  snapshot: ReportSnapshot;
  onSelectParticipant?: (speakerLabel: string) => void;
  onExportCsv?: () => void;
  onExportHtml?: () => void;
  isExporting?: boolean;
}

export const ReportSummaryView: React.FC<ReportSummaryViewProps> = ({
  snapshot,
  onSelectParticipant,
  onExportCsv,
  onExportHtml,
  isExporting = false,
}) => {
  const payload = (snapshot.report_payload || {}) as MeetingSummaryPayload;
  const meta = payload.metadata || { title: `Meeting ${snapshot.meeting_id.slice(0, 8)}` };
  const metrics = payload.summary_metrics || {
    participant_count: 0,
    total_duration_seconds: 0,
    total_words: 0,
    average_overall_score: null,
    calibrated_participants_count: 0,
  };
  const participants = payload.participants || [];
  const highlights = payload.highlights || [];
  const growthAreas = payload.areas_for_team_growth || [];

  return (
    <div className="space-y-6">
      {/* Top Header Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-white">{meta.title}</h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              Meeting Intelligence Summary
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Meeting ID: <code className="text-slate-300">{snapshot.meeting_id}</code> | Rubric Version: {snapshot.scoring_rubric_version}
          </p>
        </div>

        {/* Export Actions */}
        <div className="flex items-center gap-2">
          {onExportCsv && (
            <button
              onClick={onExportCsv}
              disabled={isExporting}
              className="flex items-center gap-2 px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium rounded-lg border border-slate-700 transition"
              title="Download CSV for Excel or Google Sheets"
            >
              <FileSpreadsheet className="w-4 h-4 text-emerald-400" />
              <span>Export CSV</span>
            </button>
          )}
          {onExportHtml && (
            <button
              onClick={onExportHtml}
              disabled={isExporting}
              className="flex items-center gap-2 px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg shadow-sm transition"
              title="View & Print Standalone HTML Report"
            >
              <FileCode className="w-4 h-4" />
              <span>Print / HTML</span>
            </button>
          )}
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold">Average English Score</span>
            <Award className="w-5 h-5 text-indigo-400" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white">
              {metrics.average_overall_score !== null ? metrics.average_overall_score : '--'}
            </span>
            <span className="text-xs text-slate-400">/ 100</span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            {metrics.calibrated_participants_count} of {metrics.participant_count} speakers calibrated
          </p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold">Speakers Analyzed</span>
            <Users className="w-5 h-5 text-sky-400" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white">{metrics.participant_count}</span>
            <span className="text-xs text-slate-400">participants</span>
          </div>
          <p className="text-xs text-slate-500 mt-1">Multi-speaker diarized streams</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold">Speaking Duration</span>
            <Clock className="w-5 h-5 text-amber-400" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white">{metrics.total_duration_seconds}s</span>
          </div>
          <p className="text-xs text-slate-500 mt-1">Actual vocal speech elapsed</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold">Words Captured</span>
            <MessageSquare className="w-5 h-5 text-emerald-400" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white">{metrics.total_words}</span>
            <span className="text-xs text-slate-400">words</span>
          </div>
          <p className="text-xs text-slate-500 mt-1">Finalized transcription count</p>
        </div>
      </div>

      {/* Highlights & Growth Areas */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            <h3 className="text-base font-semibold text-white">Meeting Highlights</h3>
          </div>
          {highlights.length > 0 ? (
            <ul className="space-y-2 text-sm text-slate-300">
              {highlights.map((h, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-emerald-400 font-bold">•</span>
                  <span>{h}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-slate-500">No meeting highlights recorded.</p>
          )}
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            <h3 className="text-base font-semibold text-white">Areas for Team Development</h3>
          </div>
          {growthAreas.length > 0 ? (
            <ul className="space-y-2 text-sm text-slate-300">
              {growthAreas.map((g, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-amber-400 font-bold">•</span>
                  <span>{g}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-slate-500">No collective areas for growth identified.</p>
          )}
        </div>
      </div>

      {/* Participants Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-800 flex justify-between items-center">
          <h3 className="text-base font-semibold text-white">Participant Performance Breakdown</h3>
          <span className="text-xs text-slate-400">Click a participant to view in-depth report</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-950/60 text-slate-400 border-b border-slate-800 text-xs uppercase tracking-wider">
              <tr>
                <th className="py-3 px-6">Speaker</th>
                <th className="py-3 px-6">Overall Score</th>
                <th className="py-3 px-6">Status</th>
                <th className="py-3 px-6">Talk Time</th>
                <th className="py-3 px-6">Spoken Words</th>
                <th className="py-3 px-6">IELTS Practice Band</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {participants.map((p, idx) => (
                <tr
                  key={idx}
                  onClick={() => onSelectParticipant && onSelectParticipant(p.speaker_label)}
                  className="hover:bg-slate-800/50 cursor-pointer transition"
                >
                  <td className="py-4 px-6">
                    <div className="font-medium text-white">{p.display_name}</div>
                    <div className="text-xs text-slate-400">{p.speaker_label}</div>
                  </td>
                  <td className="py-4 px-6">
                    {p.overall_score !== null ? (
                      <span className="font-bold text-base text-indigo-400">{p.overall_score}/100</span>
                    ) : (
                      <span className="text-slate-500 italic">--</span>
                    )}
                  </td>
                  <td className="py-4 px-6">
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                        p.status_label === 'Calibrated'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      }`}
                    >
                      {p.status_label}
                    </span>
                  </td>
                  <td className="py-4 px-6">
                    <div className="text-slate-300 font-medium">{p.talk_time_percentage}%</div>
                    <div className="text-xs text-slate-500">{p.duration_seconds}s</div>
                  </td>
                  <td className="py-4 px-6 text-slate-300 font-medium">{p.word_count} words</td>
                  <td className="py-4 px-6">
                    {p.ielts_band !== null && p.ielts_band !== undefined ? (
                      <span className="font-semibold text-sky-400">Band {p.ielts_band}</span>
                    ) : (
                      <span className="text-slate-500 italic">N/A</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

