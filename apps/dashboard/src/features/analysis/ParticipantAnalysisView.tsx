"use client";

import React, { useState } from "react";
import { useMeetingAnalysis } from "./useMeetingAnalysis";
import { AnalysisSummaryCard } from "./AnalysisSummaryCard";
import { CategoryScoresGrid } from "./CategoryScoresGrid";
import { GrammarCorrectionsList } from "./GrammarCorrectionsList";
import { VocabularyInsightsList } from "./VocabularyInsightsList";
import { FluencyMetricsCard } from "./FluencyMetricsCard";
import { RecommendationsList } from "./RecommendationsList";

interface ParticipantAnalysisViewProps {
  meetingId: string;
  apiBaseUrl?: string;
  authToken?: string;
}

export function ParticipantAnalysisView({
  meetingId,
  apiBaseUrl,
  authToken,
}: ParticipantAnalysisViewProps) {
  const {
    session,
    selectedParticipantId,
    setSelectedParticipantId,
    participantDetail,
    isLoading,
    isTriggering,
    error,
    triggerReanalyze,
  } = useMeetingAnalysis({ meetingId, apiBaseUrl, authToken });

  const [activeTab, setActiveTab] = useState<"overview" | "grammar" | "vocabulary" | "recommendations">("overview");

  if (isLoading && !session) {
    return (
      <div className="flex h-64 items-center justify-center rounded-xl border border-slate-800 bg-slate-900/40">
        <div className="flex flex-col items-center gap-2">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent" />
          <p className="text-xs text-slate-400">Loading English assessment...</p>
        </div>
      </div>
    );
  }

  if (error && !session) {
    return (
      <div className="rounded-xl border border-rose-900/40 bg-rose-950/20 p-6 text-center text-rose-300">
        <p className="font-semibold text-sm">Failed to load English analysis</p>
        <p className="mt-1 text-xs text-rose-400">{error}</p>
        <button
          onClick={triggerReanalyze}
          className="mt-4 rounded bg-rose-800 px-4 py-1.5 text-xs font-semibold text-white transition hover:bg-rose-700"
        >
          Try Again
        </button>
      </div>
    );
  }

  const activeParticipant =
    session?.participants.find((p) => p.id === selectedParticipantId) ||
    session?.participants[0] ||
    null;

  return (
    <div className="space-y-6">
      {/* Speaker Selector if multiple speakers */}
      {session && session.participants.length > 1 && (
        <div className="flex items-center gap-2 overflow-x-auto pb-1">
          <span className="text-xs font-semibold text-slate-400">Speaker:</span>
          {session.participants.map((p) => (
            <button
              key={p.id}
              onClick={() => setSelectedParticipantId(p.id)}
              className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition ${
                selectedParticipantId === p.id
                  ? "bg-indigo-600 text-white shadow-sm"
                  : "bg-slate-800/60 text-slate-400 hover:bg-slate-800 hover:text-slate-200"
              }`}
            >
              {p.speaker_label}
              {p.overall_score !== null && ` (${Math.round(p.overall_score)})`}
            </button>
          ))}
        </div>
      )}

      {/* Top Summary Card */}
      <AnalysisSummaryCard
        session={session}
        activeParticipant={activeParticipant}
        isTriggering={isTriggering}
        onReanalyze={triggerReanalyze}
      />

      {/* Category Scores Overview */}
      {activeParticipant && (
        <CategoryScoresGrid categories={activeParticipant.category_scores} />
      )}

      {/* Fluency Metrics Telemetry */}
      {participantDetail?.fluency_metrics && (
        <FluencyMetricsCard metrics={participantDetail.fluency_metrics} />
      )}

      {/* Tab Navigation */}
      <div className="border-b border-slate-800 flex gap-4">
        <button
          onClick={() => setActiveTab("overview")}
          className={`pb-2.5 text-xs font-semibold transition border-b-2 ${
            activeTab === "overview"
              ? "border-indigo-500 text-indigo-400"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          Recommendations ({participantDetail?.recommendations?.length || 0})
        </button>
        <button
          onClick={() => setActiveTab("grammar")}
          className={`pb-2.5 text-xs font-semibold transition border-b-2 ${
            activeTab === "grammar"
              ? "border-indigo-500 text-indigo-400"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          Grammar Findings ({participantDetail?.grammar_issues?.length || 0})
        </button>
        <button
          onClick={() => setActiveTab("vocabulary")}
          className={`pb-2.5 text-xs font-semibold transition border-b-2 ${
            activeTab === "vocabulary"
              ? "border-indigo-500 text-indigo-400"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          Vocabulary Insights ({participantDetail?.vocabulary_insights?.length || 0})
        </button>
      </div>

      {/* Tab Contents */}
      {activeTab === "overview" && (
        <RecommendationsList
          recommendations={participantDetail?.recommendations || []}
        />
      )}

      {activeTab === "grammar" && (
        <GrammarCorrectionsList
          issues={participantDetail?.grammar_issues || []}
        />
      )}

      {activeTab === "vocabulary" && (
        <VocabularyInsightsList
          insights={participantDetail?.vocabulary_insights || []}
        />
      )}
    </div>
  );
}

