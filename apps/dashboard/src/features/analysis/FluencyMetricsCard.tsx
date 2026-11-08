"use client";

import React from "react";
import { FluencyMetricUI } from "./types";

interface FluencyMetricsCardProps {
  metrics: FluencyMetricUI[];
}

const METRIC_LABELS: Record<string, { label: string; ideal: string; icon: string }> = {
  speech_rate_wpm: {
    label: "Speech Rate",
    ideal: "125 - 165 WPM",
    icon: "⏱️",
  },
  filler_word_rate: {
    label: "Filler Words",
    ideal: "< 3.0 / min",
    icon: "🫧",
  },
  repetition_rate: {
    label: "Hesitation Repeats",
    ideal: "< 1.0%",
    icon: "🔁",
  },
  avg_utterance_length_words: {
    label: "Average Turn Length",
    ideal: "15 - 35 words",
    icon: "💬",
  },
  pause_frequency: {
    label: "Inter-Turn Pauses",
    ideal: "Deliberate gaps",
    icon: "⏸️",
  },
};

export function FluencyMetricsCard({ metrics }: FluencyMetricsCardProps) {
  if (!metrics || metrics.length === 0) return null;

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-5 shadow">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
          <span>⚡</span> Spoken English Fluency Telemetry
        </h3>
        <span className="text-xs text-slate-400">Step 07 Millisecond Timestamps</span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
        {metrics.map((m) => {
          const info = METRIC_LABELS[m.metric_name] || {
            label: m.metric_name.replace("_", " "),
            ideal: "--",
            icon: "📈",
          };

          return (
            <div
              key={m.metric_name}
              className="rounded-lg border border-slate-800 bg-slate-800/40 p-3.5 flex flex-col justify-between"
            >
              <div>
                <span className="text-lg">{info.icon}</span>
                <p className="mt-1 text-xs font-medium text-slate-400">{info.label}</p>
              </div>
              <div className="mt-3">
                <span className="text-xl font-bold text-white">
                  {m.metric_value}
                  <span className="text-xs font-normal text-slate-400 ml-1">
                    {m.unit}
                  </span>
                </span>
                <span className="block mt-0.5 text-[10px] text-slate-500 font-mono">
                  Target: {info.ideal}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
