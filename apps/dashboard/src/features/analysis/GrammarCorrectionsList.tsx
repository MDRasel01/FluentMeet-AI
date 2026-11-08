"use client";

import React from "react";
import { GrammarIssueUI } from "./types";

interface GrammarCorrectionsListProps {
  issues: GrammarIssueUI[];
}

export function GrammarCorrectionsList({ issues }: GrammarCorrectionsListProps) {
  if (!issues || issues.length === 0) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900/30 p-8 text-center text-slate-400">
        <span className="text-3xl">✨</span>
        <p className="mt-2 text-sm font-medium text-slate-300">
          No grammatical inaccuracies detected
        </p>
        <p className="text-xs text-slate-500">
          Spoken English was structurally sound across all analyzed turns.
        </p>
      </div>
    );
  }

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case "major":
        return "bg-rose-500/10 text-rose-400 border-rose-500/20";
      case "moderate":
        return "bg-amber-500/10 text-amber-400 border-amber-500/20";
      default:
        return "bg-slate-700/30 text-slate-300 border-slate-700";
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
          <span>📘</span> Grammatical Observations ({issues.length})
        </h3>
        <span className="text-xs text-slate-400">Zero-Fabrication Verified</span>
      </div>

      <div className="divide-y divide-slate-800 rounded-xl border border-slate-800 bg-slate-900/40">
        {issues.map((issue) => (
          <div key={issue.id} className="p-4 transition hover:bg-slate-800/30">
            <div className="flex items-center justify-between gap-2">
              <span className="text-xs font-semibold text-indigo-400 font-mono">
                {issue.rule_name || issue.category.replace("_", " ").toUpperCase()}
              </span>
              <span
                className={`rounded-full border px-2.5 py-0.5 text-xs font-medium capitalize ${getSeverityBadge(
                  issue.severity
                )}`}
              >
                {issue.severity}
              </span>
            </div>

            <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
              <div className="rounded-lg bg-rose-950/20 border border-rose-900/30 p-2.5 text-rose-200">
                <span className="text-xs font-semibold uppercase text-rose-400 block mb-1">
                  Spoken Evidence:
                </span>
                <span className="font-mono text-xs">"{issue.original_text}"</span>
              </div>
              <div className="rounded-lg bg-emerald-950/20 border border-emerald-900/30 p-2.5 text-emerald-200">
                <span className="text-xs font-semibold uppercase text-emerald-400 block mb-1">
                  Corrected Standard:
                </span>
                <span className="font-mono text-xs font-semibold">
                  "{issue.corrected_text}"
                </span>
              </div>
            </div>

            <p className="mt-2 text-xs text-slate-300 leading-relaxed">
              <span className="font-semibold text-slate-400">Explanation: </span>
              {issue.explanation}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

