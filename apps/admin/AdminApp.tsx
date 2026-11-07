import React, { useState } from 'react';
import {
  ShieldAlert,
  Users,
  Building2,
  CreditCard,
  Cpu,
  Layers,
  Activity,
  AlertOctagon,
  FileCheck2,
  Settings,
  Search,
  Filter,
  RefreshCw,
  ExternalLink,
  ChevronRight,
  Sparkles,
  Server,
  Database,
  Radio,
  Lock,
  ArrowUpRight,
  TrendingUp,
  UserCheck,
  Download
} from 'lucide-react';
import { Button, Input, Card, Badge, StatCard } from '../../design-system/components';
import { DEMO_ADMIN_DATA } from '../demoData';
import { AdminExtensionReleases } from './AdminExtensionReleases';

export type AdminPage =
  | 'admin-overview'
  | 'admin-users'
  | 'admin-user-details'
  | 'admin-orgs'
  | 'admin-org-details'
  | 'admin-subscriptions'
  | 'admin-plans'
  | 'admin-ai-usage'
  | 'admin-queues'
  | 'admin-system'
  | 'admin-errors'
  | 'admin-audit'
  | 'admin-settings'
  | 'admin-extension-releases';

interface AdminAppProps {
  initialPage?: AdminPage;
  onPageChange?: (page: AdminPage) => void;
  isDark?: boolean;
}

export const AdminApp: React.FC<AdminAppProps> = ({
  initialPage = 'admin-overview',
  onPageChange,
  isDark = false,
}) => {
  const [currentPage, setCurrentPage] = useState<AdminPage>(initialPage);
  const [searchUser, setSearchUser] = useState('');
  const [selectedUser, setSelectedUser] = useState<any>({
    name: 'Priya Sharma',
    email: 'priya.sharma@acme.com',
    org: 'Acme Corp',
    role: 'Team Member',
    status: 'Active',
    meetings: 24,
    lastActive: '12 mins ago',
    extensionPaired: true
  });

  const navigateTo = (page: AdminPage) => {
    setCurrentPage(page);
    if (onPageChange) onPageChange(page);
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col antialiased">
      {/* Super Admin Top Navigation */}
      <header className="h-16 border-b border-slate-800 bg-slate-950 px-6 flex items-center justify-between sticky top-0 z-30">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-rose-600 text-white flex items-center justify-center font-bold text-sm">
            <ShieldAlert className="w-4 h-4" />
          </div>
          <div>
            <span className="font-bold text-sm tracking-tight text-white block leading-none">
              Super Admin Console
            </span>
            <span className="text-[10px] font-semibold uppercase tracking-wider text-rose-400">
              Platform Operations & Governance
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Badge variant="success" size="sm">System Operational</Badge>
          <div className="h-4 w-px bg-slate-800" />
          <span className="text-xs text-slate-400">admin@meetingcoach.ai</span>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* Admin Sidebar Navigation */}
        <aside className="w-60 bg-slate-950 border-r border-slate-800 p-3 space-y-4 flex flex-col shrink-0">
          <div className="space-y-0.5 text-xs font-medium">
            <button
              onClick={() => navigateTo('admin-overview')}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg transition-colors ${
                currentPage === 'admin-overview' ? 'bg-rose-950/60 text-rose-300' : 'text-slate-400 hover:bg-slate-900 hover:text-white'
              }`}
            >
              <Activity className="w-4 h-4" />
              <span>Admin Overview</span>
            </button>

            <button
              onClick={() => navigateTo('admin-users')}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg transition-colors ${
                currentPage === 'admin-users' || currentPage === 'admin-user-details' ? 'bg-rose-950/60 text-rose-300' : 'text-slate-400 hover:bg-slate-900 hover:text-white'
              }`}
            >
              <Users className="w-4 h-4" />
              <span>User Management</span>
            </button>

            <button
              onClick={() => navigateTo('admin-orgs')}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg transition-colors ${
                currentPage === 'admin-orgs' || currentPage === 'admin-org-details' ? 'bg-rose-950/60 text-rose-300' : 'text-slate-400 hover:bg-slate-900 hover:text-white'
              }`}
            >
              <Building2 className="w-4 h-4" />
              <span>Organizations</span>
            </button>

            <button
              onClick={() => navigateTo('admin-subscriptions')}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg transition-colors ${
                currentPage === 'admin-subscriptions' ? 'bg-rose-950/60 text-rose-300' : 'text-slate-400 hover:bg-slate-900 hover:text-white'
              }`}
            >
              <CreditCard className="w-4 h-4" />
              <span>Subscriptions</span>
            </button>

            <button
              onClick={() => navigateTo('admin-plans')}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg transition-colors ${
                currentPage === 'admin-plans' ? 'bg-rose-950/60 text-rose-300' : 'text-slate-400 hover:bg-slate-900 hover:text-white'
              }`}
            >
              <Layers className="w-4 h-4" />
              <span>Plan Management</span>
            </button>

            <button
              onClick={() => navigateTo('admin-ai-usage')}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg transition-colors ${
                currentPage === 'admin-ai-usage' ? 'bg-rose-950/60 text-rose-300' : 'text-slate-400 hover:bg-slate-900 hover:text-white'
              }`}
            >
              <Cpu className="w-4 h-4" />
              <span>AI Usage & Economics</span>
            </button>

            <button
              onClick={() => navigateTo('admin-queues')}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg transition-colors ${
                currentPage === 'admin-queues' ? 'bg-rose-950/60 text-rose-300' : 'text-slate-400 hover:bg-slate-900 hover:text-white'
              }`}
            >
              <Server className="w-4 h-4" />
              <span>Processing Queue</span>
            </button>

            <button
              onClick={() => navigateTo('admin-system')}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg transition-colors ${
                currentPage === 'admin-system' ? 'bg-rose-950/60 text-rose-300' : 'text-slate-400 hover:bg-slate-900 hover:text-white'
              }`}
            >
              <Database className="w-4 h-4" />
              <span>System Health</span>
            </button>

            <button
              onClick={() => navigateTo('admin-errors')}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg transition-colors ${
                currentPage === 'admin-errors' ? 'bg-rose-950/60 text-rose-300' : 'text-slate-400 hover:bg-slate-900 hover:text-white'
              }`}
            >
              <AlertOctagon className="w-4 h-4" />
              <span>Error Telemetry</span>
            </button>

            <button
              onClick={() => navigateTo('admin-audit')}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg transition-colors ${
                currentPage === 'admin-audit' ? 'bg-rose-950/60 text-rose-300' : 'text-slate-400 hover:bg-slate-900 hover:text-white'
              }`}
            >
              <FileCheck2 className="w-4 h-4" />
              <span>Audit Logs</span>
            </button>

            <button
              onClick={() => navigateTo('admin-settings')}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg transition-colors ${
                currentPage === 'admin-settings' ? 'bg-rose-950/60 text-rose-300' : 'text-slate-400 hover:bg-slate-900 hover:text-white'
              }`}
            >
              <Settings className="w-4 h-4" />
              <span>Platform Config</span>
            </button>

            <button
              onClick={() => navigateTo('admin-extension-releases')}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg transition-colors ${
                currentPage === 'admin-extension-releases' ? 'bg-rose-950/60 text-rose-300' : 'text-slate-400 hover:bg-slate-900 hover:text-white'
              }`}
            >
              <Download className="w-4 h-4" />
              <span>Extension Releases</span>
            </button>
          </div>
        </aside>

        {/* Admin Content Area */}
        <main className="flex-1 overflow-y-auto p-6 max-w-7xl mx-auto w-full space-y-6">
          {/* SCREEN 01: ADMIN OVERVIEW */}
          {currentPage === 'admin-overview' && (
            <div className="space-y-6">
              <div>
                <h1 className="text-xl font-bold tracking-tight text-white">Platform Health & Global Operations</h1>
                <p className="text-xs text-slate-400 mt-1">Cross-tenant activity, pipeline throughput, and AI model economics</p>
              </div>

              {/* Top Operational Metrics */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card className="bg-slate-950 border-slate-800 text-left">
                  <span className="text-xs text-slate-400">Total Registered Tenants</span>
                  <p className="text-2xl font-bold text-white mt-1 tabular-nums">{DEMO_ADMIN_DATA.totalOrganizations}</p>
                  <span className="text-[11px] text-emerald-400 mt-1 block">+8 this week</span>
                </Card>

                <Card className="bg-slate-950 border-slate-800 text-left">
                  <span className="text-xs text-slate-400">Processed Audio Minutes</span>
                  <p className="text-2xl font-bold text-white mt-1 tabular-nums">{DEMO_ADMIN_DATA.audioMinutesProcessed.toLocaleString()} mins</p>
                  <span className="text-[11px] text-slate-400 mt-1 block">99.82% success SLA</span>
                </Card>

                <Card className="bg-slate-950 border-slate-800 text-left">
                  <span className="text-xs text-slate-400">Gemini AI Token Spend</span>
                  <p className="text-2xl font-bold text-rose-400 mt-1 tabular-nums">{DEMO_ADMIN_DATA.aiTokenConsumption}</p>
                  <span className="text-[11px] text-slate-400 mt-1 block">Estimated Cost: {DEMO_ADMIN_DATA.estimatedApiCost}</span>
                </Card>

                <Card className="bg-slate-950 border-slate-800 text-left">
                  <span className="text-xs text-slate-400">Processing Backlog</span>
                  <p className="text-2xl font-bold text-emerald-400 mt-1 tabular-nums">{DEMO_ADMIN_DATA.workerQueueBacklog} tasks</p>
                  <span className="text-[11px] text-emerald-400 mt-1 block">12 worker nodes active</span>
                </Card>
              </div>

              {/* Subsystems Health Card */}
              <Card className="bg-slate-950 border-slate-800 space-y-3">
                <h3 className="text-sm font-semibold text-white">Infrastructure Status</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 text-xs">
                  <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                    <span className="text-slate-400 block text-[11px]">FastAPI Gateway</span>
                    <span className="font-semibold text-emerald-400">{DEMO_ADMIN_DATA.systemHealth.apiGateway}</span>
                  </div>
                  <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                    <span className="text-slate-400 block text-[11px]">WebSocket Streamer</span>
                    <span className="font-semibold text-emerald-400">{DEMO_ADMIN_DATA.systemHealth.webSocketServer}</span>
                  </div>
                  <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                    <span className="text-slate-400 block text-[11px]">Redis Queue & Cache</span>
                    <span className="font-semibold text-emerald-400">{DEMO_ADMIN_DATA.systemHealth.redisCluster}</span>
                  </div>
                </div>
              </Card>
            </div>
          )}

          {/* SCREEN 02: USER MANAGEMENT */}
          {currentPage === 'admin-users' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-xl font-bold text-white">Global User Directory</h1>
                  <p className="text-xs text-slate-400">{DEMO_ADMIN_DATA.totalUsers} registered users across all tenants</p>
                </div>
              </div>

              <Card className="bg-slate-950 border-slate-800" padding="none">
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-slate-800 text-[11px] font-semibold text-slate-400 uppercase bg-slate-900/60">
                        <th className="py-3 px-4">User</th>
                        <th className="py-3 px-4">Organization</th>
                        <th className="py-3 px-4">Role</th>
                        <th className="py-3 px-4">Meetings</th>
                        <th className="py-3 px-4">Status</th>
                        <th className="py-3 px-4 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/80">
                      {[
                        { name: 'Priya Sharma', email: 'priya.sharma@acme.com', org: 'Acme Corp', role: 'Team Member', meetings: 24, status: 'Active' },
                        { name: 'Carlos Mendez', email: 'carlos@acme.com', org: 'Acme Corp', role: 'Team Manager', meetings: 18, status: 'Active' },
                        { name: 'Sarah Jenkins', email: 'sarah.j@acme.com', org: 'Acme Corp', role: 'Org Admin', meetings: 32, status: 'Active' },
                        { name: 'David Chen', email: 'david.chen@acme.com', org: 'Acme Corp', role: 'Team Member', meetings: 12, status: 'Active' },
                      ].map((u, i) => (
                        <tr key={i} className="hover:bg-slate-900/40 cursor-pointer" onClick={() => navigateTo('admin-user-details')}>
                          <td className="py-3 px-4 font-semibold text-white">{u.name}</td>
                          <td className="py-3 px-4 text-slate-400">{u.org}</td>
                          <td className="py-3 px-4">{u.role}</td>
                          <td className="py-3 px-4">{u.meetings}</td>
                          <td className="py-3 px-4"><Badge variant="success" size="sm">{u.status}</Badge></td>
                          <td className="py-3 px-4 text-right">
                            <Button size="sm" variant="ghost">Inspect →</Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Card>
            </div>
          )}

          {/* SCREEN 03: USER DETAILS */}
          {currentPage === 'admin-user-details' && (
            <div className="space-y-4 max-w-xl">
              <div className="flex items-center justify-between">
                <h1 className="text-xl font-bold text-white">User Inspection: Priya Sharma</h1>
                <Button size="sm" variant="ghost" onClick={() => navigateTo('admin-users')}>Back to Directory</Button>
              </div>

              <Card className="bg-slate-950 border-slate-800 space-y-3 text-xs">
                <div>
                  <span className="text-slate-400 block text-[11px]">Email Address</span>
                  <span className="font-semibold text-white">priya.sharma@acme.com</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[11px]">Assigned Organization Tenant</span>
                  <span className="font-semibold text-white">Acme Corp (ID: tenant-acme-842)</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[11px]">Chrome Extension Pairing State</span>
                  <span className="font-semibold text-emerald-400">Paired (Token ID: tok_ext_9284)</span>
                </div>
                <div className="pt-3 border-t border-slate-800 flex gap-2">
                  <Button size="sm" variant="outline">Impersonate Session</Button>
                  <Button size="sm" variant="destructive">Suspend User</Button>
                </div>
              </Card>
            </div>
          )}

          {/* SCREEN 04: ORG MANAGEMENT */}
          {currentPage === 'admin-orgs' && (
            <div className="space-y-4">
              <h1 className="text-xl font-bold text-white">Tenant Organization Registry</h1>
              <Card className="bg-slate-950 border-slate-800" padding="none">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-800 text-[11px] font-semibold text-slate-400 uppercase bg-slate-900/60">
                      <th className="py-3 px-4">Organization</th>
                      <th className="py-3 px-4">Plan Tier</th>
                      <th className="py-3 px-4">Seat Usage</th>
                      <th className="py-3 px-4">Retention</th>
                      <th className="py-3 px-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {[
                      { name: 'Acme Corp', plan: 'Enterprise Team', seats: '25 / 40 seats', retention: '7 Days' },
                      { name: 'TechFlow Global', plan: 'Team Plan', seats: '12 / 15 seats', retention: '30 Days' },
                      { name: 'Stripe Partners', plan: 'Enterprise Custom', seats: '84 / 100 seats', retention: 'Ephemeral' },
                    ].map((org, i) => (
                      <tr key={i} className="hover:bg-slate-900/40 cursor-pointer" onClick={() => navigateTo('admin-org-details')}>
                        <td className="py-3 px-4 font-semibold text-white">{org.name}</td>
                        <td className="py-3 px-4"><Badge variant="primary" size="sm">{org.plan}</Badge></td>
                        <td className="py-3 px-4">{org.seats}</td>
                        <td className="py-3 px-4 text-slate-400">{org.retention}</td>
                        <td className="py-3 px-4 text-right"><Button size="sm" variant="ghost">Edit Tenant →</Button></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </Card>
            </div>
          )}

          {/* SCREEN 05: ORG DETAILS */}
          {currentPage === 'admin-org-details' && (
            <div className="space-y-4 max-w-xl">
              <div className="flex items-center justify-between">
                <h1 className="text-xl font-bold text-white">Tenant Details: Acme Corp</h1>
                <Button size="sm" variant="ghost" onClick={() => navigateTo('admin-orgs')}>Back</Button>
              </div>
              <Card className="bg-slate-950 border-slate-800 space-y-3 text-xs">
                <div>
                  <span className="text-slate-400 block text-[11px]">Tenant Plan</span>
                  <span className="font-semibold text-white">Enterprise Team ($499/mo)</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[11px]">Allocated Audio Quota</span>
                  <span className="font-semibold text-white">2,500 minutes / month</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[11px]">Enforced Privacy Retention</span>
                  <span className="font-semibold text-white">7-Day Automatic Purging</span>
                </div>
              </Card>
            </div>
          )}

          {/* SCREEN 06: SUBSCRIPTION MANAGEMENT */}
          {currentPage === 'admin-subscriptions' && (
            <div className="space-y-4">
              <h1 className="text-xl font-bold text-white">SaaS Subscriptions</h1>
              <Card className="bg-slate-950 border-slate-800 p-4 text-xs space-y-2">
                <p className="text-slate-400">Total Active Subscriptions: 78 accounts • Monthly Recurring Revenue (MRR): $18,420</p>
              </Card>
            </div>
          )}

          {/* SCREEN 07: PLAN MANAGEMENT */}
          {currentPage === 'admin-plans' && (
            <div className="space-y-4">
              <h1 className="text-xl font-bold text-white">Pricing & Plan Tier Configuration</h1>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card className="bg-slate-950 border-slate-800 space-y-2 text-xs">
                  <h3 className="font-bold text-white text-sm">Individual Pro</h3>
                  <p className="text-slate-400">$29 / month</p>
                  <p className="text-slate-500">500 meeting minutes</p>
                </Card>
                <Card className="bg-slate-950 border-slate-800 space-y-2 text-xs border-rose-500/50">
                  <h3 className="font-bold text-white text-sm">Team Tier</h3>
                  <p className="text-slate-400">$19 / seat / month</p>
                  <p className="text-slate-500">Shared pool: 1,500 minutes</p>
                </Card>
                <Card className="bg-slate-950 border-slate-800 space-y-2 text-xs">
                  <h3 className="font-bold text-white text-sm">Enterprise</h3>
                  <p className="text-slate-400">Custom billing</p>
                  <p className="text-slate-500">Unlimited retention controls</p>
                </Card>
              </div>
            </div>
          )}

          {/* SCREEN 08: AI USAGE */}
          {currentPage === 'admin-ai-usage' && (
            <div className="space-y-4">
              <h1 className="text-xl font-bold text-white">Google Gemini API Token Consumption</h1>
              <Card className="bg-slate-950 border-slate-800 p-4 text-xs space-y-2">
                <p className="text-slate-400">Total Tokens Consumed: 124.6M tokens • Average tokens per meeting minute: 840 tokens</p>
                <p className="text-slate-400">Schema Validation Errors: 0.02% (Target &lt; 0.1%)</p>
              </Card>
            </div>
          )}

          {/* SCREEN 09: PROCESSING QUEUE */}
          {currentPage === 'admin-queues' && (
            <div className="space-y-4">
              <h1 className="text-xl font-bold text-white">Asynchronous Task Queue (Celery / Redis)</h1>
              <Card className="bg-slate-950 border-slate-800 p-4 text-xs space-y-2">
                <p className="text-slate-400">Active Tasks: 3 • Queue Latency: 420ms • Dead-letter tasks: 0</p>
              </Card>
            </div>
          )}

          {/* SCREEN 10: SYSTEM MONITORING */}
          {currentPage === 'admin-system' && (
            <div className="space-y-4">
              <h1 className="text-xl font-bold text-white">System Health & Telemetry</h1>
              <Card className="bg-slate-950 border-slate-800 p-4 text-xs space-y-2">
                <p className="text-emerald-400">All systems normal. Database connection pool: 18% capacity.</p>
              </Card>
            </div>
          )}

          {/* SCREEN 11: ERROR LOGS */}
          {currentPage === 'admin-errors' && (
            <div className="space-y-4">
              <h1 className="text-xl font-bold text-white">Real-Time Error Telemetry</h1>
              <Card className="bg-slate-950 border-slate-800 p-4 text-xs font-mono text-slate-400 space-y-1">
                <p className="text-emerald-400">[INFO] 2026-11-06T04:22:18Z Stream session-842 finalized normally.</p>
                <p className="text-amber-400">[WARN] 2026-11-06T04:19:12Z Client reported transient WS buffer flush (12 frames).</p>
              </Card>
            </div>
          )}

          {/* SCREEN 12: AUDIT LOGS */}
          {currentPage === 'admin-audit' && (
            <div className="space-y-4">
              <h1 className="text-xl font-bold text-white">Compliance & Governance Audit Trail</h1>
              <Card className="bg-slate-950 border-slate-800" padding="none">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-800 text-[11px] font-semibold text-slate-400 uppercase bg-slate-900/60">
                      <th className="py-3 px-4">Action</th>
                      <th className="py-3 px-4">Actor</th>
                      <th className="py-3 px-4">Details</th>
                      <th className="py-3 px-4">Timestamp</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {DEMO_ADMIN_DATA.recentAuditLogs.map((log) => (
                      <tr key={log.id}>
                        <td className="py-3 px-4 font-bold text-rose-400">{log.action}</td>
                        <td className="py-3 px-4 text-white">{log.actor}</td>
                        <td className="py-3 px-4 text-slate-400">{log.target}</td>
                        <td className="py-3 px-4 text-slate-500">{log.time}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </Card>
            </div>
          )}

          {/* SCREEN 13: ADMIN SETTINGS */}
          {currentPage === 'admin-settings' && (
            <div className="space-y-4 max-w-xl">
              <h1 className="text-xl font-bold text-white">Platform Settings & Maintenance Mode</h1>
              <Card className="bg-slate-950 border-slate-800 p-4 space-y-3 text-xs">
                <label className="flex items-center justify-between cursor-pointer">
                  <span>Maintenance Mode (Temporarily rejects new meeting capture)</span>
                  <input type="checkbox" />
                </label>
                <Button size="sm">Save Global Config</Button>
              </Card>
            </div>
          )}

          {/* SCREEN 14: EXTENSION RELEASE MANAGEMENT */}
          {currentPage === 'admin-extension-releases' && (
            <AdminExtensionReleases />
          )}
        </main>
      </div>
    </div>
  );
};

