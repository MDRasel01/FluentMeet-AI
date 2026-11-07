"use client";

import React, { useState } from "react";
import { MeetingSpeakerUI } from "./types";
import { X, Check, User } from "lucide-react";

interface SpeakerManagerModalProps {
  isOpen: boolean;
  onClose: () => void;
  speakers: MeetingSpeakerUI[];
  meetingId: string;
  apiBaseUrl?: string;
  authToken?: string;
  onSpeakerUpdated?: () => void;
}

export function SpeakerManagerModal({
  isOpen,
  onClose,
  speakers,
  meetingId,
  apiBaseUrl = "http://localhost:8000",
  authToken,
  onSpeakerUpdated,
}: SpeakerManagerModalProps) {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [nameValue, setNameValue] = useState("");
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleStartEdit = (speaker: MeetingSpeakerUI) => {
    setEditingId(speaker.id);
    setNameValue(speaker.display_name || speaker.speaker_label);
  };

  const handleSave = async (speakerId: string) => {
    if (!nameValue.trim()) return;
    setLoading(true);
    try {
      const headers: Record<string, string> = { "Content-Type": "application/json" };
      if (authToken) headers["Authorization"] = `Bearer ${authToken}`;

      const res = await fetch(`${apiBaseUrl}/api/v1/meetings/${meetingId}/speakers/${speakerId}`, {
        method: "PATCH",
        headers,
        body: JSON.stringify({ display_name: nameValue.trim() }),
      });

      if (res.ok) {
        setEditingId(null);
        if (onSpeakerUpdated) onSpeakerUpdated();
      }
    } catch (err) {
      console.error("Failed to update speaker name:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
          <div className="flex items-center space-x-2">
            <User className="w-5 h-5 text-indigo-400" />
            <h3 className="text-base font-semibold text-slate-100">Meeting Participants & Speakers</h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-200">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-4 max-h-96 overflow-y-auto">
          {speakers.map((spk) => (
            <div
              key={spk.id}
              className="flex items-center justify-between p-3 rounded-xl bg-slate-800/50 border border-slate-800"
            >
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 rounded-full bg-indigo-600/30 text-indigo-400 border border-indigo-500/20 flex items-center justify-center font-bold text-xs uppercase">
                  {(spk.display_name || spk.speaker_label).slice(0, 2)}
                </div>
                <div>
                  {editingId === spk.id ? (
                    <input
                      type="text"
                      value={nameValue}
                      onChange={(e) => setNameValue(e.target.value)}
                      className="bg-slate-950 border border-indigo-500 text-slate-100 text-sm px-2.5 py-1 rounded-md focus:outline-none"
                      autoFocus
                    />
                  ) : (
                    <div>
                      <p className="text-sm font-semibold text-slate-200">
                        {spk.display_name || spk.speaker_label}
                      </p>
                      <p className="text-xs text-slate-500">{spk.speaker_label}</p>
                    </div>
                  )}
                </div>
              </div>

              <div>
                {editingId === spk.id ? (
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleSave(spk.id)}
                      disabled={loading}
                      className="p-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white transition"
                    >
                      <Check className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => setEditingId(null)}
                      className="p-1.5 rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-300 transition"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => handleStartEdit(spk)}
                    className="text-xs text-indigo-400 hover:text-indigo-300 font-medium px-3 py-1 rounded bg-indigo-500/10 hover:bg-indigo-500/20 transition"
                  >
                    Rename
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="px-6 py-4 bg-slate-950/40 border-t border-slate-800 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-slate-300 hover:text-white rounded-lg bg-slate-800 hover:bg-slate-700 transition"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}

