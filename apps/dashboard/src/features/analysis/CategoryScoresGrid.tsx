"use client";

import React from "react";
import { CategoryScoreUI } from "./types";

interface CategoryScoresGridProps {
  categories: CategoryScoreUI[];
}

const CATEGORY_META: Record<
  string,
  { label: string; weight: string; icon: string; description: string }
> = {
  grammar: {
    label: "Grammar & Accuracy",
    weight: "25%",
    icon: "📘",
    description: "Tense consistency, subject-verb agreement, and prepositions.",
  },
  vocabulary: {
    label: "Vocabulary Precision",
    weight: "20%",
    icon: "💎",
    description: "Lexical diversity, executive collocations, and word choice.",
  },
  fluency: {
    label: "Fluency & Speech Pace",
    weight: "20%",
    icon: "⚡",
    description: "WPM speech rate, filler minimization, and deliberate pausing.",
  },
  sentence_structure: {
    label: "Sentence Structure",
    weight: "10%",
    icon: "🏗️",
    description: "Clause coordination, variety, and run-on sentence control.",
  },
  communication: {
    label: "Communication & Relevance",
    weight: "15%",
    icon: "🤝",
    description: "Active listening indicators, conversational diplomacy, clarity.",
  },
  contextual_language: {
    label: "Contextual Register",
    weight: "10%",
    icon: "🎯",
    description: "Alignment with meeting domain and professional formality.",
  },
};

export function CategoryScoresGrid({ categories }: CategoryScoresGridProps) {
  if (!categories || categories.length === 0) return null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {categories.map((cat) => {
        const meta = CATEGORY_META[cat.category] || {
          label: cat.category.replace("_", " "),
          weight: "",
          icon: "📊",
          description: "Linguistic evaluation category",
        };

        const scoreVal = cat.score !== null ? Math.round(cat.score) : null;

        return (
          <div
            key={cat.category}
            className="flex flex-col justify-between rounded-xl border border-slate-800 bg-slate-900/40 p-5 shadow transition hover:border-slate-700"
          >
            <div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-xl">{meta.icon}</span>
                  <h3 className="font-semibold text-slate-100">{meta.label}</h3>
                </div>
                <span className="rounded bg-slate-800 px-2 py-0.5 text-xs text-slate-400 font-mono">
                  {meta.weight}
                </span>
              </div>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">
                {meta.description}
              </p>
            </div>

            <div className="mt-4">
              <div className="flex items-baseline justify-between mb-1.5">
                <span className="text-2xl font-bold text-white">
                  {scoreVal !== null ? scoreVal : "--"}
                  <span className="text-xs text-slate-500 font-normal">/100</span>
                </span>
                <span className="text-xs text-slate-400">
                  {cat.status === "insufficient_data"
                    ? "Insufficient speech"
                    : `${cat.evidence_count} evidence items`}
                </span>
              </div>

              {/* Progress bar */}
              <div className="h-2 w-full overflow-hidden rounded-full bg-slate-800">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    scoreVal === null
                      ? "bg-slate-700"
                      : scoreVal >= 80
                      ? "bg-emerald-500"
                      : scoreVal >= 65
                      ? "bg-blue-500"
                      : "bg-amber-500"
                  }`}
                  style={{ width: `${scoreVal || 0}%` }}
                />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

