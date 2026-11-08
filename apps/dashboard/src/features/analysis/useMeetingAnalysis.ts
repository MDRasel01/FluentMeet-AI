"use client";

import { useState, useEffect, useCallback } from "react";
import {
  AnalysisSessionUI,
  ParticipantSummaryUI,
  ParticipantDetailedAnalysisUI,
} from "./types";

interface UseMeetingAnalysisProps {
  meetingId: string;
  apiBaseUrl?: string;
  authToken?: string;
}

export function useMeetingAnalysis({
  meetingId,
  apiBaseUrl = "http://localhost:8000",
  authToken,
}: UseMeetingAnalysisProps) {
  const [session, setSession] = useState<AnalysisSessionUI | null>(null);
  const [selectedParticipantId, setSelectedParticipantId] = useState<string | null>(null);
  const [participantDetail, setParticipantDetail] =
    useState<ParticipantDetailedAnalysisUI | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isTriggering, setIsTriggering] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const getHeaders = useCallback((): Record<string, string> => {
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (authToken) headers["Authorization"] = `Bearer ${authToken}`;
    return headers;
  }, [authToken]);

  // Fetch session
  const fetchSession = useCallback(async () => {
    if (!meetingId) return;
    setIsLoading(true);
    setError(null);
    try {
      // Trigger or retrieve meeting analysis
      const res = await fetch(`${apiBaseUrl}/api/v1/meetings/${meetingId}/analysis`, {
        method: "POST",
        headers: getHeaders(),
        body: JSON.stringify({ force_reanalyze: false }),
      });
      if (!res.ok) {
        throw new Error(`Failed to load analysis session (HTTP ${res.status})`);
      }
      const json = await res.json();
      if (json.data) {
        setSession(json.data);
        if (json.data.participants && json.data.participants.length > 0) {
          setSelectedParticipantId(json.data.participants[0].id);
        }
      }
    } catch (err: any) {
      console.error("Analysis load error:", err);
      setError(err.message || "Failed to load analysis");
    } finally {
      setIsLoading(false);
    }
  }, [meetingId, apiBaseUrl, getHeaders]);

  // Fetch participant detail when selected
  const fetchParticipantDetail = useCallback(
    async (sessionId: string, participantAnalysisId: string) => {
      try {
        const res = await fetch(
          `${apiBaseUrl}/api/v1/analysis/${sessionId}/participants/${participantAnalysisId}`,
          { headers: getHeaders() }
        );
        if (res.ok) {
          const json = await res.json();
          if (json.data) setParticipantDetail(json.data);
        }
      } catch (err) {
        console.error("Failed to load participant detailed analysis:", err);
      }
    },
    [apiBaseUrl, getHeaders]
  );

  useEffect(() => {
    fetchSession();
  }, [fetchSession]);

  useEffect(() => {
    if (session?.id && selectedParticipantId) {
      fetchParticipantDetail(session.id, selectedParticipantId);
    }
  }, [session?.id, selectedParticipantId, fetchParticipantDetail]);

  const triggerReanalyze = async () => {
    if (!meetingId) return;
    setIsTriggering(true);
    setError(null);
    try {
      const res = await fetch(`${apiBaseUrl}/api/v1/meetings/${meetingId}/analysis`, {
        method: "POST",
        headers: getHeaders(),
        body: JSON.stringify({ force_reanalyze: true }),
      });
      if (!res.ok) throw new Error("Re-analysis request failed");
      const json = await res.json();
      if (json.data) {
        setSession(json.data);
        if (json.data.participants?.length > 0) {
          setSelectedParticipantId(json.data.participants[0].id);
        }
      }
    } catch (err: any) {
      setError(err.message || "Failed to trigger re-analysis");
    } finally {
      setIsTriggering(false);
    }
  };

  return {
    session,
    selectedParticipantId,
    setSelectedParticipantId,
    participantDetail,
    isLoading,
    isTriggering,
    error,
    refreshAnalysis: fetchSession,
    triggerReanalyze,
  };
}

