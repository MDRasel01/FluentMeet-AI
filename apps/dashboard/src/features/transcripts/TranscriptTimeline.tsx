"use client";

import React, { useState, useRef, useEffect } from "react";
import { TranscriptSegmentUI, MeetingSpeakerUI, SpeechOverlapUI } from "./types";
import { MessageSquare, Users, AlertTriangle, Edit3, Volume2 } from "lucide-react";

interface TranscriptTimelineProps {
  segments: TranscriptSegmentUI[];
  speakers: MeetingSpeakerUI[];
  overlaps: SpeechOverlapUI[];
  partialText?: { speakerLabel: string; text: string } | null;
  onEditSegment?: (segment: TranscriptSegmentUI) => void;
  onManageSpeakers?: () => void;
}

export function TranscriptTimeline({
  segments,
  speakers,
  overlaps,
  partialText,
  onEditSegment,
  onManageSpeakers,
}: TranscriptTimelineProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = useState(true);

  // Auto-scroll on new segments
  useEffect(() => {
    if (autoScroll && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [segments, partialText, autoScroll]);

  const handleScroll = () => {
    if (!scrollRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;
    setAutoScroll(isAtBottom);
  };

  const formatTimestamp = (ms: number): string => {
    const totalSeconds = Math.floor(ms / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
  };

  const getSpeakerDisplayName = (speakerId?: string | null, speakerLabel?: string | null): string => {
    if (!speakerId && !speakerLabel) return "Unknown Speaker";
    const found = speakers.find((s) => s.id === speakerId || s.speaker_label === speakerLabel);
    if (found?.display_name) return found.display_name;
    if (speakerLabel === "speaker_user_me") return "You (Host)";
    return speakerLabel ? speakerLabel.replace("_", " ").toUpperCase() : "Speaker";
  };

  return (
    <div className="flex flex-col h-full bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-2xl">
      {/* Header bar */}
      <div className="flex items-center justify-between px-6 py-4 bg-slate-950/70 border-b border-slate-800 backdrop-blur-md">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-indigo-500/10 text-indigo-400 rounded-lg">
            <MessageSquare className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-semibold text-slate-100">Live Meeting Transcript</h2>
            <p className="text-xs text-slate-400">
              {segments.length} verified turns • {speakers.length} speakers
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {overlaps.length > 0 && (
            <div className="flex items-center space-x-1.5 px-3 py-1 rounded-full bg-amber-500/10 text-amber-400 text-xs font-medium border border-amber-500/20">
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>{overlaps.length} Overlaps</span>
            </div>
          )}
          <button
            onClick={onManageSpeakers}
            className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition"
          >
            <Users className="w-3.5 h-3.5 text-indigo-400" />
            <span>Manage Speakers</span>
          </button>
        </div>
      </div>

      {/* Main transcript scroll area */}
      <div
        ref={scrollRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-slate-800"
      >
        {segments.length === 0 && !partialText ? (
          <div className="flex flex-col items-center justify-center h-64 text-center text-slate-500">
            <Volume2 className="w-10 h-10 mb-3 opacity-40 animate-pulse" />
            <p className="text-sm font-medium">Listening for speech...</p>
            <p className="text-xs text-slate-600 mt-1">Transcripts will appear in real time once speech is detected.</p>
          </div>
        ) : (
          segments.map((segment) => {
            const isLocalUser = segment.source_id === 0 || segment.speaker_label === "speaker_user_me";
            const speakerName = getSpeakerDisplayName(segment.speaker_id, segment.speaker_label);

            return (
              <div
                key={segment.id}
                className={`flex flex-col group p-4 rounded-xl transition duration-200 ${
                  isLocalUser
                    ? "bg-indigo-950/20 border border-indigo-900/30 hover:border-indigo-800/50"
                    : "bg-slate-800/40 border border-slate-800 hover:border-slate-700"
                }`}
              >
                {/* Speaker meta row */}
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2.5">
                    <div
                      className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold uppercase ${
                        isLocalUser ? "bg-indigo-600 text-white" : "bg-emerald-600 text-white"
                      }`}
                    >
                      {speakerName.slice(0, 2)}
                    </div>
                    <span className="text-sm font-semibold text-slate-200">{speakerName}</span>
                    <span className="text-xs text-slate-500">
                      {formatTimestamp(segment.start_time_ms)} - {formatTimestamp(segment.end_time_ms)}
                    </span>
                    {segment.status === "corrected" && (
                      <span className="text-[10px] font-medium px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                        Edited (v{segment.revision_number})
                      </span>
                    )}
                  </div>

                  {onEditSegment && (
                    <button
                      onClick={() => onEditSegment(segment)}
                      className="opacity-0 group-hover:opacity-100 text-slate-400 hover:text-slate-200 p-1 rounded hover:bg-slate-700/50 transition"
                      title="Edit transcript"
                    >
                      <Edit3 className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>

                {/* Words & Text */}
                <p className="text-sm text-slate-300 leading-relaxed pl-9">
                  {segment.words && segment.words.length > 0 ? (
                    segment.words.map((w, idx) => {
                      const isLowConfidence = w.confidence_score !== null && w.confidence_score !== undefined && w.confidence_score < 0.65;
                      return (
                        <span
                          key={idx}
                          title={isLowConfidence ? `Low confidence: ${Math.round((w.confidence_score || 0) * 100)}%` : undefined}
                          className={`mr-1 inline-block transition-colors ${
                            isLowConfidence
                              ? "border-b border-dotted border-amber-500 text-amber-200/90"
                              : "hover:text-indigo-300"
                          }`}
                        >
                          {w.word}
                        </span>
                      );
                    })
                  ) : (
                    segment.text
                  )}
                </p>
              </div>
            );
          })
        )}

        {/* Live streaming partial preview */}
        {partialText && (
          <div className="flex flex-col p-4 rounded-xl bg-slate-800/20 border border-indigo-500/30 border-dashed animate-pulse">
            <div className="flex items-center space-x-2 mb-2">
              <span className="w-2 h-2 rounded-full bg-indigo-500 animate-ping" />
              <span className="text-xs font-semibold text-indigo-400">
                {getSpeakerDisplayName(null, partialText.speakerLabel)} (Speaking...)
              </span>
            </div>
            <p className="text-sm text-slate-400 pl-4 italic">{partialText.text}</p>
          </div>
        )}
      </div>
    </div>
  );
}
