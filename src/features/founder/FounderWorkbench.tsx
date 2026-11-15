// src/features/founder/FounderWorkbench.tsx
// Founder-only User Management, Session Activity & Audit Logs
// WCAG 2.1 AA compliant, responsive, accessible native drawer, live presence indicators.
import React, { useEffect, useRef, useState } from 'react';
import {
  Users,
  Activity,
  UserCheck,
  ShieldAlert,
  Search,
  Filter,
  Download,
  Clock,
  Globe,
  Laptop,
  Smartphone,
  Tablet,
  CheckCircle2,
  XCircle,
  KeyRound,
  Lock,
  Unlock,
  AlertTriangle,
  RotateCcw,
  ExternalLink,
  ChevronRight,
  Shield,
  Radio,
  FileSpreadsheet
} from 'lucide-react';
import { supabase } from '../../lib/supabase';
import {
  useUserManagement,
  type AuditEventType,
  type AuditRow,
} from './useUserManagement';

const EVENT_LABEL: Record<AuditEventType, string> = {
  LOGIN_SUCCESS: 'Login Successful',
  LOGIN_FAILED: 'Failed Login Attempt',
  LOGOUT: 'Session Logout',
  SESSION_REVOKED: 'Session Force Revoked',
  PASSWORD_CHANGED: 'Password Changed',
  ACCOUNT_LOCKED: 'Account Locked Out',
  ACCOUNT_UNLOCKED: 'Account Unlocked',
  ROLE_CHANGED: 'Role Changed',
  STATUS_CHANGED: 'Status Changed',
};

const EVENT_STYLE: Record<AuditEventType, { icon: React.ReactNode; cls: string }> = {
  LOGIN_SUCCESS: {
    icon: <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />,
    cls: 'bg-emerald-50 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800',
  },
  LOGIN_FAILED: {
    icon: <XCircle className="w-3.5 h-3.5 text-rose-600 dark:text-rose-400" />,
    cls: 'bg-rose-50 text-rose-800 dark:bg-rose-950/60 dark:text-rose-300 border-rose-200 dark:border-rose-800',
  },
  LOGOUT: {
    icon: <RotateCcw className="w-3.5 h-3.5 text-slate-600 dark:text-slate-400" />,
    cls: 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300 border-slate-200 dark:border-slate-700',
  },
  SESSION_REVOKED: {
    icon: <ShieldAlert className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" />,
    cls: 'bg-amber-50 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300 border-amber-200 dark:border-amber-800',
  },
  PASSWORD_CHANGED: {
    icon: <KeyRound className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />,
    cls: 'bg-indigo-50 text-indigo-800 dark:bg-indigo-950/60 dark:text-indigo-300 border-indigo-200 dark:border-indigo-800',
  },
  ACCOUNT_LOCKED: {
    icon: <Lock className="w-3.5 h-3.5 text-red-600 dark:text-red-400" />,
    cls: 'bg-red-50 text-red-800 dark:bg-red-950/60 dark:text-red-300 border-red-200 dark:border-red-800',
  },
  ACCOUNT_UNLOCKED: {
    icon: <Unlock className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />,
    cls: 'bg-emerald-50 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800',
  },
  ROLE_CHANGED: {
    icon: <Shield className="w-3.5 h-3.5 text-purple-600 dark:text-purple-400" />,
    cls: 'bg-purple-50 text-purple-800 dark:bg-purple-950/60 dark:text-purple-300 border-purple-200 dark:border-purple-800',
  },
  STATUS_CHANGED: {
    icon: <AlertTriangle className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" />,
    cls: 'bg-amber-50 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300 border-amber-200 dark:border-amber-800',
  },
};

const ALL_EVENTS = Object.keys(EVENT_LABEL) as AuditEventType[];

function flag(cc: string | null) {
  if (!cc || !/^[A-Za-z]{2}$/.test(cc)) return '🌐';
  return String.fromCodePoint(...[...cc.toUpperCase()].map((c) => 0x1f1a5 + c.charCodeAt(0)));
}

const fmt = (iso: string) =>
  new Date(iso).toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'medium',
  });

function KpiCard({
  label,
  value,
  sublabel,
  icon,
  live,
}: {
  label: string;
  value: number | string;
  sublabel?: string;
  icon: React.ReactNode;
  live?: boolean;
}) {
  return (
    <div className="rounded-2xl border border-slate-200/90 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 shadow-sm transition-all hover:shadow-md">
      <div className="flex items-center justify-between">
        <dt className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          {live && (
            <span aria-hidden="true" className="relative flex h-2.5 w-2.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-emerald-500" />
            </span>
          )}
          {label}
        </dt>
        <div className="p-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
          {icon}
        </div>
      </div>
      <dd className="mt-2 text-3xl font-extrabold tabular-nums text-slate-900 dark:text-white">
        {value}
      </dd>
      {sublabel && (
        <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
          {sublabel}
        </p>
      )}
    </div>
  );
}

function SessionInspectorModal({
  row,
  onClose,
  onTimeline,
  actions,
}: {
  row: AuditRow | null;
  onClose: () => void;
  onTimeline: (userId: string) => void;
  actions: ReturnType<typeof useUserManagement>['actions'];
}) {
  const ref = useRef<HTMLDialogElement>(null);
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const d = ref.current;
    if (!d) return;
    if (row && !d.open) d.showModal();
    if (!row && d.open) d.close();
    setConfirming(false);
  }, [row]);

  const run = async (fn: () => Promise<{ ok: boolean }>) => {
    setBusy(true);
    await fn();
    setBusy(false);
    setConfirming(false);
  };
  const uid = row?.user_id;

  return (
    <dialog
      ref={ref}
      onClose={onClose}
      aria-labelledby="inspector-title"
      className="m-0 ml-auto h-full w-full max-w-lg bg-white p-6 text-slate-900 shadow-2xl backdrop:bg-black/60 dark:bg-slate-900 dark:text-white z-50 border-l border-slate-200 dark:border-slate-800"
    >
      {row && (
        <div className="flex h-full flex-col gap-5 overflow-y-auto">
          {/* Header */}
          <div className="flex items-start justify-between pb-4 border-b border-slate-100 dark:border-slate-800">
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-600 dark:text-indigo-400">
                Live Session Inspector
              </span>
              <h2 id="inspector-title" className="text-lg font-bold text-slate-900 dark:text-white break-all">
                {row.email ?? 'Unknown Account'}
              </h2>
              <p className="text-xs text-slate-500 font-mono mt-0.5">ID: {uid ?? 'Unregistered IP'}</p>
            </div>
            <button
              onClick={onClose}
              aria-label="Close inspector"
              className="p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition-colors"
            >
              ✕
            </button>
          </div>

          {/* Details list */}
          <div className="space-y-3 bg-slate-50 dark:bg-slate-800/60 p-4 rounded-2xl border border-slate-200/80 dark:border-slate-700/80 text-xs">
            <div className="flex justify-between py-1 border-b border-slate-200/60 dark:border-slate-700/60">
              <span className="text-slate-500 font-medium">Last Event</span>
              <span className="font-semibold text-slate-900 dark:text-white">{EVENT_LABEL[row.event_type]}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-200/60 dark:border-slate-700/60">
              <span className="text-slate-500 font-medium">Timestamp</span>
              <span className="font-mono text-slate-900 dark:text-white">{fmt(row.created_at)}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-200/60 dark:border-slate-700/60">
              <span className="text-slate-500 font-medium">Country / Region</span>
              <span className="font-semibold flex items-center gap-1.5">
                <span>{flag(row.country_code)}</span>
                <span>{row.country_code ?? 'Global / Unknown'}</span>
              </span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-200/60 dark:border-slate-700/60">
              <span className="text-slate-500 font-medium">Network (Masked)</span>
              <span className="font-mono text-indigo-600 dark:text-indigo-400 font-semibold">{row.ip_address ?? '—'}</span>
            </div>
            <div className="pt-1">
              <span className="text-slate-500 font-medium block mb-1">User Agent & Client Device</span>
              <p className="font-mono text-[11px] text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-900 p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 break-words">
                {row.user_agent ?? '—'}
              </p>
            </div>
          </div>

          {/* Timeline action */}
          {uid && (
            <button
              onClick={() => {
                onTimeline(uid);
                onClose();
              }}
              className="w-full py-2.5 px-4 rounded-xl border border-indigo-200 dark:border-indigo-800/80 bg-indigo-50/60 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300 font-semibold text-xs flex items-center justify-center gap-2 hover:bg-indigo-100 dark:hover:bg-indigo-900/40 transition-colors"
            >
              <Clock className="w-4 h-4" />
              <span>Filter This User&apos;s Full Audit Timeline</span>
            </button>
          )}

          {/* Security & Administrative Actions */}
          {uid && (
            <div className="mt-auto pt-4 border-t border-slate-200 dark:border-slate-800 space-y-3">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block">
                Administrative Security Controls
              </span>

              {!confirming ? (
                <button
                  onClick={() => setConfirming(true)}
                  disabled={busy}
                  className="w-full py-3 px-4 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs shadow-md shadow-rose-600/20 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
                >
                  <ShieldAlert className="w-4 h-4" />
                  <span>Revoke All Active Sessions (Remote Logout)</span>
                </button>
              ) : (
                <div role="alertdialog" aria-label="Confirm revoke" className="rounded-2xl border border-rose-300 bg-rose-50 dark:bg-rose-950/40 p-4 space-y-2.5">
                  <p className="text-xs text-rose-900 dark:text-rose-200 font-medium">
                    Are you sure? This will immediately invalidate all refresh tokens and terminate this user&apos;s active sessions on all devices.
                  </p>
                  <div className="flex gap-2">
                    <button
                      autoFocus
                      disabled={busy}
                      onClick={() => run(() => actions.revokeAllSessions(uid, 'Revoked by founder via inspector'))}
                      className="flex-1 py-2 rounded-xl bg-rose-600 text-white font-bold text-xs hover:bg-rose-700 transition-colors"
                    >
                      {busy ? 'Terminating…' : 'Yes, Revoke Sessions'}
                    </button>
                    <button
                      onClick={() => setConfirming(false)}
                      className="flex-1 py-2 rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-xs font-semibold"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}

              <div className="grid grid-cols-2 gap-2">
                <button
                  disabled={busy}
                  onClick={() => run(() => actions.setStatus(uid, 'suspended'))}
                  className="py-2.5 px-3 rounded-xl border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-200"
                >
                  Suspend Account
                </button>
                <button
                  disabled={busy}
                  onClick={() => run(() => actions.setStatus(uid, 'active'))}
                  className="py-2.5 px-3 rounded-xl border border-emerald-300 dark:border-emerald-800 hover:bg-emerald-50 dark:hover:bg-emerald-950/50 text-xs font-semibold text-emerald-700 dark:text-emerald-300"
                >
                  Reactivate
                </button>
                <button
                  disabled={busy}
                  onClick={() => run(() => actions.unlock(uid))}
                  className="py-2.5 px-3 rounded-xl border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-200"
                >
                  Unlock Login
                </button>
                <button
                  disabled={busy}
                  onClick={() => run(() => actions.setRole(uid, 'admin'))}
                  className="py-2.5 px-3 rounded-xl border border-indigo-300 dark:border-indigo-800 hover:bg-indigo-50 dark:hover:bg-indigo-950/50 text-xs font-semibold text-indigo-700 dark:text-indigo-300"
                >
                  Make Admin
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </dialog>
  );
}

export const FounderWorkbench: React.FC = () => {
  const {
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
  } = useUserManagement(supabase);

  const [selected, setSelected] = useState<AuditRow | null>(null);

  const toggleEvent = (t: AuditEventType) =>
    setFilters({
      eventTypes: filters.eventTypes.includes(t)
        ? filters.eventTypes.filter((x) => x !== t)
        : [...filters.eventTypes, t],
    });

  return (
    <div className="max-w-7xl mx-auto space-y-6 p-4 sm:p-6 lg:p-8 font-sans">
      {/* Header bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-slate-200 dark:border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white tracking-tight">
              User Management &amp; Audit Trail
            </h1>
            <span className="px-2 py-0.5 rounded-full bg-indigo-100 dark:bg-indigo-950/80 text-indigo-700 dark:text-indigo-300 text-[11px] font-bold border border-indigo-200 dark:border-indigo-800">
              Live Presence Engine
            </span>
          </div>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-0.5">
            Real-time session monitoring, immutable authentication audit trail, and remote access revocation.
          </p>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto">
          <button
            onClick={() => void exportCsv()}
            className="px-3.5 py-2 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600 text-xs font-semibold text-slate-700 dark:text-slate-200 shadow-sm flex items-center gap-2 transition-all"
          >
            <FileSpreadsheet className="w-4 h-4 text-emerald-600" />
            <span>Export CSV</span>
          </button>
          <button
            onClick={reload}
            className="px-3 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold shadow-md shadow-indigo-600/20 flex items-center gap-1.5 transition-all"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* KPI Cards Row */}
      <section aria-label="Key Performance Indicators">
        <dl className="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-3.5 sm:gap-4">
          <KpiCard
            label="Total Users"
            value={kpis?.total_users ?? '—'}
            sublabel={`+${kpis?.new_signups_today ?? 0} new registrations today`}
            icon={<Users className="w-5 h-5 text-indigo-500" />}
          />
          <KpiCard
            label="Active Now"
            value={kpis?.active_now ?? '—'}
            sublabel="Live heartbeat within last 5 mins"
            icon={<Activity className="w-5 h-5 text-emerald-500" />}
            live
          />
          <KpiCard
            label="Daily Active (DAU)"
            value={kpis?.dau ?? '—'}
            sublabel={`${kpis?.returning_users ?? 0} returning members`}
            icon={<UserCheck className="w-5 h-5 text-blue-500" />}
          />
          <KpiCard
            label="Failed Logins (24h)"
            value={kpis?.failed_24h ?? '—'}
            sublabel="Brute-force protection active"
            icon={<ShieldAlert className="w-5 h-5 text-rose-500" />}
          />
        </dl>
      </section>

      {/* Audit Log Filters */}
      <section className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/90 dark:border-slate-800 p-4 sm:p-5 shadow-sm space-y-4">
        <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-3">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 flex-1">
            {/* Search by email */}
            <div>
              <label htmlFor="f-search" className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                Search by Email
              </label>
              <div className="relative">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  id="f-search"
                  type="search"
                  placeholder="e.g. user@domain.com"
                  className="w-full pl-9 pr-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs font-medium text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  value={filters.search}
                  onChange={(e) => setFilters({ search: e.target.value })}
                />
              </div>
            </div>

            {/* From Date */}
            <div>
              <label htmlFor="f-from" className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                From Date
              </label>
              <input
                id="f-from"
                type="date"
                className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs font-medium text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                onChange={(e) => setFilters({ from: e.target.value ? new Date(e.target.value).toISOString() : null })}
              />
            </div>

            {/* To Date */}
            <div>
              <label htmlFor="f-to" className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                To Date
              </label>
              <input
                id="f-to"
                type="date"
                className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs font-medium text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                onChange={(e) =>
                  setFilters({
                    to: e.target.value
                      ? new Date(new Date(e.target.value).getTime() + 86_400_000).toISOString()
                      : null,
                  })
                }
              />
            </div>
          </div>

          {/* Reset button if filtered */}
          {(filters.search || filters.from || filters.to || filters.eventTypes.length > 0 || filters.userId) && (
            <button
              onClick={() => setFilters({ search: '', from: null, to: null, eventTypes: [], userId: null })}
              className="text-xs font-semibold text-rose-600 dark:text-rose-400 hover:underline py-2 self-start"
            >
              Clear All Filters
            </button>
          )}
        </div>

        {/* Event Type Badges Filter */}
        <div>
          <span className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-2">
            Filter by Event Type
          </span>
          <div className="flex flex-wrap gap-1.5">
            {ALL_EVENTS.map((t) => {
              const active = filters.eventTypes.includes(t);
              return (
                <button
                  key={t}
                  onClick={() => toggleEvent(t)}
                  className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold border transition-all flex items-center gap-1.5 ${
                    active
                      ? 'bg-indigo-600 text-white border-indigo-600 shadow-sm'
                      : 'bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700 hover:border-slate-300'
                  }`}
                >
                  <span>{EVENT_LABEL[t]}</span>
                </button>
              );
            })}
          </div>
        </div>
      </section>

      {/* Realtime Live notification alert */}
      <div aria-live="polite" className="min-h-5">
        {error && (
          <div role="alert" className="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/60 border border-rose-200 dark:border-rose-800 text-rose-800 dark:text-rose-200 text-xs font-semibold">
            {error}
          </div>
        )}
        {liveCount > 0 && (
          <button
            onClick={reload}
            className="w-full py-2 px-4 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-xs font-bold shadow-md shadow-indigo-600/20 flex items-center justify-center gap-2 hover:opacity-95 transition-all animate-bounce"
          >
            <Radio className="w-3.5 h-3.5 animate-pulse" />
            <span>{liveCount} new authentication events detected — Click to view latest</span>
          </button>
        )}
      </div>

      {/* Audit Log Table */}
      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/90 dark:border-slate-800 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[760px] text-left text-xs">
            <thead className="bg-slate-50 dark:bg-slate-800/80 text-slate-500 dark:text-slate-400 font-bold uppercase tracking-wider text-[10px] border-b border-slate-100 dark:border-slate-800">
              <tr>
                <th scope="col" className="p-3.5">Time</th>
                <th scope="col" className="p-3.5">Event</th>
                <th scope="col" className="p-3.5">User Identity</th>
                <th scope="col" className="p-3.5">Location</th>
                <th scope="col" className="p-3.5">Device &amp; IP</th>
                <th scope="col" className="p-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {rows.map((r) => {
                const s = EVENT_STYLE[r.event_type] || EVENT_STYLE.LOGOUT;
                return (
                  <tr key={r.id} className="hover:bg-slate-50/80 dark:hover:bg-slate-800/50 transition-colors">
                    {/* Timestamp */}
                    <td className="p-3.5 whitespace-nowrap font-mono text-slate-500 dark:text-slate-400 text-[11px]">
                      {fmt(r.created_at)}
                    </td>

                    {/* Event badge */}
                    <td className="p-3.5">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold border ${s.cls}`}>
                        {s.icon}
                        <span>{EVENT_LABEL[r.event_type]}</span>
                      </span>
                    </td>

                    {/* User email */}
                    <td className="p-3.5 font-semibold text-slate-900 dark:text-white break-all">
                      {r.email ?? <span className="text-slate-400 italic">Unknown account</span>}
                    </td>

                    {/* Location */}
                    <td className="p-3.5 whitespace-nowrap">
                      <span className="flex items-center gap-1.5">
                        <span className="text-base">{flag(r.country_code)}</span>
                        <span className="font-medium text-slate-700 dark:text-slate-300">
                          {r.country_code ?? 'Global'}
                        </span>
                      </span>
                    </td>

                    {/* Device & IP */}
                    <td className="p-3.5 max-w-[200px]">
                      <div className="font-mono text-[11px] text-indigo-600 dark:text-indigo-400 font-semibold truncate">
                        {r.ip_address ?? '—'}
                      </div>
                      <div className="text-[10px] text-slate-400 truncate" title={r.user_agent ?? ''}>
                        {r.user_agent ?? '—'}
                      </div>
                    </td>

                    {/* Action button */}
                    <td className="p-3.5 text-right">
                      <button
                        onClick={() => setSelected(r)}
                        className="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-[11px] font-semibold text-slate-700 dark:text-slate-300 transition-colors inline-flex items-center gap-1"
                      >
                        <span>Inspect</span>
                        <ChevronRight className="w-3 h-3 text-slate-400" />
                      </button>
                    </td>
                  </tr>
                );
              })}

              {!loading && rows.length === 0 && (
                <tr>
                  <td colSpan={6} className="p-8 text-center text-slate-500">
                    No authentication events match your filter criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Load More pagination button */}
        {hasMore && (
          <div className="p-4 border-t border-slate-100 dark:border-slate-800 flex justify-center bg-slate-50/50 dark:bg-slate-800/30">
            <button
              onClick={loadMore}
              disabled={loading}
              className="px-6 py-2 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:border-slate-300 font-semibold text-xs text-slate-700 dark:text-slate-200 shadow-sm disabled:opacity-50"
            >
              {loading ? 'Fetching Next Keyset Batch…' : 'Load More Events'}
            </button>
          </div>
        )}
      </div>

      {/* Session Inspector Drawer Modal */}
      <SessionInspectorModal
        row={selected}
        onClose={() => setSelected(null)}
        actions={actions}
        onTimeline={(userId) =>
          setFilters({
            userId,
            eventTypes: ['LOGIN_SUCCESS', 'LOGIN_FAILED', 'LOGOUT', 'SESSION_REVOKED'],
          })
        }
      />
    </div>
  );
};

export default FounderWorkbench;
