// src/features/founder/useUserManagement.ts
// Data layer for the Founder Workbench: Dual Mode (REAL vs DEMO), KPIs,
// keyset-paginated audit log, live feed, session heartbeat, and owner actions.
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import type { SupabaseClient } from '@supabase/supabase-js';
import { isLiveSupabaseConfigured } from '../../lib/supabase';

export type TabDataMode = 'REAL' | 'DEMO';

export type AuditEventType =
  | 'LOGIN_SUCCESS'
  | 'LOGIN_FAILED'
  | 'LOGOUT'
  | 'SESSION_REVOKED'
  | 'PASSWORD_CHANGED'
  | 'ACCOUNT_LOCKED'
  | 'ACCOUNT_UNLOCKED'
  | 'ROLE_CHANGED'
  | 'STATUS_CHANGED';

export interface AuditRow {
  id: string;
  created_at: string;
  user_id: string | null;
  email: string | null;
  event_type: AuditEventType;
  ip_address: string | null;
  country_code: string | null;
  user_agent: string | null;
  metadata: Record<string, unknown>;
}

export interface Kpis {
  total_users: number;
  new_signups_today: number;
  dau: number;
  returning_users: number;
  peak_concurrent: number;
  active_now: number;
  failed_24h: number;
  rollup_updated_at: string | null;
}

export interface AuditFilters {
  eventTypes: AuditEventType[];
  search: string;          // email prefix
  from: string | null;     // ISO
  to: string | null;       // ISO (exclusive)
  userId: string | null;
}

export const EMPTY_FILTERS: AuditFilters = { eventTypes: [], search: '', from: null, to: null, userId: null };

const PAGE_SIZE = 50;
const KPI_REFRESH_MS = 30_000;
const HEARTBEAT_MS = 60_000;

// High-fidelity fallback demo data for local review and offline testing
const FALLBACK_KPIS: Kpis = {
  total_users: 1428,
  new_signups_today: 43,
  dau: 386,
  returning_users: 343,
  peak_concurrent: 112,
  active_now: 28,
  failed_24h: 3,
  rollup_updated_at: new Date().toISOString(),
};

const REAL_EMPTY_KPIS: Kpis = {
  total_users: 0,
  new_signups_today: 0,
  dau: 0,
  returning_users: 0,
  peak_concurrent: 0,
  active_now: 0,
  failed_24h: 0,
  rollup_updated_at: null,
};

export const SAMPLE_AUDIT_LOGS: AuditRow[] = [
  {
    id: 'aud-1',
    created_at: new Date(Date.now() - 1000 * 60 * 2).toISOString(),
    user_id: 'usr-1',
    email: 'russell7@gmail.com',
    event_type: 'LOGIN_SUCCESS',
    ip_address: '103.145.74.0/24',
    country_code: 'BD',
    user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0.0.0',
    metadata: { session_id: 'ses-101', device: { os: 'Windows', browser: 'Chrome', device: 'desktop' } },
  },
  {
    id: 'aud-2',
    created_at: new Date(Date.now() - 1000 * 60 * 12).toISOString(),
    user_id: 'usr-2',
    email: 'priya.sharma@acmecorp.com',
    event_type: 'LOGIN_SUCCESS',
    ip_address: '49.205.122.0/24',
    country_code: 'IN',
    user_agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1.15',
    metadata: { session_id: 'ses-102', device: { os: 'macOS', browser: 'Safari', device: 'desktop' } },
  },
  {
    id: 'aud-3',
    created_at: new Date(Date.now() - 1000 * 60 * 25).toISOString(),
    user_id: null,
    email: 'unknown_attacker@darkweb.io',
    event_type: 'LOGIN_FAILED',
    ip_address: '185.220.101.0/24',
    country_code: 'NL',
    user_agent: 'python-requests/2.31.0',
    metadata: { reason: 'invalid_credentials' },
  },
  {
    id: 'aud-4',
    created_at: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
    user_id: 'usr-3',
    email: 'marcus.vance@techcorp.io',
    event_type: 'PASSWORD_CHANGED',
    ip_address: '172.56.21.0/24',
    country_code: 'US',
    user_agent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) Mobile/15E148',
    metadata: { mfa_enabled: true },
  },
  {
    id: 'aud-5',
    created_at: new Date(Date.now() - 1000 * 60 * 70).toISOString(),
    user_id: 'usr-4',
    email: 'elena.rostova@berlin-design.de',
    event_type: 'LOGOUT',
    ip_address: '88.130.49.0/24',
    country_code: 'DE',
    user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
    metadata: { reason: 'user_initiated', session_duration_sec: 2450 },
  },
  {
    id: 'aud-6',
    created_at: new Date(Date.now() - 1000 * 60 * 120).toISOString(),
    user_id: 'usr-5',
    email: 'liam.kane@london-agency.co.uk',
    event_type: 'ROLE_CHANGED',
    ip_address: '81.187.24.0/24',
    country_code: 'GB',
    user_agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) Chrome/124.0.0.0',
    metadata: { old_role: 'member', new_role: 'admin', actor: 'russell7@gmail.com' },
  },
];

/** Friendly message only; raw error is logged, never shown to user */
const friendly = (e: unknown) => {
  console.error('[founder]', e);
  return 'Something went wrong. Please try again.';
};

// ---------------------------------------------------------------------------
// Heartbeat: mount once in the authenticated app shell (for ALL users).
// Returns false from server => session was revoked => sign out locally.
// ---------------------------------------------------------------------------
export function useSessionHeartbeat(supabase: SupabaseClient, gatewayUrl = '/api/auth-gateway') {
  useEffect(() => {
    let stopped = false;
    const beat = async () => {
      if (stopped || document.visibilityState === 'hidden') return;
      if (!isLiveSupabaseConfigured) return;
      try {
        const { data, error } = await supabase.rpc('session_heartbeat');
        if (!error && data === false) await supabase.auth.signOut();
      } catch (err) {
        console.warn('Heartbeat check bypassed:', err);
      }
    };

    void beat();
    const id = window.setInterval(beat, HEARTBEAT_MS);
    const onVisible = () => { if (document.visibilityState === 'visible') void beat(); };
    document.addEventListener('visibilitychange', onVisible);

    const onPageHide = async () => {
      if (!isLiveSupabaseConfigured) return;
      try {
        const { data } = await supabase.auth.getSession();
        const token = data.session?.access_token;
        if (token && navigator.sendBeacon) {
          navigator.sendBeacon(
            `${gatewayUrl}/beacon-end`,
            new Blob([JSON.stringify({ access_token: token })], { type: 'application/json' }),
          );
        }
      } catch {
        // best effort only
      }
    };
    window.addEventListener('pagehide', onPageHide);
    return () => {
      stopped = true;
      window.clearInterval(id);
      document.removeEventListener('visibilitychange', onVisible);
      window.removeEventListener('pagehide', onPageHide);
    };
  }, [supabase, gatewayUrl]);
}

// ---------------------------------------------------------------------------
// Main hook: Supports both REAL VERSION and DEMO VERSION
// ---------------------------------------------------------------------------
export function useUserManagement(
  supabase: SupabaseClient,
  mode: TabDataMode = 'DEMO'
) {
  const [demoRows, setDemoRows] = useState<AuditRow[]>(SAMPLE_AUDIT_LOGS);
  const [kpis, setKpis] = useState<Kpis | null>(mode === 'DEMO' ? FALLBACK_KPIS : REAL_EMPTY_KPIS);
  const [rows, setRows] = useState<AuditRow[]>(mode === 'DEMO' ? SAMPLE_AUDIT_LOGS : []);
  const [hasMore, setHasMore] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFiltersState] = useState<AuditFilters>(EMPTY_FILTERS);
  const [liveCount, setLiveCount] = useState(0);

  const cursor = useRef<{ ts: string; id: string } | null>(null);
  const reqSeq = useRef(0);
  const filtersRef = useRef(filters);
  filtersRef.current = filters;

  const fetchPage = useCallback(async (reset: boolean) => {
    const seq = ++reqSeq.current;
    const f = filtersRef.current;
    setLoading(true);
    setError(null);

    if (mode === 'DEMO') {
      // High-fidelity client-side filtering for interactive demo mode
      setTimeout(() => {
        let filtered = [...demoRows];
        if (f.search) {
          filtered = filtered.filter((r) => (r.email || '').toLowerCase().includes(f.search.toLowerCase()));
        }
        if (f.eventTypes.length > 0) {
          filtered = filtered.filter((r) => f.eventTypes.includes(r.event_type));
        }
        if (f.userId) {
          filtered = filtered.filter((r) => r.user_id === f.userId);
        }
        setRows(filtered);
        setHasMore(false);
        setLoading(false);
      }, 100);
      return;
    }

    // REAL PRODUCTION MODE
    if (!isLiveSupabaseConfigured) {
      setRows([]);
      setHasMore(false);
      setLoading(false);
      return;
    }

    const c = reset ? null : cursor.current;
    try {
      const { data, error: err } = await supabase.rpc('owner_list_audit_logs', {
        p_limit: PAGE_SIZE + 1,
        p_cursor_ts: c?.ts ?? null,
        p_cursor_id: c?.id ?? null,
        p_event_types: f.eventTypes.length ? f.eventTypes : null,
        p_user_id: f.userId,
        p_from: f.from,
        p_to: f.to,
        p_search: f.search.trim() || null,
      });

      if (seq !== reqSeq.current) return;
      if (err) {
        console.warn('owner_list_audit_logs RPC error in REAL mode:', err);
        setError(`Live Supabase Query Notice: ${err.message || 'Run migration 20261115_001_founder_user_management.sql'}`);
        setRows([]);
        setLoading(false);
        return;
      }

      const page = (data ?? []) as AuditRow[];
      const more = page.length > PAGE_SIZE;
      const visible = more ? page.slice(0, PAGE_SIZE) : page;
      const last = visible[visible.length - 1];
      cursor.current = last ? { ts: last.created_at, id: last.id } : c;
      setHasMore(more);
      setRows((prev) => (reset ? visible : [...prev, ...visible]));
      if (reset) setLiveCount(0);
    } catch (e) {
      console.warn('RPC invocation failed:', e);
      setError('Failed to reach Supabase database. Verify network or database configuration.');
      setRows([]);
    } finally {
      setLoading(false);
    }
  }, [mode, demoRows, supabase]);

  const refreshKpis = useCallback(async () => {
    if (mode === 'DEMO') {
      setKpis(FALLBACK_KPIS);
      return;
    }

    // REAL MODE
    if (!isLiveSupabaseConfigured) {
      setKpis(REAL_EMPTY_KPIS);
      return;
    }

    try {
      const { data, error: err } = await supabase.rpc('owner_kpis');
      if (err) {
        console.warn('owner_kpis RPC notice:', err);
        setKpis(REAL_EMPTY_KPIS);
        return;
      }
      setKpis(data as Kpis);
    } catch {
      setKpis(REAL_EMPTY_KPIS);
    }
  }, [mode, supabase]);

  // Initial load + filter changes + mode changes
  useEffect(() => {
    cursor.current = null;
    const t = window.setTimeout(() => {
      void fetchPage(true);
      void refreshKpis();
    }, 150);
    return () => window.clearTimeout(t);
  }, [mode, filters, fetchPage, refreshKpis]);

  // KPI polling
  useEffect(() => {
    const id = window.setInterval(() => {
      if (document.visibilityState === 'visible') void refreshKpis();
    }, KPI_REFRESH_MS);
    return () => window.clearInterval(id);
  }, [refreshKpis]);

  // Live feed: Realtime INSERTs in REAL mode
  useEffect(() => {
    if (mode !== 'REAL' || !isLiveSupabaseConfigured) return;

    let pending = 0;
    let flush: number | undefined;
    const channel = supabase
      .channel('founder-audit-feed')
      .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'auth_audit_logs' }, () => {
        pending += 1;
        flush ??= window.setTimeout(() => {
          setLiveCount((n) => n + pending);
          pending = 0;
          flush = undefined;
          void refreshKpis();
        }, 1500);
      })
      .subscribe();

    return () => {
      if (flush) window.clearTimeout(flush);
      void supabase.removeChannel(channel);
    };
  }, [mode, supabase, refreshKpis]);

  const setFilters = useCallback((patch: Partial<AuditFilters>) =>
    setFiltersState((prev) => ({ ...prev, ...patch })), []);
  const loadMore = useCallback(() => { if (hasMore && !loading) void fetchPage(false); }, [hasMore, loading, fetchPage]);
  const reload = useCallback(() => {
    cursor.current = null;
    void fetchPage(true);
    void refreshKpis();
  }, [fetchPage, refreshKpis]);

  // Owner actions
  const act = useCallback(async (fn: string, args: Record<string, unknown>) => {
    if (mode === 'DEMO') {
      // Simulate real owner actions in demo mode
      console.log(`[Demo Action] Simulated ${fn} with args:`, args);
      if (fn === 'owner_revoke_user_sessions') {
        const uid = args.p_user_id as string;
        setDemoRows((prev) =>
          prev.map((r) =>
            r.user_id === uid ? { ...r, event_type: 'SESSION_REVOKED' as AuditEventType } : r
          )
        );
      }
      reload();
      return { ok: true as const, demo: true };
    }

    if (!isLiveSupabaseConfigured) {
      setError('Live Supabase credentials are not configured in this environment.');
      return { ok: false as const };
    }

    const { data, error: err } = await supabase.rpc(fn, args);
    if (err) {
      setError(friendly(err));
      return { ok: false as const };
    }
    reload();
    return { ok: true as const, data };
  }, [mode, reload, supabase]);

  const actions = useMemo(() => ({
    revokeAllSessions: (userId: string, reason?: string) =>
      act('owner_revoke_user_sessions', { p_user_id: userId, p_reason: reason ?? null }),
    setStatus: (userId: string, status: 'active' | 'suspended') =>
      act('owner_set_status', { p_user_id: userId, p_status: status }),
    setRole: (userId: string, role: 'admin' | 'member') =>
      act('owner_set_role', { p_user_id: userId, p_role: role }),
    unlock: (userId: string) => act('owner_unlock_user', { p_user_id: userId }),
  }), [act]);

  // CSV export with CSV injection protection
  const exportCsv = useCallback(async (maxRows = 10_000) => {
    const f = filtersRef.current;
    const out: AuditRow[] = [];
    let c: { ts: string; id: string } | null = null;

    if (mode === 'DEMO' || !isLiveSupabaseConfigured) {
      out.push(...rows);
    } else {
      while (out.length < maxRows) {
        const { data, error: err } = await supabase.rpc('owner_list_audit_logs', {
          p_limit: 200,
          p_cursor_ts: c?.ts ?? null,
          p_cursor_id: c?.id ?? null,
          p_event_types: f.eventTypes.length ? f.eventTypes : null,
          p_user_id: f.userId,
          p_from: f.from,
          p_to: f.to,
          p_search: f.search.trim() || null,
        });
        if (err) { setError(friendly(err)); return; }
        const page = (data ?? []) as AuditRow[];
        out.push(...page);
        if (page.length < 200) break;
        c = { ts: page[page.length - 1].created_at, id: page[page.length - 1].id };
      }
    }

    const cell = (v: unknown) => {
      let s = v == null ? '' : typeof v === 'object' ? JSON.stringify(v) : String(v);
      if (/^[=+\-@\t\r]/.test(s)) s = `'${s}`;
      return `"${s.replace(/"/g, '""')}"`;
    };
    const header = ['time', 'event', 'email', 'ip', 'country', 'user_agent', 'metadata'];
    const lines = out.map((r) =>
      [r.created_at, r.event_type, r.email, r.ip_address, r.country_code, r.user_agent, r.metadata].map(cell).join(','));
    const blob = new Blob([[header.join(','), ...lines].join('\n')], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `fluentmeet-${mode.toLowerCase()}-audit-${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }, [mode, rows, supabase]);

  return {
    kpis,
    rows,
    hasMore,
    loading,
    error,
    filters,
    setFilters,
    liveCount,
    loadMore,
    reload,
    actions,
    exportCsv,
  };
}
