"use client";

import React from "react";
import { VocabularyInsightUI } from "./types";

interface VocabularyInsightsListProps {
  insights: VocabularyInsightUI[];
}

export function VocabularyInsightsList({ insights }: VocabularyInsightsListProps) {
  if (!insights || insights.length === 0) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900/30 p-8 text-center text-slate-400">
        <span className="text-3xl">💎</span>
        <p className="mt-2 text-sm font-medium text-slate-300">
          Vocabulary is naturally aligned with the meeting context
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
          <span>💎</span> Vocabulary & Executive Collocations ({insights.length})
        </h3>
        <span className="text-xs text-slate-400">Context-Tailored</span>
      </div>

      <div className="divide-y divide-slate-800 rounded-xl border border-slate-800 bg-slate-900/40">
        {insights.map((item) => (
          <div key={item.id} className="p-4 transition hover:bg-slate-800/30">
            <div className="flex items-center gap-2 mb-2">
              <span className="rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-2 py-0.5 text-xs font-semibold capitalize">
                {item.insight_type.replace("_", " ")}
              </span>
              {item.context_note && (
                <span className="text-xs text-slate-500">{item.context_note}</span>
              )}
            </div>

            <div className="flex flex-col sm:flex-row sm:items-center gap-2 text-sm">
              <div className="flex-1 rounded-lg bg-slate-800/50 p-2.5 text-slate-300">
                <span className="text-xs font-semibold uppercase text-slate-400 block mb-0.5">
                  Spoken:
                </span>
                <span className="font-mono text-xs text-rose-300">
                  "{item.original_expression}"
                </span>
              </div>
              <span className="text-slate-500 hidden sm:inline">➔</span>
              <div className="flex-1 rounded-lg bg-emerald-950/20 border border-emerald-900/30 p-2.5 text-emerald-200">
                <span className="text-xs font-semibold uppercase text-emerald-400 block mb-0.5">
                  Elevated Phrasing:
                </span>
                <span className="font-mono text-xs font-bold text-emerald-300">
                  "{item.suggested_expression}"
                </span>
              </div>
            </div>

            <p className="mt-2 text-xs text-slate-300 leading-relaxed">
              {item.explanation}
            </p>

            {item.example_sentence && (
              <p className="mt-1 text-xs text-slate-400 italic">
                Example: "{item.example_sentence}"
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
