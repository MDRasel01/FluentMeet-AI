"use client";

import React, { useState } from "react";
import { TranscriptSegmentUI, MeetingSpeakerUI } from "./types";
import { X, Check, Edit2 } from "lucide-react";

interface TranscriptSegmentEditModalProps {
  segment: TranscriptSegmentUI | null;
  isOpen: boolean;
  onClose: () => void;
  speakers: MeetingSpeakerUI[];
  meetingId: string;
  apiBaseUrl?: string;
  authToken?: string;
  onSegmentSaved?: () => void;
}

export function TranscriptSegmentEditModal({
  segment,
  isOpen,
  onClose,
  speakers,
  meetingId,
  apiBaseUrl = "http://localhost:8000",
  authToken,
  onSegmentSaved,
}: TranscriptSegmentEditModalProps) {
  const [editedText, setEditedText] = useState(segment?.text || "");
  const [selectedSpeakerId, setSelectedSpeakerId] = useState(segment?.speaker_id || "");
  const [loading, setLoading] = useState(false);

  // Sync state on segment change
  React.useEffect(() => {
    if (segment) {
      setEditedText(segment.text);
      setSelectedSpeakerId(segment.speaker_id || "");
    }
  }, [segment]);

  if (!isOpen || !segment) return null;

  const handleSave = async () => {
    setLoading(true);
    try {
      const headers: Record<string, string> = { "Content-Type": "application/json" };
      if (authToken) headers["Authorization"] = `Bearer ${authToken}`;

      const res = await fetch(`${apiBaseUrl}/api/v1/meetings/${meetingId}/transcripts/${segment.id}`, {
        method: "PATCH",
        headers,
        body: JSON.stringify({
          text: editedText.trim(),
          speaker_id: selectedSpeakerId || undefined,
        }),
      });

      if (res.ok) {
        if (onSegmentSaved) onSegmentSaved();
        onClose();
      }
    } catch (err) {
      console.error("Failed to correct transcript segment:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
          <div className="flex items-center space-x-2">
            <Edit2 className="w-5 h-5 text-indigo-400" />
            <h3 className="text-base font-semibold text-slate-100">Correct Transcript Segment</h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-200">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
              Speaker Attribution
            </label>
            <select
              value={selectedSpeakerId}
              onChange={(e) => setSelectedSpeakerId(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 text-slate-200 text-sm rounded-lg px-3 py-2 focus:border-indigo-500 focus:outline-none"
            >
              <option value="">Keep current ({segment.speaker_name || segment.speaker_label})</option>
              {speakers.map((spk) => (
                <option key={spk.id} value={spk.id}>
                  {spk.display_name || spk.speaker_label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
              Spoken Text
            </label>
            <textarea
              rows={4}
              value={editedText}
              onChange={(e) => setEditedText(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 text-slate-100 text-sm rounded-lg p-3 focus:border-indigo-500 focus:outline-none"
            />
          </div>
        </div>

        <div className="px-6 py-4 bg-slate-950/40 border-t border-slate-800 flex justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-slate-400 hover:text-white transition"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={loading}
            className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition"
          >
            <Check className="w-4 h-4" />
            <span>Save Correction</span>
          </button>
        </div>
      </div>
    </div>
  );
}
