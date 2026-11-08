"use client";

import React from "react";
import { AnalysisSessionUI, ParticipantSummaryUI } from "./types";

interface AnalysisSummaryCardProps {
  session: AnalysisSessionUI | null;
  activeParticipant: ParticipantSummaryUI | null;
  isTriggering: boolean;
  onReanalyze: () => void;
}

export function AnalysisSummaryCard({
  session,
  activeParticipant,
  isTriggering,
  onReanalyze,
}: AnalysisSummaryCardProps) {
  if (!session) return null;

  const score = activeParticipant?.overall_score;
  const status = activeParticipant?.score_status || session.status;

  const getScoreColor = (val: number | null) => {
    if (val === null) return "text-slate-400 border-slate-700 bg-slate-800/40";
    if (val >= 85) return "text-emerald-400 border-emerald-500/30 bg-emerald-500/10";
    if (val >= 70) return "text-blue-400 border-blue-500/30 bg-blue-500/10";
    if (val >= 55) return "text-amber-400 border-amber-500/30 bg-amber-500/10";
    return "text-rose-400 border-rose-500/30 bg-rose-500/10";
  };

  const getRatingLabel = (val: number | null) => {
    if (val === null) return "Insufficient Speech Data";
    if (val >= 90) return "Executive / Fluent Master";
    if (val >= 80) return "Professional / Advanced";
    if (val >= 65) return "Intermediate Communicator";
    return "Developing Foundations";
  };

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 shadow-xl backdrop-blur-md">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="inline-block h-2 w-2 rounded-full bg-indigo-500 animate-pulse" />
            <h2 className="text-xl font-bold text-white tracking-wide">
              AI English Communication Assessment
            </h2>
          </div>
          <p className="mt-1 text-sm text-slate-400">
            Participant:{" "}
            <span className="font-semibold text-slate-200">
              {activeParticipant?.speaker_label || "All Speakers"}
            </span>{" "}
            | Status:{" "}
            <span className="capitalize text-slate-300">
              {status.replace("_", " ")}
            </span>
          </p>
        </div>

        <div className="flex items-center gap-4">
          <div
            className={`flex flex-col items-center justify-center rounded-2xl border px-6 py-2 ${getScoreColor(
              score ?? null
            )}`}
          >
            <span className="text-3xl font-extrabold tracking-tight">
              {score !== null && score !== undefined ? Math.round(score) : "--"}
              <span className="text-sm font-medium text-slate-400">/100</span>
            </span>
            <span className="text-xs font-semibold uppercase tracking-wider">
              {getRatingLabel(score ?? null)}
            </span>
          </div>

          <button
            onClick={onReanalyze}
            disabled={isTriggering}
            className="rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-md transition hover:bg-indigo-500 disabled:opacity-50"
          >
            {isTriggering ? "Re-Analyzing..." : "Re-Analyze"}
          </button>
        </div>
      </div>
    </div>
  );
}
