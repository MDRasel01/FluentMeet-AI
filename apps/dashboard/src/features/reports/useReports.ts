/**
 * FluentMeet AI - Step 10: Reports Custom Hook
 */

import { useState, useEffect, useCallback } from 'react';
import {
  ReportSnapshot,
  MeetingSummaryPayload,
  ParticipantReportPayload,
  HistoricalComparisonData,
} from './types';

interface UseReportsOptions {
  meetingId?: string;
  participantId?: string;
  autoFetch?: boolean;
}

export function useReports({ meetingId, participantId, autoFetch = true }: UseReportsOptions = {}) {
  const [meetingSummary, setMeetingSummary] = useState<ReportSnapshot | null>(null);
  const [participantReports, setParticipantReports] = useState<ReportSnapshot[]>([]);
  const [activeParticipantReport, setActiveParticipantReport] = useState<ReportSnapshot | null>(null);
  const [historicalData, setHistoricalData] = useState<HistoricalComparisonData | null>(null);
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMeetingReports = useCallback(async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      // 1. Fetch meeting summary
      const sumRes = await fetch(`/api/v1/reports/meetings/${id}`);
      if (sumRes.ok) {
        const json = await sumRes.json();
        setMeetingSummary(json.data);
      }

      // 2. Fetch participant reports
      const partsRes = await fetch(`/api/v1/reports/meetings/${id}/participants`);
      if (partsRes.ok) {
        const json = await partsRes.json();
        setParticipantReports(json.data || []);
        if (json.data && json.data.length > 0 && !activeParticipantReport) {
          setActiveParticipantReport(json.data[0]);
        }
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to fetch meeting reports');
    } finally {
      setLoading(false);
    }
  }, [activeParticipantReport]);

  const generateReports = useCallback(async (id: string, force = false) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/v1/reports/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ meeting_id: id, force_regenerate: force }),
      });
      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson?.detail || 'Failed to generate report snapshots');
      }
      await fetchMeetingReports(id);
    } catch (err: any) {
      setError(err?.message || 'Failed to trigger report generation');
    } finally {
      setLoading(false);
    }
  }, [fetchMeetingReports]);

  const fetchParticipantHistory = useCallback(async (pId: string) => {
    try {
      const res = await fetch(`/api/v1/reports/participants/${pId}/history`);
      if (res.ok) {
        const json = await res.json();
        setHistoricalData(json.data);
      }
    } catch (err: any) {
      console.error('Failed to fetch participant history', err);
    }
  }, []);

  const exportReport = useCallback(async (reportId: string, format: 'csv' | 'html') => {
    setExporting(true);
    try {
      const res = await fetch(`/api/v1/reports/${reportId}/export/${format}`, {
        method: 'POST',
      });
      if (!res.ok) {
        throw new Error(`Failed to export ${format.toUpperCase()}`);
      }
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `fluentmeet-report-${reportId.slice(0, 8)}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      setError(err?.message || 'Export error');
    } finally {
      setExporting(false);
    }
  }, []);

  useEffect(() => {
    if (autoFetch && meetingId) {
      fetchMeetingReports(meetingId);
    }
  }, [meetingId, autoFetch, fetchMeetingReports]);

  useEffect(() => {
    if (participantId) {
      fetchParticipantHistory(participantId);
    }
  }, [participantId, fetchParticipantHistory]);

  return {
    meetingSummary,
    participantReports,
    activeParticipantReport,
    setActiveParticipantReport,
    historicalData,
    loading,
    exporting,
    error,
    generateReports,
    fetchMeetingReports,
    fetchParticipantHistory,
    exportReport,
  };
}

