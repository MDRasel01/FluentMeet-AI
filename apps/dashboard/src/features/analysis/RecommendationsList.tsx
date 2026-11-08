"use client";

import React from "react";
import { RecommendationUI } from "./types";

interface RecommendationsListProps {
  recommendations: RecommendationUI[];
}

export function RecommendationsList({ recommendations }: RecommendationsListProps) {
  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900/30 p-8 text-center text-slate-400">
        <span className="text-3xl">🌟</span>
        <p className="mt-2 text-sm font-medium text-slate-300">
          No critical areas for improvement flagged
        </p>
      </div>
    );
  }

  const getPriorityStyle = (priority: string) => {
    switch (priority) {
      case "high":
        return "bg-rose-500/10 text-rose-400 border-rose-500/30";
      case "medium":
        return "bg-amber-500/10 text-amber-400 border-amber-500/30";
      default:
        return "bg-blue-500/10 text-blue-400 border-blue-500/30";
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
          <span>🎯</span> Personalized Improvement Plan ({recommendations.length})
        </h3>
        <span className="text-xs text-slate-400">Ranked by Coaching Impact</span>
      </div>

      <div className="space-y-3">
        {recommendations.map((rec) => (
          <div
            key={rec.id}
            className="rounded-xl border border-slate-800 bg-slate-900/40 p-4 transition hover:border-slate-700"
          >
            <div className="flex items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <span
                  className={`rounded-full border px-2.5 py-0.5 text-xs font-bold uppercase tracking-wider ${getPriorityStyle(
                    rec.priority
                  )}`}
                >
                  {rec.priority} Priority
                </span>
                <span className="text-xs text-slate-400 capitalize font-medium">
                  {rec.skill_category}
                </span>
              </div>
            </div>

            <h4 className="mt-2 text-sm font-bold text-white">{rec.title}</h4>
            <p className="mt-1 text-xs text-slate-300 leading-relaxed">
              {rec.actionable_suggestion}
            </p>

            {rec.example && (
              <div className="mt-2 rounded bg-slate-800/60 p-2 text-xs text-slate-300 font-mono">
                {rec.example}
              </div>
            )}

            {rec.expected_outcome && (
              <p className="mt-2 text-[11px] text-emerald-400 flex items-center gap-1.5 font-medium">
                <span>✓</span> Expected Impact: {rec.expected_outcome}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
