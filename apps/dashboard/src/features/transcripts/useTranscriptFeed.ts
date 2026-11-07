"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { TranscriptSegmentUI, MeetingSpeakerUI, SpeechOverlapUI } from "./types";

interface UseTranscriptFeedProps {
  meetingId: string;
  apiBaseUrl?: string;
  wsBaseUrl?: string;
  authToken?: string;
}

export function useTranscriptFeed({
  meetingId,
  apiBaseUrl = "http://localhost:8000",
  wsBaseUrl = "ws://localhost:8000",
  authToken,
}: UseTranscriptFeedProps) {
  const [segments, setSegments] = useState<TranscriptSegmentUI[]>([]);
  const [speakers, setSpeakers] = useState<MeetingSpeakerUI[]>([]);
  const [overlaps, setOverlaps] = useState<SpeechOverlapUI[]>([]);
  const [partialText, setPartialText] = useState<{ speakerLabel: string; text: string } | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  // Fetch initial transcripts, speakers, and overlaps from REST API
  const fetchInitialData = useCallback(async () => {
    try {
      const headers: Record<string, string> = { "Content-Type": "application/json" };
      if (authToken) headers["Authorization"] = `Bearer ${authToken}`;

      const [transcriptsRes, speakersRes, overlapsRes] = await Promise.all([
        fetch(`${apiBaseUrl}/api/v1/meetings/${meetingId}/transcripts`, { headers }),
        fetch(`${apiBaseUrl}/api/v1/meetings/${meetingId}/speakers`, { headers }),
        fetch(`${apiBaseUrl}/api/v1/meetings/${meetingId}/overlaps`, { headers }),
      ]);

      if (transcriptsRes.ok) {
        const data = await transcriptsRes.json();
        if (data.data) setSegments(data.data);
      }
      if (speakersRes.ok) {
        const data = await speakersRes.json();
        if (data.data) setSpeakers(data.data);
      }
      if (overlapsRes.ok) {
        const data = await overlapsRes.json();
        if (data.data) setOverlaps(data.data);
      }
    } catch (err) {
      console.error("Failed to fetch initial transcript data:", err);
    }
  }, [meetingId, apiBaseUrl, authToken]);

  useEffect(() => {
    fetchInitialData();
  }, [fetchInitialData]);

  // WebSocket real-time subscription
  useEffect(() => {
    if (!meetingId) return;

    const wsUrl = `${wsBaseUrl}/ws/meetings/${meetingId}/transcripts${authToken ? `?token=${authToken}` : ""}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      // Send handshake
      ws.send(JSON.stringify({ type: "subscribe_transcripts", meetingId }));
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        const eventType = msg.type;
        const payload = msg.payload || msg;

        switch (eventType) {
          case "transcript.partial":
            setPartialText({
              speakerLabel: payload.speaker_label || "speaker_user_me",
              text: payload.text || "",
            });
            break;

          case "transcript.final":
            setPartialText(null);
            setSegments((prev) => {
              // Avoid duplicates
              if (prev.some((s) => s.id === payload.id)) {
                return prev.map((s) => (s.id === payload.id ? { ...s, ...payload } : s));
              }
              return [...prev, payload];
            });
            break;

          case "transcript.corrected":
            setSegments((prev) =>
              prev.map((s) =>
                s.id === payload.segment_id
                  ? {
                      ...s,
                      text: payload.text,
                      speaker_id: payload.speaker_id,
                      status: "corrected",
                      revision_number: payload.revision_number,
                    }
                  : s
              )
            );
            break;

          case "speaker.detected":
            setSpeakers((prev) => {
              if (prev.some((spk) => spk.id === payload.speaker_id)) return prev;
              return [
                ...prev,
                {
                  id: payload.speaker_id,
                  meeting_id: payload.meeting_id,
                  speaker_label: payload.speaker_label,
                  display_name: payload.display_name,
                  is_identified: false,
                  source_id: payload.source_id,
                },
              ];
            });
            break;

          case "speaker.updated":
            setSpeakers((prev) =>
              prev.map((spk) =>
                spk.id === payload.speaker_id
                  ? {
                      ...spk,
                      display_name: payload.display_name,
                      is_identified: payload.is_identified,
                    }
                  : spk
              )
            );
            break;

          case "speaker.overlap":
            setOverlaps((prev) => [...prev, payload]);
            break;

          default:
            break;
        }
      } catch (err) {
        console.error("Error processing transcript WS message:", err);
      }
    };

    ws.onclose = () => setIsConnected(false);
    ws.onerror = (err) => console.error("Transcript WebSocket error:", err);

    return () => {
      ws.close();
    };
  }, [meetingId, wsBaseUrl, authToken]);

  return {
    segments,
    speakers,
    overlaps,
    partialText,
    isConnected,
    refetch: fetchInitialData,
  };
}
