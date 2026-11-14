import React, { useState } from 'react';
import {
  LayoutDashboard,
  Video,
  FileText,
  TrendingUp,
  BookOpen,
  Users,
  Settings,
  CreditCard,
  Shield,
  Bell,
  Search,
  CheckCircle2,
  AlertCircle,
  Play,
  RotateCcw,
  Sparkles,
  Award,
  Calendar,
  Clock,
  ChevronRight,
  Filter,
  Download,
  Trash2,
  ExternalLink,
  ChevronDown,
  Layers,
  HelpCircle,
  LogOut,
  Moon,
  Sun,
  Menu,
  X,
  Volume2,
  Check,
  BookmarkPlus,
  ArrowRight,
  BarChart2,
  Mic,
  Languages,
  Puzzle,
  MoreVertical
} from 'lucide-react';
import { ChromeExtensionPage } from './ChromeExtensionPage';
import TeamSettings from './src/features/team/TeamSettings';
import {
  ReportSummaryView,
  ParticipantReportDetail,
  HistoricalTrendView,
  ReportSnapshot,
  HistoricalComparisonData,
} from './src/features/reports';
import {
  Button,
  Input,
  Card,
  Badge,
  StatCard,
  ScoreIndicator,
  AudioPlayer,
  TranscriptSegment,
  GrammarErrorCard,
  EmptyState,
  ErrorState,
  Modal,
  ConfirmationDialog,
  PlatformIcon,
  PlatformBadge,
  PlatformSelect,
} from '../../design-system/components';
import {
  useTabDataMode,
  DataModeSelector,
  DemoModeNotice,
  DEMO_MEETINGS,
  DEMO_TRANSCRIPT_SEGMENTS,
  DEMO_MISTAKES,
  DEMO_VOCABULARY_SUGGESTIONS,
  DEMO_TEAM_ANALYTICS,
  DEMO_ADMIN_DATA,
  DEMO_MEETING_SUMMARY_SNAPSHOT,
  DEMO_PARTICIPANT_SNAPSHOT,
  DEMO_HISTORICAL_DATA,
  DemoMeeting,
} from './src/demo';

export type DashboardPage =
  | 'overview'
  | 'meetings'
  | 'meeting-details'
  | 'transcript-viewer'
  | 'report'
  | 'my-performance'
  | 'grammar'
  | 'vocabulary'
  | 'fluency'
  | 'pronunciation'
  | 'ielts-practice'
  | 'learning-center'
  | 'mistakes'
  | 'improvement-plan'
  | 'team-analytics'
  | 'team-settings'
  | 'integrations'
  | 'chrome-extension'
  | 'billing'
  | 'profile-settings'
  | 'privacy-settings'
  | 'security-settings'
  | 'notification-settings';

interface DashboardAppProps {
  initialPage?: DashboardPage;
  onPageChange?: (page: DashboardPage) => void;
  isDark: boolean;
  onToggleTheme: () => void;
}

export const DashboardApp: React.FC<DashboardAppProps> = ({
  initialPage = 'overview',
  onPageChange,
  isDark,
  onToggleTheme,
}) => {
  const { getMode, setMode, isDemo } = useTabDataMode('priya_sharma');
  const [realMeetings, setRealMeetings] = useState<DemoMeeting[]>([]);
  const [realSavedMistakes, setRealSavedMistakes] = useState<string[]>([]);
  const [currentPage, setCurrentPage] = useState<DashboardPage>(initialPage);
  const [selectedMeeting, setSelectedMeeting] = useState<DemoMeeting>(DEMO_MEETINGS[0]);
  const [activeTab, setActiveTab] = useState<'overview' | 'transcript' | 'participants' | 'analysis'>('overview');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [platformFilter, setPlatformFilter] = useState<'all' | 'google-meet' | 'zoom' | 'teams'>('all');
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [audioCurrentTime, setAudioCurrentTime] = useState(252);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [savedMistakes, setSavedMistakes] = useState<string[]>(['dm-1']);
  const [practiceAnswered, setPracticeAnswered] = useState<number | null>(null);
  const [selectedTranscriptMistake, setSelectedTranscriptMistake] = useState<any>(null);
  const [reportSubView, setReportSubView] = useState<'summary' | 'participant' | 'history'>('summary');
  const [openActionMenuId, setOpenActionMenuId] = useState<string | null>(null);

  const navigateTo = (page: DashboardPage) => {
    setCurrentPage(page);
    setMobileMenuOpen(false);
    if (onPageChange) onPageChange(page);
  };

  const filteredMeetings = DEMO_MEETINGS.filter((m) => {
    const matchesSearch = m.title.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesPlatform = platformFilter === 'all' || m.platform === platformFilter;
    return matchesSearch && matchesPlatform;
  });

  const toggleSaveMistake = (id: string) => {
    if (savedMistakes.includes(id)) {
      setSavedMistakes(savedMistakes.filter((mId) => mId !== id));
    } else {
      setSavedMistakes([...savedMistakes, id]);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex flex-col antialiased">
      {/* Top Application Bar */}
      <header className="h-16 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-4 flex items-center justify-between sticky top-0 z-30 shadow-xs">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 rounded-lg text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>

          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-indigo-600 text-white flex items-center justify-center font-bold text-base shadow-sm">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <span className="font-bold text-sm tracking-tight text-slate-900 dark:text-white block leading-none">
                AI Meeting Coach
              </span>
              <span className="text-[10px] font-semibold uppercase tracking-wider text-indigo-600 dark:text-indigo-400">
                Enterprise SaaS
              </span>
            </div>
          </div>

          <div className="hidden lg:flex items-center gap-2 ml-6 pl-6 border-l border-slate-200 dark:border-slate-800">
            <Badge variant="primary" size="sm">Acme Corp Workspace</Badge>
            <span className="text-xs text-slate-400">•</span>
            <span className="text-xs text-slate-500 font-medium">Engineering Dept</span>
          </div>
        </div>

        {/* Global Search and Actions */}
        <div className="flex items-center gap-3">
          <div className="relative hidden md:block w-64">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
            <input
              type="text"
              placeholder="Search meetings, errors, vocabulary..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full h-9 pl-9 pr-3 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 text-xs text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
            />
          </div>

          <button
            onClick={onToggleTheme}
            className="p-2 rounded-lg text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            title={isDark ? 'Switch to Light Theme' : 'Switch to Dark Theme'}
          >
            {isDark ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4" />}
          </button>

          <div className="h-6 w-px bg-slate-200 dark:bg-slate-800" />

          {/* User Profile */}
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-600 to-violet-500 text-white font-bold text-xs flex items-center justify-center shadow-xs">
              PS
            </div>
            <div className="hidden sm:block text-left">
              <span className="text-xs font-semibold block leading-tight text-slate-800 dark:text-slate-200">
                Priya Sharma
              </span>
              <span className="text-[10px] text-slate-400 block leading-tight">
                Senior Engineer
              </span>
            </div>
          </div>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* Left Navigation Sidebar */}
        <aside
          className={`
            fixed md:static inset-y-0 left-0 z-20 w-64 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col transition-all duration-200 ease-in-out
            ${mobileMenuOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
            ${sidebarCollapsed ? 'md:w-16' : 'md:w-64'}
          `}
        >
          <div className="flex-1 overflow-y-auto p-3 space-y-6">
            {/* Workspace Group */}
            <div>
              {!sidebarCollapsed && (
                <p className="px-3 text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                  Workspace
                </p>
              )}
              <div className="space-y-0.5">
                <button
                  onClick={() => navigateTo('overview')}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                    currentPage === 'overview'
                      ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                  }`}
                >
                  <LayoutDashboard className="w-4 h-4 shrink-0" />
                  {!sidebarCollapsed && <span>Dashboard Overview</span>}
                </button>

                <button
                  onClick={() => navigateTo('meetings')}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                    currentPage === 'meetings' || currentPage === 'meeting-details' || currentPage === 'transcript-viewer' || currentPage === 'report'
                      ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                  }`}
                >
                  <Video className="w-4 h-4 shrink-0" />
                  {!sidebarCollapsed && <span>All Meetings</span>}
                </button>
              </div>
            </div>

            {/* My English Group */}
            <div>
              {!sidebarCollapsed && (
                <p className="px-3 text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                  My English
                </p>
              )}
              <div className="space-y-0.5">
                <button
                  onClick={() => navigateTo('my-performance')}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                    currentPage === 'my-performance'
                      ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                  }`}
                >
                  <TrendingUp className="w-4 h-4 shrink-0" />
                  {!sidebarCollapsed && <span>My Performance</span>}
                </button>

                <button
                  onClick={() => navigateTo('grammar')}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                    currentPage === 'grammar'
                      ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                  }`}
                >
                  <FileText className="w-4 h-4 shrink-0" />
                  {!sidebarCollapsed && <span>Grammar Analysis</span>}
                </button>

                <button
                  onClick={() => navigateTo('vocabulary')}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                    currentPage === 'vocabulary'
                      ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                  }`}
                >
                  <Languages className="w-4 h-4 shrink-0" />
                  {!sidebarCollapsed && <span>Vocabulary</span>}
                </button>

                <button
                  onClick={() => navigateTo('fluency')}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                    currentPage === 'fluency'
                      ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                  }`}
                >
                  <Mic className="w-4 h-4 shrink-0" />
                  {!sidebarCollapsed && <span>Fluency Dynamics</span>}
                </button>

                <button
                  onClick={() => navigateTo('pronunciation')}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                    currentPage === 'pronunciation'
                      ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                  }`}
                >
                  <Volume2 className="w-4 h-4 shrink-0" />
                  {!sidebarCollapsed && <span>Pronunciation</span>}
                </button>

                <button
                  onClick={() => navigateTo('ielts-practice')}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                    currentPage === 'ielts-practice'
                      ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                  }`}
                >
                  <Award className="w-4 h-4 shrink-0 text-amber-500" />
                  {!sidebarCollapsed && <span>IELTS Benchmarking</span>}
                </button>
              </div>
            </div>

            {/* Learning Group */}
            <div>
              {!sidebarCollapsed && (
                <p className="px-3 text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                  Learning
                </p>
              )}
              <div className="space-y-0.5">
                <button
                  onClick={() => navigateTo('learning-center')}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                    currentPage === 'learning-center'
                      ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                  }`}
                >
                  <BookOpen className="w-4 h-4 shrink-0" />
                  {!sidebarCollapsed && <span>Learning Center</span>}
                </button>

                <button
                  onClick={() => navigateTo('mistakes')}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                    currentPage === 'mistakes'
                      ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                  }`}
                >
                  <BookmarkPlus className="w-4 h-4 shrink-0" />
                  {!sidebarCollapsed && <span>Mistake History</span>}
                </button>

                <button
                  onClick={() => navigateTo('improvement-plan')}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                    currentPage === 'improvement-plan'
                      ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                  }`}
                >
                  <BarChart2 className="w-4 h-4 shrink-0" />
                  {!sidebarCollapsed && <span>Improvement Plan</span>}
                </button>
              </div>
            </div>

            {/* Organization Group */}
            <div>
              {!sidebarCollapsed && (
                <p className="px-3 text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                  Organization
                </p>
              )}
              <div className="space-y-0.5">
                <button
                  onClick={() => navigateTo('team-analytics')}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                    currentPage === 'team-analytics'
                      ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                  }`}
                >
                  <Users className="w-4 h-4 shrink-0" />
                  {!sidebarCollapsed && <span>Team Analytics</span>}
                </button>

                <button
                  onClick={() => navigateTo('team-settings')}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                    currentPage === 'team-settings'
                      ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                  }`}
                >
                  <Shield className="w-4 h-4 shrink-0 text-indigo-500" />
                  {!sidebarCollapsed && <span>Team Workspace Seats</span>}
                </button>
              </div>
            </div>

            {/* System & Settings Group */}
            <div>
              {!sidebarCollapsed && (
                <p className="px-3 text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                  System
                </p>
              )}
              <div className="space-y-0.5">
                <button
                  onClick={() => navigateTo('integrations')}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                    currentPage === 'integrations'
                      ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                  }`}
                >
                  <Layers className="w-4 h-4 shrink-0" />
                  {!sidebarCollapsed && <span>Integrations</span>}
                </button>

                <button
                  onClick={() => navigateTo('chrome-extension')}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                    currentPage === 'chrome-extension'
                      ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                  }`}
                >
                  <Puzzle className="w-4 h-4 shrink-0" />
                  {!sidebarCollapsed && <span>Chrome Extension</span>}
                </button>

                <button
                  onClick={() => navigateTo('billing')}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                    currentPage === 'billing'
                      ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                  }`}
                >
                  <CreditCard className="w-4 h-4 shrink-0" />
                  {!sidebarCollapsed && <span>Billing & Usage</span>}
                </button>

                <button
                  onClick={() => navigateTo('profile-settings')}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                    currentPage.includes('settings')
                      ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                  }`}
                >
                  <Settings className="w-4 h-4 shrink-0" />
                  {!sidebarCollapsed && <span>Settings</span>}
                </button>
              </div>
            </div>
          </div>

          <div className="p-3 border-t border-slate-200 dark:border-slate-800">
            <button
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="hidden md:flex w-full items-center justify-center p-2 rounded-lg text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs font-medium"
            >
              {sidebarCollapsed ? '→' : '← Collapse Sidebar'}
            </button>
          </div>
        </aside>

        {/* Main Application Body */}
        <main className="flex-1 overflow-y-auto p-4 md:p-8 max-w-7xl mx-auto w-full">
          {/* Breadcrumb Bar */}
          <div className="flex items-center gap-2 text-xs text-slate-400 mb-6 font-medium">
            <span className="hover:text-slate-700 dark:hover:text-slate-300 cursor-pointer" onClick={() => navigateTo('overview')}>
              Dashboard
            </span>
            <span>/</span>
            <span className="text-slate-800 dark:text-slate-200 capitalize">
              {currentPage.replace('-', ' ')}
            </span>
          </div>

          {/* PAGE 01: OVERVIEW */}
          {currentPage === 'overview' && (
            <div className="space-y-6">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
                    Good morning, Priya
                  </h1>
                  <p className="text-xs text-slate-500 mt-1">
                    {isDemo('overview')
                      ? 'Thursday, Nov 6, 2026 • Your spoken English mastery increased by 3.2% this month.'
                      : 'Welcome to your real-time English communication workspace.'}
                  </p>
                </div>
                <div className="flex items-center gap-2.5">
                  <DataModeSelector
                    mode={getMode('overview')}
                    onChange={(m) => setMode('overview', m)}
                    tabLabel="Overview"
                  />
                  <Button variant="outline" size="sm" onClick={() => navigateTo('integrations')}>
                    Check Extension
                  </Button>
                  <Button size="sm" onClick={() => navigateTo('learning-center')}>
                    Today's 3-Min Practice
                  </Button>
                </div>
              </div>

              {isDemo('overview') && (
                <DemoModeNotice
                  tabName="Dashboard Overview"
                  onSwitchReal={() => setMode('overview', 'REAL')}
                />
              )}

              {/* 4 KPI Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard
                  title="Total Meetings Analyzed"
                  value={isDemo('overview') ? "24" : String(realMeetings.length)}
                  change={isDemo('overview') ? "+4 this mo" : "0 this mo"}
                  trend={isDemo('overview') ? "up" : "neutral"}
                  supportingText="All browser meeting sessions"
                  icon={<Video className="w-4 h-4 text-indigo-600" />}
                />
                <StatCard
                  title="Total Speaking Time"
                  value={isDemo('overview') ? "4h 32m" : "0m"}
                  change={isDemo('overview') ? "+12% activity" : "0% activity"}
                  trend={isDemo('overview') ? "up" : "neutral"}
                  supportingText="Active participant speech"
                  icon={<Clock className="w-4 h-4 text-emerald-600" />}
                />
                <StatCard
                  title="Average English Score"
                  value={isDemo('overview') ? "81 / 100" : "-- / 100"}
                  change={isDemo('overview') ? "+3.2% trend" : "Pending sessions"}
                  trend={isDemo('overview') ? "up" : "neutral"}
                  supportingText={isDemo('overview') ? "C1 Advanced Equivalent" : "Awaiting meeting audio"}
                  icon={<Sparkles className="w-4 h-4 text-indigo-600" />}
                />
                <StatCard
                  title="Resolved Mistakes"
                  value={isDemo('overview') ? "18" : String(realSavedMistakes.length)}
                  change={isDemo('overview') ? "85% retention" : "0% retention"}
                  trend={isDemo('overview') ? "up" : "neutral"}
                  supportingText="Eliminated via practice drills"
                  icon={<CheckCircle2 className="w-4 h-4 text-emerald-600" />}
                />
              </div>

              {!isDemo('overview') ? (
                <Card className="p-8 text-center space-y-4">
                  <div className="w-14 h-14 rounded-2xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mx-auto">
                    <Sparkles className="w-7 h-7" />
                  </div>
                  <div className="max-w-md mx-auto space-y-1">
                    <h3 className="text-base font-bold text-slate-900 dark:text-white">
                      No real meeting sessions analyzed yet
                    </h3>
                    <p className="text-xs text-slate-500 leading-relaxed">
                      You are viewing the <strong>REAL VERSION</strong>. Connect the FluentMeet AI Chrome Extension on your Google Meet, Zoom, or Teams call to capture spoken English and view live performance metrics.
                    </p>
                  </div>
                  <div className="flex items-center justify-center gap-3 pt-2">
                    <Button size="sm" onClick={() => navigateTo('chrome-extension')}>
                      Open Chrome Extension Guide
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => setMode('overview', 'DEMO')}>
                      Preview Sample Data (Demo Mode)
                    </Button>
                  </div>
                </Card>
              ) : (
                <div className="space-y-6">

              {/* Performance Trend and Top Improvements */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <Card className="lg:col-span-2 space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-sm font-semibold text-slate-900 dark:text-white">
                        Linguistic Performance Trajectory
                      </h2>
                      <p className="text-xs text-slate-500">
                        Grammar, Vocabulary, Fluency & Pronunciation over the last 30 days
                      </p>
                    </div>
                    <Badge variant="primary" size="sm">Last 30 Days</Badge>
                  </div>

                  {/* Simulated Line Chart Area */}
                  <div className="h-56 w-full rounded-xl bg-slate-50 dark:bg-slate-950/60 border border-slate-100 dark:border-slate-800 p-4 flex flex-col justify-between">
                    <div className="flex items-center justify-between text-xs text-slate-400">
                      <span>Score 100</span>
                      <div className="flex items-center gap-4 text-[11px]">
                        <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-indigo-600" /> Grammar (84)</span>
                        <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500" /> Vocab (82)</span>
                        <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-amber-500" /> Fluency (78)</span>
                        <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-sky-500" /> Pronunciation (80)</span>
                      </div>
                    </div>
                    {/* SVG Curve */}
                    <div className="w-full h-32 relative">
                      <svg className="w-full h-full" viewBox="0 0 500 120" preserveAspectRatio="none">
                        <polyline
                          fill="none"
                          stroke="#6366F1"
                          strokeWidth="2.5"
                          strokeLinecap="round"
                          points="10,80 100,75 200,60 300,50 400,35 490,25"
                        />
                        <polyline
                          fill="none"
                          stroke="#10B981"
                          strokeWidth="2"
                          strokeDasharray="4 4"
                          points="10,90 100,85 200,70 300,65 400,45 490,40"
                        />
                      </svg>
                    </div>
                    <div className="flex items-center justify-between text-[11px] text-slate-400 border-t border-slate-200 dark:border-slate-800 pt-2">
                      <span>Oct 7</span>
                      <span>Oct 14</span>
                      <span>Oct 21</span>
                      <span>Oct 28</span>
                      <span>Nov 6 (Today)</span>
                    </div>
                  </div>
                </Card>

                {/* Top Improvement Areas */}
                <Card className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h2 className="text-sm font-semibold text-slate-900 dark:text-white">
                      Top Improvement Focus
                    </h2>
                    <span className="text-xs text-indigo-600 dark:text-indigo-400 font-medium cursor-pointer" onClick={() => navigateTo('grammar')}>
                      View all
                    </span>
                  </div>

                  <div className="space-y-3">
                    <div className="p-3 rounded-lg bg-rose-50/60 dark:bg-rose-950/20 border border-rose-200/60 dark:border-rose-900/40">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-rose-800 dark:text-rose-300">Preposition Omission</span>
                        <Badge variant="danger" size="sm">4 instances</Badge>
                      </div>
                      <p className="text-[11px] text-rose-700 dark:text-rose-400 mt-1">
                        Frequent omission with verbs like "explain to someone".
                      </p>
                    </div>

                    <div className="p-3 rounded-lg bg-amber-50/60 dark:bg-amber-950/20 border border-amber-200/60 dark:border-amber-900/40">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-amber-800 dark:text-amber-300">Future Conditionals</span>
                        <Badge variant="warning" size="sm">2 instances</Badge>
                      </div>
                      <p className="text-[11px] text-amber-700 dark:text-amber-400 mt-1">
                        Use present simple in "if" clauses, not "if I will have".
                      </p>
                    </div>

                    <div className="p-3 rounded-lg bg-sky-50/60 dark:bg-sky-950/20 border border-sky-200/60 dark:border-sky-900/40">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-sky-800 dark:text-sky-300">Filler Word "Actually"</span>
                        <Badge variant="info" size="sm">4.2% density</Badge>
                      </div>
                      <p className="text-[11px] text-sky-700 dark:text-sky-400 mt-1">
                        Pacing is healthy (142 WPM) but filler words disrupt tone.
                      </p>
                    </div>
                  </div>
                </Card>
              </div>

              {/* Recent Meetings Table */}
              <Card className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-sm font-semibold text-slate-900 dark:text-white">
                      Recent Meeting Sessions
                    </h2>
                    <p className="text-xs text-slate-500">
                      Click any meeting to inspect audio-synced transcripts and AI coaching reports
                    </p>
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => navigateTo('meetings')}>
                    View Full Archive →
                  </Button>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="border-b border-slate-200 dark:border-slate-800 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                        <th className="py-2.5 px-3">Meeting Title</th>
                        <th className="py-2.5 px-3">Platform</th>
                        <th className="py-2.5 px-3">Date</th>
                        <th className="py-2.5 px-3">Duration</th>
                        <th className="py-2.5 px-3">My Speech</th>
                        <th className="py-2.5 px-3">Score</th>
                        <th className="py-2.5 px-3 text-right">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 text-xs">
                      {DEMO_MEETINGS.map((m) => (
                        <tr
                          key={m.id}
                          className="hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition-colors cursor-pointer group"
                          onClick={() => {
                            setSelectedMeeting(m);
                            navigateTo('meeting-details');
                          }}
                        >
                          <td className="py-3 px-3 font-medium text-slate-900 dark:text-slate-100">
                            {m.title}
                          </td>
                          <td className="py-3 px-3">
                            <PlatformBadge platform={m.platform} size="sm" />
                          </td>
                          <td className="py-3 px-3 text-slate-500">{m.date}</td>
                          <td className="py-3 px-3 text-slate-500">{m.duration}</td>
                          <td className="py-3 px-3 font-semibold text-indigo-600 dark:text-indigo-400">
                            {m.mySpeakingTime}
                          </td>
                          <td className="py-3 px-3">
                            <span className="font-bold text-emerald-600 dark:text-emerald-400">
                              {m.overallScore}
                            </span>
                          </td>
                          <td className="py-3 px-3 text-right">
                            <Button variant="ghost" size="sm">
                              Report →
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Card>
            </div>
          )}
        </div>
      )}

          {/* PAGE 02: ALL MEETINGS */}
          {currentPage === 'meetings' && (
            <div className="space-y-6">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
                    Meetings Archive
                  </h1>
                  <p className="text-xs text-slate-500 mt-1">
                    Search and filter all past captured meeting sessions
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <DataModeSelector
                    mode={getMode('meetings')}
                    onChange={(m) => setMode('meetings', m)}
                    tabLabel="Meetings Archive"
                  />
                  <Button variant="outline" size="sm" leadingIcon={<Download className="w-3.5 h-3.5" />}>
                    Export CSV
                  </Button>
                </div>
              </div>

              {isDemo('meetings') && (
                <DemoModeNotice
                  tabName="Meetings Archive"
                  onSwitchReal={() => setMode('meetings', 'REAL')}
                />
              )}

              {/* Filters Bar with 3D Platform Selector */}
              <div className="flex flex-wrap items-center justify-between gap-3 bg-white dark:bg-slate-900 p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
                <div className="flex flex-wrap items-center gap-3">
                  <div className="flex items-center gap-1.5 text-xs font-bold text-slate-700 dark:text-slate-300">
                    <Filter className="w-4 h-4 text-indigo-500" />
                    <span>Filter Platform:</span>
                  </div>
                  <PlatformSelect
                    value={platformFilter}
                    onChange={(val) => setPlatformFilter(val as any)}
                    variant="pills"
                    size="sm"
                  />
                </div>
                <div className="hidden sm:block">
                  <span className="text-[11px] text-slate-400">
                    Showing {(isDemo('meetings') ? filteredMeetings : realMeetings).length} meetings
                  </span>
                </div>
              </div>

              {/* Real vs Demo Meeting List */}
              {!isDemo('meetings') && realMeetings.length === 0 ? (
                <Card className="p-8 text-center space-y-4">
                  <EmptyState
                    icon={<Video className="w-8 h-8 text-indigo-500" />}
                    title="No real meeting sessions found"
                    description="You are viewing the REAL VERSION. Start a meeting on Google Meet, Zoom, or Teams with the FluentMeet Chrome Extension to capture your real conversations."
                    actionLabel="Switch to Demo Version"
                    onAction={() => setMode('meetings', 'DEMO')}
                  />
                </Card>
              ) : (
                <Card padding="none">
                  <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                      <thead>
                        <tr className="border-b border-slate-200 dark:border-slate-800 text-[11px] font-semibold text-slate-400 uppercase tracking-wider bg-slate-50/50 dark:bg-slate-900/50">
                          <th className="py-3 px-4">Title</th>
                          <th className="py-3 px-4">Platform</th>
                          <th className="py-3 px-4">Date</th>
                          <th className="py-3 px-4">Duration</th>
                          <th className="py-3 px-4">Participants</th>
                          <th className="py-3 px-4">English Score</th>
                          <th className="py-3 px-4 text-right">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 text-xs">
                        {(isDemo('meetings') ? filteredMeetings : realMeetings).map((m) => (
                          <tr key={m.id} className="hover:bg-slate-50/80 dark:hover:bg-slate-800/40">
                            <td className="py-3.5 px-4 font-semibold text-slate-900 dark:text-slate-100">
                              {m.title}
                            </td>
                            <td className="py-3.5 px-4">
                              <PlatformBadge platform={m.platform} size="sm" />
                            </td>
                            <td className="py-3.5 px-4 text-slate-500">{m.date}</td>
                            <td className="py-3.5 px-4 text-slate-500">{m.duration}</td>
                            <td className="py-3.5 px-4">
                              <div className="flex -space-x-1.5">
                                {m.participants.map((p, idx) => (
                                  <div
                                    key={idx}
                                    className="w-5 h-5 rounded-full flex items-center justify-center text-[9px] font-bold text-white border-2 border-white dark:border-slate-900"
                                    style={{ backgroundColor: p.color }}
                                    title={p.name}
                                  >
                                    {p.name[0]}
                                  </div>
                                ))}
                              </div>
                            </td>
                            <td className="py-3.5 px-4">
                              <Badge variant="success" size="sm">{m.overallScore} / 100</Badge>
                            </td>
                            <td className="py-3.5 px-4 text-right">
                              <div className="flex items-center justify-end gap-1.5 relative">
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => {
                                    setSelectedMeeting(m);
                                    navigateTo('meeting-details');
                                  }}
                                >
                                  Details
                                </Button>
                                <Button
                                  variant="primary"
                                  size="sm"
                                  onClick={() => {
                                    setSelectedMeeting(m);
                                    navigateTo('report');
                                  }}
                                >
                                  Report
                                </Button>

                                {/* 3-Dot (Three Dots) Actions Menu */}
                                <div className="relative inline-block text-left">
                                  <button
                                    type="button"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      setOpenActionMenuId(openActionMenuId === m.id ? null : m.id);
                                    }}
                                    className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                                    title="More Options"
                                  >
                                    <MoreVertical className="w-4 h-4" />
                                  </button>

                                  {openActionMenuId === m.id && (
                                    <div
                                      onClick={(e) => e.stopPropagation()}
                                      className="absolute right-0 top-full mt-1 w-44 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xl py-1 z-50 text-left text-xs"
                                    >
                                      <button
                                        onClick={() => {
                                          setSelectedMeeting(m);
                                          navigateTo('meeting-details');
                                          setOpenActionMenuId(null);
                                        }}
                                        className="w-full px-3 py-1.5 flex items-center gap-2 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300"
                                      >
                                        <FileText className="w-3.5 h-3.5 text-indigo-500" />
                                        <span>Meeting Summary</span>
                                      </button>
                                      <button
                                        onClick={() => {
                                          setSelectedMeeting(m);
                                          navigateTo('transcript-viewer');
                                          setOpenActionMenuId(null);
                                        }}
                                        className="w-full px-3 py-1.5 flex items-center gap-2 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300"
                                      >
                                        <Volume2 className="w-3.5 h-3.5 text-emerald-500" />
                                        <span>Full Transcript</span>
                                      </button>
                                      <button
                                        onClick={() => {
                                          navigator.clipboard.writeText(window.location.origin + '/meetings/' + m.id);
                                          setOpenActionMenuId(null);
                                        }}
                                        className="w-full px-3 py-1.5 flex items-center gap-2 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300"
                                      >
                                        <ExternalLink className="w-3.5 h-3.5 text-sky-500" />
                                        <span>Copy Link</span>
                                      </button>
                                      <div className="h-px bg-slate-100 dark:bg-slate-800 my-1" />
                                      <button
                                        onClick={() => {
                                          setShowDeleteModal(true);
                                          setOpenActionMenuId(null);
                                        }}
                                        className="w-full px-3 py-1.5 flex items-center gap-2 hover:bg-rose-50 dark:hover:bg-rose-950/40 text-rose-600"
                                      >
                                        <Trash2 className="w-3.5 h-3.5" />
                                        <span>Delete Session</span>
                                      </button>
                                    </div>
                                  )}
                                </div>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </Card>
              )}
            </div>
          )}

          {/* PAGE 03: MEETING DETAILS */}
          {currentPage === 'meeting-details' && (
            <div className="space-y-6">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-4">
                <div>
                  <div className="flex items-center gap-2.5 mb-1.5">
                    <PlatformBadge platform={selectedMeeting.platform} size="md" />
                    <span className="text-xs text-slate-400">• {selectedMeeting.date} • {selectedMeeting.duration}</span>
                  </div>
                  <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-white">
                    {selectedMeeting.title}
                  </h1>
                </div>

                <div className="flex items-center gap-2">
                  <DataModeSelector
                    mode={getMode('meeting-details')}
                    onChange={(m) => setMode('meeting-details', m)}
                    tabLabel="Meeting Details"
                  />
                  <Button variant="outline" size="sm" onClick={() => navigateTo('transcript-viewer')}>
                    Open Transcript Viewer
                  </Button>
                  <Button size="sm" onClick={() => navigateTo('report')}>
                    My English Coaching Report
                  </Button>
                </div>
              </div>

              {isDemo('meeting-details') && (
                <DemoModeNotice
                  tabName="Meeting Details"
                  onSwitchReal={() => setMode('meeting-details', 'REAL')}
                />
              )}

              {!isDemo('meeting-details') && realMeetings.length === 0 ? (
                <Card className="p-8 text-center space-y-4">
                  <EmptyState
                    icon={<FileText className="w-8 h-8 text-indigo-500" />}
                    title="No real meeting selected"
                    description="You are in REAL VERSION mode. Select a recorded meeting from the Meetings archive or start a new recording via the Chrome Extension to view speaker participation and audio waveforms."
                    actionLabel="Switch to Demo Version"
                    onAction={() => setMode('meeting-details', 'DEMO')}
                  />
                </Card>
              ) : (
                <>
                  {/* Tabs Bar */}
                  <div className="flex items-center gap-4 border-b border-slate-200 dark:border-slate-800 text-xs font-semibold">
                    {(['overview', 'participants', 'analysis'] as const).map((tab) => (
                      <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
                        className={`pb-3 capitalize transition-colors relative ${
                          activeTab === tab
                            ? 'text-indigo-600 dark:text-indigo-400 border-b-2 border-indigo-600'
                            : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
                        }`}
                      >
                        {tab}
                      </button>
                    ))}
                  </div>

              {/* Tab Content */}
              {activeTab === 'overview' && (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  <Card className="lg:col-span-2 space-y-4">
                    <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
                      Executive Meeting Summary
                    </h3>
                    <ul className="space-y-2 text-xs text-slate-600 dark:text-slate-300 list-disc list-inside leading-relaxed">
                      {selectedMeeting.summary.map((pt, i) => (
                        <li key={i}>{pt}</li>
                      ))}
                    </ul>

                    <div className="pt-4 border-t border-slate-100 dark:border-slate-800">
                      <h4 className="text-xs font-semibold text-slate-800 dark:text-slate-200 mb-2">
                        Speaking Share Distribution
                      </h4>
                      <div className="space-y-2">
                        {selectedMeeting.participants.map((p, i) => (
                          <div key={i} className="space-y-1">
                            <div className="flex items-center justify-between text-xs">
                              <span className="font-medium text-slate-700 dark:text-slate-300">{p.name}</span>
                              <span className="font-semibold text-slate-900 dark:text-slate-100">{p.speakingShare}%</span>
                            </div>
                            <div className="w-full h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                              <div
                                className="h-full rounded-full"
                                style={{ width: `${p.speakingShare}%`, backgroundColor: p.color }}
                              />
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </Card>

                  <Card className="space-y-4 text-center">
                    <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
                      Your Spoken Score
                    </h3>
                    <ScoreIndicator score={selectedMeeting.overallScore} size="lg" label="Proficient (C1)" />
                    <p className="text-xs text-slate-500 leading-relaxed">
                      You spoke for {selectedMeeting.mySpeakingTime} during this call. 4 grammar nuances were detected.
                    </p>
                    <Button fullWidth size="sm" onClick={() => navigateTo('report')}>
                      Inspect Mistakes & Audio
                    </Button>
                  </Card>
                </div>
              )}

              {activeTab === 'participants' && (
                <Card padding="none">
                  <div className="p-4 border-b border-slate-200 dark:border-slate-800 font-semibold text-xs">
                    Discovered Participants ({selectedMeeting.participants.length})
                  </div>
                  <div className="divide-y divide-slate-100 dark:divide-slate-800">
                    {selectedMeeting.participants.map((p, i) => (
                      <div key={i} className="p-4 flex items-center justify-between text-xs">
                        <div className="flex items-center gap-3">
                          <div
                            className="w-8 h-8 rounded-full flex items-center justify-center font-bold text-white text-xs"
                            style={{ backgroundColor: p.color }}
                          >
                            {p.name[0]}
                          </div>
                          <div>
                            <span className="font-semibold text-slate-900 dark:text-slate-100 block">
                              {p.name}
                            </span>
                            <span className="text-[11px] text-slate-400">
                              Diarization Match Confidence: 94%
                            </span>
                          </div>
                        </div>
                        <Badge variant="neutral" size="sm">{p.speakingShare}% share</Badge>
                      </div>
                    ))}
                  </div>
                </Card>
              )}

              {activeTab === 'analysis' && (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {DEMO_MISTAKES.map((m) => (
                      <GrammarErrorCard
                        key={m.id}
                        originalSentence={m.original}
                        correctedSentence={m.corrected}
                        errorCategory={m.category}
                        severity={m.severity}
                        explanation={m.explanation}
                        timestamp={m.timestamp}
                        onPlayAudio={() => {
                          setIsPlayingAudio(true);
                          setAudioCurrentTime(252);
                        }}
                        onAddToPractice={() => toggleSaveMistake(m.id)}
                        isSaved={savedMistakes.includes(m.id)}
                      />
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      )}

          {/* PAGE 04: TRANSCRIPT VIEWER */}
          {currentPage === 'transcript-viewer' && (
            <div className="space-y-4 flex flex-col h-[calc(100vh-140px)]">
              <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
                <div>
                  <h1 className="text-lg font-bold text-slate-900 dark:text-white">
                    Interactive Transcript — {isDemo('transcript-viewer') ? selectedMeeting.title : 'Live Meeting Transcript'}
                  </h1>
                  <p className="text-xs text-slate-500">
                    Click any sentence to seek audio playback. Mistakes carry interactive explanations.
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <DataModeSelector
                    mode={getMode('transcript-viewer')}
                    onChange={(m) => setMode('transcript-viewer', m)}
                    tabLabel="Transcript Viewer"
                  />
                  <Button variant="outline" size="sm" onClick={() => navigateTo('report')}>
                    View Coaching Report
                  </Button>
                </div>
              </div>

              {isDemo('transcript-viewer') && (
                <DemoModeNotice
                  tabName="Interactive Transcript Viewer"
                  onSwitchReal={() => setMode('transcript-viewer', 'REAL')}
                />
              )}

              {!isDemo('transcript-viewer') ? (
                <Card className="p-8 text-center space-y-4 my-auto">
                  <EmptyState
                    icon={<Mic className="w-8 h-8 text-indigo-500" />}
                    title="No real transcript recorded"
                    description="You are viewing the REAL VERSION. Transcripts with word-level timestamps, speaker diarization, and linguistic mistake detection will appear here once meeting audio is captured and analyzed."
                    actionLabel="Preview Sample Transcript (Demo Mode)"
                    onAction={() => setMode('transcript-viewer', 'DEMO')}
                  />
                </Card>
              ) : (
                <>
                  {/* 3-Pane Transcript Layout */}
                  <div className="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-4 overflow-hidden">
                {/* Left Speaker Filter (1 col) */}
                <div className="hidden lg:block bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-3 space-y-3">
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
                    Speakers (4)
                  </span>
                  <div className="space-y-1">
                    {selectedMeeting.participants.map((p, i) => (
                      <button
                        key={i}
                        className="w-full flex items-center justify-between p-2 rounded-lg text-xs font-medium hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-left"
                      >
                        <span className="truncate">{p.name}</span>
                        <span className="text-[10px] font-mono text-slate-400">{p.speakingShare}%</span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Center Chronological Transcript Feed (2-3 cols) */}
                <div className="lg:col-span-2 overflow-y-auto space-y-3 pr-2">
                  {DEMO_TRANSCRIPT_SEGMENTS.map((seg) => (
                    <TranscriptSegment
                      key={seg.id}
                      speakerName={seg.speakerName}
                      speakerColor={seg.speakerColor}
                      timestamp={seg.timestamp}
                      text={seg.text}
                      mistakes={seg.mistakes}
                      isActive={audioCurrentTime >= seg.timestampSeconds && audioCurrentTime < seg.timestampSeconds + 40}
                      onPlayClick={() => {
                        setAudioCurrentTime(seg.timestampSeconds);
                        setIsPlayingAudio(true);
                      }}
                      onMistakeClick={(m) => setSelectedTranscriptMistake(m)}
                    />
                  ))}
                </div>

                {/* Right Inspector Drawer (1 col) */}
                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 space-y-3">
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
                    Mistake Inspector
                  </span>
                  {selectedTranscriptMistake ? (
                    <div className="space-y-3">
                      <Badge variant="danger" size="sm">{selectedTranscriptMistake.type}</Badge>
                      <div>
                        <p className="text-xs text-slate-400">Original phrase:</p>
                        <p className="text-sm font-semibold text-rose-600 line-through">
                          {selectedTranscriptMistake.original}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-400">Native rephrase:</p>
                        <p className="text-sm font-semibold text-emerald-600">
                          {selectedTranscriptMistake.corrected}
                        </p>
                      </div>
                      <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-slate-800 p-2.5 rounded-lg">
                        {selectedTranscriptMistake.explanation}
                      </p>
                      <Button fullWidth size="sm" onClick={() => setSelectedTranscriptMistake(null)}>
                        Clear Inspector
                      </Button>
                    </div>
                  ) : (
                    <div className="text-center py-12 text-slate-400 text-xs">
                      Click any highlighted mistake underline in the transcript to inspect grammar explanations.
                    </div>
                  )}
                </div>
              </div>

              {/* Sticky Bottom Audio Player */}
              <div className="pt-2">
                <AudioPlayer
                  currentTime={audioCurrentTime}
                  duration={selectedMeeting.durationSeconds}
                  isPlaying={isPlayingAudio}
                  onPlayPause={() => setIsPlayingAudio(!isPlayingAudio)}
                  onSeek={(secs) => setAudioCurrentTime(secs)}
                />
              </div>
            </>
          )}
        </div>
      )}

          {/* PAGE 05: INDIVIDUAL REPORT & STEP 10 ANALYTICS ENGINE */}
          {currentPage === 'report' && (
            <div className="space-y-6">
              {/* Report Sub-view Navigation Bar */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-4">
                <div>
                  <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
                    English Performance & Meeting Analytics Report
                  </h1>
                  <p className="text-xs text-slate-500 mt-1">
                    Multi-speaker calibrated scoring, longitudinal progress, and IELTS-style practice assessment
                  </p>
                </div>

                <div className="flex items-center gap-3">
                  <DataModeSelector
                    mode={getMode('report')}
                    onChange={(m) => setMode('report', m)}
                    tabLabel="Report"
                  />
                  {/* Sub-view Switcher Tabs */}
                  <div className="flex items-center gap-1.5 p-1 bg-slate-100 dark:bg-slate-800/80 rounded-xl border border-slate-200 dark:border-slate-700">
                    <button
                      onClick={() => setReportSubView('summary')}
                      className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                        reportSubView === 'summary'
                          ? 'bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-xs'
                          : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                      }`}
                    >
                      Meeting Summary
                    </button>
                    <button
                      onClick={() => setReportSubView('participant')}
                      className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                        reportSubView === 'participant'
                          ? 'bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-xs'
                          : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                      }`}
                    >
                      Speaker Assessment
                    </button>
                    <button
                      onClick={() => setReportSubView('history')}
                      className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                        reportSubView === 'history'
                          ? 'bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-xs'
                          : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                      }`}
                    >
                      Historical Trajectory
                    </button>
                  </div>
                </div>
              </div>

              {isDemo('report') && (
                <DemoModeNotice
                  tabName="Communication & IELTS Report"
                  onSwitchReal={() => setMode('report', 'REAL')}
                />
              )}

              {/* Sub-view Contents */}
              {!isDemo('report') ? (
                <Card className="p-8 text-center space-y-4">
                  <EmptyState
                    icon={<Award className="w-8 h-8 text-indigo-500" />}
                    title="No communication report generated yet"
                    description="You are in REAL VERSION mode. Complete an analyzed meeting session to view calibrated multi-speaker scores, pronunciation accuracy, and IELTS-style band metrics."
                    actionLabel="Switch to Demo Version"
                    onAction={() => setMode('report', 'DEMO')}
                  />
                </Card>
              ) : (
                <>
                  {reportSubView === 'summary' && (
                    <ReportSummaryView
                      snapshot={DEMO_MEETING_SUMMARY_SNAPSHOT}
                      onSelectParticipant={() => setReportSubView('participant')}
                    />
                  )}

                  {reportSubView === 'participant' && (
                    <ParticipantReportDetail
                      snapshot={DEMO_PARTICIPANT_SNAPSHOT}
                      onBackToSummary={() => setReportSubView('summary')}
                    />
                  )}

                  {reportSubView === 'history' && (
                    <HistoricalTrendView data={DEMO_HISTORICAL_DATA} />
                  )}
                </>
              )}
            </div>
          )}

          {/* PAGE 06: MY PERFORMANCE */}
          {currentPage === 'my-performance' && (
            <div className="space-y-6">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
                    Longitudinal English Trajectory
                  </h1>
                  <p className="text-xs text-slate-500 mt-1">
                    Multi-week retention, fluency dynamics, and mistake mastery progress
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <DataModeSelector
                    mode={getMode('my-performance')}
                    onChange={(m) => setMode('my-performance', m)}
                    tabLabel="My Performance"
                  />
                  <Badge variant="primary" size="md">C1 Advanced Track</Badge>
                </div>
              </div>

              {isDemo('my-performance') && (
                <DemoModeNotice
                  tabName="Longitudinal Performance"
                  onSwitchReal={() => setMode('my-performance', 'REAL')}
                />
              )}

              {!isDemo('my-performance') ? (
                <Card className="p-8 text-center space-y-4">
                  <EmptyState
                    icon={<TrendingUp className="w-8 h-8 text-indigo-500" />}
                    title="No performance trends recorded"
                    description="You are in REAL VERSION mode. Track your speaking growth across meetings. As you complete sessions, your linguistic velocity and IELTS band trajectory will map out here."
                    actionLabel="Switch to Demo Version"
                    onAction={() => setMode('my-performance', 'DEMO')}
                  />
                </Card>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <Card className="space-y-3">
                    <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
                      Grammar Mastery Progress
                    </h3>
                    <div className="space-y-2 text-xs">
                      <div>
                        <div className="flex justify-between text-slate-600 dark:text-slate-400 mb-1">
                          <span>Preposition Consistency</span>
                          <span className="font-semibold text-emerald-600">85% Mastered</span>
                        </div>
                        <div className="w-full h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                          <div className="h-full bg-emerald-500 w-[85%]" />
                        </div>
                      </div>
                      <div>
                        <div className="flex justify-between text-slate-600 dark:text-slate-400 mb-1">
                          <span>Conditional Tenses</span>
                          <span className="font-semibold text-amber-600">60% Mastered</span>
                        </div>
                        <div className="w-full h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                          <div className="h-full bg-amber-500 w-[60%]" />
                        </div>
                      </div>
                    </div>
                  </Card>

                  <Card className="space-y-3">
                    <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
                      Speaking Pacing & Disfluencies
                    </h3>
                    <div className="flex items-center justify-around py-4">
                      <div className="text-center">
                        <span className="text-2xl font-bold text-indigo-600 block">142</span>
                        <span className="text-xs text-slate-400">Average WPM (Optimal)</span>
                      </div>
                      <div className="h-8 w-px bg-slate-200 dark:border-slate-800" />
                      <div className="text-center">
                        <span className="text-2xl font-bold text-emerald-600 block">3.2%</span>
                        <span className="text-xs text-slate-400">Filler Ratio (Target &lt; 3%)</span>
                      </div>
                    </div>
                  </Card>
                </div>
              )}
            </div>
          )}

          {/* PAGE 07: GRAMMAR ANALYSIS */}
          {currentPage === 'grammar' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
                    Grammar Analysis Engine
                  </h1>
                  <p className="text-xs text-slate-500 mt-1">
                    Systematic breakdown of structural syntax and grammatical accuracy
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <DataModeSelector
                    mode={getMode('grammar')}
                    onChange={(m) => setMode('grammar', m)}
                    tabLabel="Grammar"
                  />
                  {isDemo('grammar') && <Badge variant="danger" size="md">4 Recurring Patterns</Badge>}
                </div>
              </div>

              {isDemo('grammar') && (
                <DemoModeNotice
                  tabName="Grammar Analysis Engine"
                  onSwitchReal={() => setMode('grammar', 'REAL')}
                />
              )}

              {!isDemo('grammar') ? (
                <Card className="p-8 text-center space-y-4">
                  <EmptyState
                    icon={<FileText className="w-8 h-8 text-indigo-500" />}
                    title="No grammar issues recorded"
                    description="You are in REAL VERSION mode. Once meeting audio is transcribed and evaluated, grammatical structural inaccuracies and explanations will appear here."
                    actionLabel="Switch to Demo Version"
                    onAction={() => setMode('grammar', 'DEMO')}
                  />
                </Card>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {DEMO_MISTAKES.map((m) => (
                    <GrammarErrorCard
                      key={m.id}
                      originalSentence={m.original}
                      correctedSentence={m.corrected}
                      errorCategory={m.category}
                      severity={m.severity}
                      explanation={m.explanation}
                      timestamp={m.timestamp}
                      onPlayAudio={() => setIsPlayingAudio(true)}
                      onAddToPractice={() => toggleSaveMistake(m.id)}
                      isSaved={savedMistakes.includes(m.id)}
                    />
                  ))}
                </div>
              )}
            </div>
          )}

          {/* PAGE 08: VOCABULARY ANALYSIS */}
          {currentPage === 'vocabulary' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
                    Vocabulary & Lexical Resource
                  </h1>
                  <p className="text-xs text-slate-500 mt-1">
                    Replacing colloquial repetition with executive business English
                  </p>
                </div>
                <DataModeSelector
                  mode={getMode('vocabulary')}
                  onChange={(m) => setMode('vocabulary', m)}
                  tabLabel="Vocabulary"
                />
              </div>

              {isDemo('vocabulary') && (
                <DemoModeNotice
                  tabName="Vocabulary & Lexical Resource"
                  onSwitchReal={() => setMode('vocabulary', 'REAL')}
                />
              )}

              {!isDemo('vocabulary') ? (
                <Card className="p-8 text-center space-y-4">
                  <EmptyState
                    icon={<Languages className="w-8 h-8 text-indigo-500" />}
                    title="No vocabulary suggestions yet"
                    description="You are in REAL VERSION mode. Executive vocabulary upgrades, word repetition counts, and lexical diversity metrics appear after meeting analysis."
                    actionLabel="Switch to Demo Version"
                    onAction={() => setMode('vocabulary', 'DEMO')}
                  />
                </Card>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {DEMO_VOCABULARY_SUGGESTIONS.map((v, i) => (
                    <Card key={i} className="space-y-2">
                      <Badge variant="primary" size="sm">{v.context}</Badge>
                      <p className="text-xs text-rose-500 line-through">Spoken: "{v.original}"</p>
                      <p className="text-sm font-bold text-emerald-600 dark:text-emerald-400">
                        Recommended: "{v.suggested}"
                      </p>
                      <p className="text-xs text-slate-500 italic mt-2">{v.example}</p>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* PAGE 09: FLUENCY */}
          {currentPage === 'fluency' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
                    Speaking Fluency & Temporal Dynamics
                  </h1>
                  <p className="text-xs text-slate-500 mt-1">
                    Speech-to-pause ratios, pause histograms, and filler disfluency density
                  </p>
                </div>
                <DataModeSelector
                  mode={getMode('fluency')}
                  onChange={(m) => setMode('fluency', m)}
                  tabLabel="Fluency"
                />
              </div>

              {isDemo('fluency') && (
                <DemoModeNotice
                  tabName="Speaking Fluency & Temporal Dynamics"
                  onSwitchReal={() => setMode('fluency', 'REAL')}
                />
              )}

              {!isDemo('fluency') ? (
                <Card className="p-8 text-center space-y-4">
                  <EmptyState
                    icon={<Clock className="w-8 h-8 text-indigo-500" />}
                    title="No fluency metrics recorded"
                    description="You are in REAL VERSION mode. Speaking pace (WPM), speech-to-pause ratios, and filler word density are calculated from meeting audio streams."
                    actionLabel="Switch to Demo Version"
                    onAction={() => setMode('fluency', 'DEMO')}
                  />
                </Card>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Card className="text-center p-6">
                    <span className="text-3xl font-bold text-indigo-600 block">142</span>
                    <span className="text-xs font-semibold text-slate-700 dark:text-slate-300 mt-1 block">Words Per Minute</span>
                    <p className="text-[11px] text-slate-400 mt-2">Professional baseline: 130–160 WPM</p>
                  </Card>
                  <Card className="text-center p-6">
                    <span className="text-3xl font-bold text-amber-500 block">1.8s</span>
                    <span className="text-xs font-semibold text-slate-700 dark:text-slate-300 mt-1 block">Mean Pause Duration</span>
                    <p className="text-[11px] text-slate-400 mt-2">Zero excessive cognitive blocks (&gt; 3.0s)</p>
                  </Card>
                  <Card className="text-center p-6">
                    <span className="text-3xl font-bold text-emerald-500 block">3.2%</span>
                    <span className="text-xs font-semibold text-slate-700 dark:text-slate-300 mt-1 block">Filler Density Ratio</span>
                    <p className="text-[11px] text-slate-400 mt-2">Target threshold: &lt; 3.0%</p>
                  </Card>
                </div>
              )}
            </div>
          )}

          {/* PAGE 10: PRONUNCIATION */}
          {currentPage === 'pronunciation' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
                    Pronunciation & Phonetics
                  </h1>
                  <p className="text-xs text-slate-500 mt-1">
                    Acoustic spectrogram analysis, phoneme alignment, and prosodic intonation
                  </p>
                </div>
                <DataModeSelector
                  mode={getMode('pronunciation')}
                  onChange={(m) => setMode('pronunciation', m)}
                  tabLabel="Pronunciation"
                />
              </div>

              {isDemo('pronunciation') && (
                <DemoModeNotice
                  tabName="Pronunciation Analysis"
                  onSwitchReal={() => setMode('pronunciation', 'REAL')}
                />
              )}

              {!isDemo('pronunciation') ? (
                <Card className="p-8 text-center space-y-4">
                  <EmptyState
                    icon={<Mic className="w-8 h-8 text-indigo-500" />}
                    title="No pronunciation assessments yet"
                    description="You are in REAL VERSION mode. Phoneme alignment, word stress detection, and pitch intonation are computed using audio spectrogram analysis."
                    actionLabel="Switch to Demo Version"
                    onAction={() => setMode('pronunciation', 'DEMO')}
                  />
                </Card>
              ) : (
                <>
                  <div className="p-4 rounded-xl bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-900 text-xs text-indigo-800 dark:text-indigo-300">
                    <strong>Acoustic Model Assessment:</strong> Pronunciation evaluation is grounded in raw audio spectrograms. Accents are never penalized if speech intelligibility is clear.
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Card className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-bold text-slate-900 dark:text-white">Word Stress: Development</span>
                        <Badge variant="success" size="sm">Stress Correct</Badge>
                      </div>
                      <p className="text-xs font-mono text-slate-500">Target IPA: /dɪˈvel.əp.mənt/</p>
                      <p className="text-xs text-slate-600 dark:text-slate-300">
                        Syllable stress placed accurately on the second syllable "VEL".
                      </p>
                    </Card>

                    <Card className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-bold text-slate-900 dark:text-white">Phoneme: /θ/ vs /s/</span>
                        <Badge variant="warning" size="sm">Minor Lisp</Badge>
                      </div>
                      <p className="text-xs font-mono text-slate-500">Word: "Methodology" /ˌmeθ.əˈdɒl.ə.dʒi/</p>
                      <p className="text-xs text-slate-600 dark:text-slate-300">
                        Slight dental fricative flattening detected at timestamp 00:14:22.
                      </p>
                    </Card>
                  </div>
                </>
              )}
            </div>
          )}

          {/* PAGE 11: IELTS PRACTICE */}
          {currentPage === 'ielts-practice' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
                    IELTS-Style Speaking Practice Assessment
                  </h1>
                  <p className="text-xs text-slate-500 mt-1">
                    Formative benchmarking across fluency, lexical resource, grammar, and pronunciation
                  </p>
                </div>
                <DataModeSelector
                  mode={getMode('ielts-practice')}
                  onChange={(m) => setMode('ielts-practice', m)}
                  tabLabel="IELTS Practice"
                />
              </div>

              {isDemo('ielts-practice') && (
                <DemoModeNotice
                  tabName="IELTS Practice Assessment"
                  onSwitchReal={() => setMode('ielts-practice', 'REAL')}
                />
              )}

              {!isDemo('ielts-practice') ? (
                <Card className="p-8 text-center space-y-4">
                  <EmptyState
                    icon={<Award className="w-8 h-8 text-indigo-500" />}
                    title="No IELTS-style estimate available"
                    description="You are in REAL VERSION mode. Educational practice band scores across Fluency, Lexical Resource, Grammar, and Pronunciation will calculate after your first meeting session."
                    actionLabel="Switch to Demo Version"
                    onAction={() => setMode('ielts-practice', 'DEMO')}
                  />
                </Card>
              ) : (
                <>
                  <div className="p-3.5 rounded-xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900 text-xs text-amber-800 dark:text-amber-300 flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 shrink-0" />
                    <span>
                      <strong>Regulatory Notice:</strong> This evaluation is an AI-assisted estimate designed for self-improvement and is neither affiliated with nor endorsed by IELTS™, British Council, IDP, or Cambridge English.
                    </span>
                  </div>

                  <div className="flex flex-col md:flex-row items-center gap-6 bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800">
                    <div className="text-center">
                      <span className="text-5xl font-black text-indigo-600 dark:text-indigo-400 block tabular-nums">
                        7.5
                      </span>
                      <span className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mt-1 block">
                        Estimated Band Score
                      </span>
                      <Badge variant="success" size="sm" className="mt-2">Good / Very Good User</Badge>
                    </div>

                    <div className="flex-1 grid grid-cols-1 sm:grid-cols-2 gap-3 w-full">
                      <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60">
                        <span className="text-xs font-bold block text-slate-800 dark:text-slate-200">Fluency & Coherence</span>
                        <span className="text-sm font-bold text-indigo-600">Band 7.5</span>
                        <p className="text-[11px] text-slate-500 mt-0.5">Spoke at length without noticeable effort.</p>
                      </div>
                      <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60">
                        <span className="text-xs font-bold block text-slate-800 dark:text-slate-200">Lexical Resource</span>
                        <span className="text-sm font-bold text-indigo-600">Band 7.0</span>
                        <p className="text-[11px] text-slate-500 mt-0.5">Wide vocabulary with appropriate technical jargon.</p>
                      </div>
                      <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60">
                        <span className="text-xs font-bold block text-slate-800 dark:text-slate-200">Grammatical Accuracy</span>
                        <span className="text-sm font-bold text-indigo-600">Band 7.5</span>
                        <p className="text-[11px] text-slate-500 mt-0.5">Frequent error-free complex sentences.</p>
                      </div>
                      <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60">
                        <span className="text-xs font-bold block text-slate-800 dark:text-slate-200">Pronunciation</span>
                        <span className="text-sm font-bold text-indigo-600">Band 8.0</span>
                        <p className="text-[11px] text-slate-500 mt-0.5">Clear and easy to understand throughout.</p>
                      </div>
                    </div>
                  </div>
                </>
              )}
            </div>
          )}

          {/* PAGE 12: LEARNING CENTER */}
          {currentPage === 'learning-center' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
                    Personalized Learning Center
                  </h1>
                  <p className="text-xs text-slate-500 mt-1">
                    Daily 3-minute micro-drills generated dynamically from your recent meeting mistakes
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <DataModeSelector
                    mode={getMode('learning-center')}
                    onChange={(m) => setMode('learning-center', m)}
                    tabLabel="Learning Center"
                  />
                  <Badge variant="primary" size="md">{isDemo('learning-center') ? 'Streak: 7 Days 🔥' : 'Streak: 1 Day'}</Badge>
                </div>
              </div>

              {isDemo('learning-center') && (
                <DemoModeNotice
                  tabName="Personalized Learning Center"
                  onSwitchReal={() => setMode('learning-center', 'REAL')}
                />
              )}

              {/* Today's Practice Challenge */}
              <Card className="space-y-4 border-2 border-indigo-500/30">
                <div className="flex items-center justify-between">
                  <Badge variant="primary" size="sm">Today's Focus: Prepositions & Conditionals</Badge>
                  <span className="text-xs text-slate-400">Estimated: 3 mins</span>
                </div>

                <div className="space-y-3">
                  <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
                    Question 1 of 3: Choose the correct business English phrasing:
                  </h3>
                  <p className="text-xs text-slate-600 dark:text-slate-300 italic bg-slate-50 dark:bg-slate-800 p-3 rounded-lg">
                    "During sprint planning, I promised I would _______ the new audio architecture."
                  </p>

                  <div className="space-y-2">
                    {[
                      { idx: 0, text: 'explain you', correct: false },
                      { idx: 1, text: 'explain to you', correct: true },
                      { idx: 2, text: 'explain about', correct: false },
                    ].map((opt) => (
                      <button
                        key={opt.idx}
                        onClick={() => setPracticeAnswered(opt.idx)}
                        className={`w-full p-3 rounded-xl border text-xs font-medium text-left flex items-center justify-between transition-colors ${
                          practiceAnswered === opt.idx
                            ? opt.correct
                              ? 'bg-emerald-50 border-emerald-500 text-emerald-900 dark:bg-emerald-950/40 dark:text-emerald-200'
                              : 'bg-rose-50 border-rose-500 text-rose-900 dark:bg-rose-950/40 dark:text-rose-200'
                            : 'border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/60'
                        }`}
                      >
                        <span>{opt.text}</span>
                        {practiceAnswered === opt.idx && (
                          opt.correct ? <Check className="w-4 h-4 text-emerald-600" /> : <X className="w-4 h-4 text-rose-600" />
                        )}
                      </button>
                    ))}
                  </div>

                  {practiceAnswered !== null && (
                    <div className="p-3 rounded-lg bg-indigo-50 dark:bg-indigo-950/40 text-xs text-indigo-900 dark:text-indigo-200">
                      <strong>Rule:</strong> The verb "explain" takes a prepositional object ("explain to someone"). Correct choice: <em>explain to you</em>.
                    </div>
                  )}
                </div>
              </Card>
            </div>
          )}

          {/* PAGE 13: MISTAKE HISTORY */}
          {currentPage === 'mistakes' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
                    Saved Mistake History
                  </h1>
                  <p className="text-xs text-slate-500 mt-1">
                    Your personal flashcard bank compiled from meeting analysis
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <DataModeSelector
                    mode={getMode('mistakes')}
                    onChange={(m) => setMode('mistakes', m)}
                    tabLabel="Mistakes"
                  />
                  <Badge variant="neutral" size="md">
                    {isDemo('mistakes') ? savedMistakes.length : realSavedMistakes.length} Saved Items
                  </Badge>
                </div>
              </div>

              {isDemo('mistakes') && (
                <DemoModeNotice
                  tabName="Saved Mistake History"
                  onSwitchReal={() => setMode('mistakes', 'REAL')}
                />
              )}

              {!isDemo('mistakes') && realSavedMistakes.length === 0 ? (
                <Card className="p-8 text-center space-y-4">
                  <EmptyState
                    icon={<BookOpen className="w-8 h-8 text-indigo-500" />}
                    title="Your mistakes notebook is empty"
                    description="You are in REAL VERSION mode. As you review meeting transcripts and speech reports, bookmark grammar, pronunciation, or vocabulary corrections to practice them in this notebook."
                    actionLabel="Switch to Demo Version"
                    onAction={() => setMode('mistakes', 'DEMO')}
                  />
                </Card>
              ) : (
                <div className="space-y-3">
                  {(isDemo('mistakes') ? DEMO_MISTAKES.filter((m) => savedMistakes.includes(m.id)) : []).map((m) => (
                    <Card key={m.id} className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <Badge variant="danger" size="sm">{m.category}</Badge>
                          <span className="text-xs text-slate-400">{m.timestamp}</span>
                        </div>
                        <p className="text-xs text-rose-600 line-through">"{m.original}"</p>
                        <p className="text-sm font-semibold text-emerald-600 mt-0.5">"{m.corrected}"</p>
                        <p className="text-[11px] text-slate-500 mt-1">{m.explanation}</p>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => toggleSaveMistake(m.id)}
                      >
                        Remove from Deck
                      </Button>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* PAGE 14: IMPROVEMENT PLAN */}
          {currentPage === 'improvement-plan' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
                    4-Week Linguistic Mastery Plan
                  </h1>
                  <p className="text-xs text-slate-500 mt-1">
                    Structured personalized milestones tailored to your workplace speaking data
                  </p>
                </div>
                <DataModeSelector
                  mode={getMode('improvement-plan')}
                  onChange={(m) => setMode('improvement-plan', m)}
                  tabLabel="Improvement Plan"
                />
              </div>

              {isDemo('improvement-plan') && (
                <DemoModeNotice
                  tabName="Linguistic Mastery Plan"
                  onSwitchReal={() => setMode('improvement-plan', 'REAL')}
                />
              )}

              {!isDemo('improvement-plan') ? (
                <Card className="p-8 text-center space-y-4">
                  <EmptyState
                    icon={<Sparkles className="w-8 h-8 text-indigo-500" />}
                    title="No personalized plan generated yet"
                    description="You are in REAL VERSION mode. Your 4-week linguistic mastery plan will be automatically compiled by Gemini AI after your first meeting is analyzed."
                    actionLabel="Switch to Demo Version"
                    onAction={() => setMode('improvement-plan', 'DEMO')}
                  />
                </Card>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Card className="space-y-2 border-l-4 border-l-emerald-500">
                    <Badge variant="success" size="sm">Week 1: Completed</Badge>
                    <h3 className="text-sm font-bold text-slate-900 dark:text-white">Preposition Grounding</h3>
                    <p className="text-xs text-slate-500">Eliminate missing "to" in verbs of reporting and explanation.</p>
                  </Card>

                  <Card className="space-y-2 border-l-4 border-l-indigo-500">
                    <Badge variant="primary" size="sm">Week 2: In Progress</Badge>
                    <h3 className="text-sm font-bold text-slate-900 dark:text-white">Conditional Clauses</h3>
                    <p className="text-xs text-slate-500">Master first and second conditional structures during deadline estimates.</p>
                  </Card>

                  <Card className="space-y-2 border-l-4 border-l-slate-300">
                    <Badge variant="neutral" size="sm">Week 3: Upcoming</Badge>
                    <h3 className="text-sm font-bold text-slate-900 dark:text-white">Executive Paraphrasing</h3>
                    <p className="text-xs text-slate-500">Replacing conversational filler words with diplomatic transition cues.</p>
                  </Card>

                  <Card className="space-y-2 border-l-4 border-l-slate-300">
                    <Badge variant="neutral" size="sm">Week 4: Upcoming</Badge>
                    <h3 className="text-sm font-bold text-slate-900 dark:text-white">High-Stakes Negotiation</h3>
                    <p className="text-xs text-slate-500">Simulating pushback defense and C-level sprint presentations.</p>
                  </Card>
                </div>
              )}
            </div>
          )}

          {/* PAGE 15: TEAM ANALYTICS */}
          {currentPage === 'team-analytics' && (
            <div className="space-y-6">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
                    Team Communication Analytics
                  </h1>
                  <p className="text-xs text-slate-500 mt-1">
                    Department: Engineering Cohort • 4 Members Active • Privacy-Preserved Aggregate View
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <DataModeSelector
                    mode={getMode('team-analytics')}
                    onChange={(m) => setMode('team-analytics', m)}
                    tabLabel="Team Analytics"
                  />
                  <Button variant="outline" size="sm">
                    Export Team Report
                  </Button>
                </div>
              </div>

              {isDemo('team-analytics') && (
                <DemoModeNotice
                  tabName="Team Communication Analytics"
                  onSwitchReal={() => setMode('team-analytics', 'REAL')}
                />
              )}

              {!isDemo('team-analytics') ? (
                <Card className="p-8 text-center space-y-4">
                  <EmptyState
                    icon={<Users className="w-8 h-8 text-indigo-500" />}
                    title="No team meeting data aggregated"
                    description="You are in REAL VERSION mode. Connect your organization workspace to view team-wide speaking pace, aggregate filler word density, and cross-department communication benchmarks."
                    actionLabel="Switch to Demo Version"
                    onAction={() => setMode('team-analytics', 'DEMO')}
                  />
                </Card>
              ) : (
                <>
                  {/* Team Metrics */}
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <StatCard
                      title="Total Team Meetings"
                      value={DEMO_TEAM_ANALYTICS.totalTeamMeetings}
                      supportingText={DEMO_TEAM_ANALYTICS.totalSpeakingHours + " speaking time"}
                      icon={<Video className="w-4 h-4 text-indigo-600" />}
                    />
                    <StatCard
                      title="Team Average Pacing"
                      value={DEMO_TEAM_ANALYTICS.averageSpeakingPace + " WPM"}
                      supportingText="Optimal professional rhythm"
                      icon={<Clock className="w-4 h-4 text-emerald-600" />}
                    />
                    <StatCard
                      title="Team Filler Word Rate"
                      value={DEMO_TEAM_ANALYTICS.averageFillerDensity + "%"}
                      supportingText="3.8% mean density across engineers"
                      icon={<Sparkles className="w-4 h-4 text-amber-500" />}
                    />
                  </div>

                  {/* Top Team Bottlenecks */}
                  <Card className="space-y-4">
                    <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
                      Widespread Team Language Bottlenecks
                    </h3>
                    <div className="space-y-3">
                      {DEMO_TEAM_ANALYTICS.topMistakeCategories.map((c, i) => (
                        <div key={i} className="space-y-1">
                          <div className="flex justify-between text-xs font-medium">
                            <span className="text-slate-700 dark:text-slate-300">{c.category}</span>
                            <span className="text-slate-900 dark:text-slate-100 font-bold">{c.percentage}% of all team flaws ({c.count} occurrences)</span>
                          </div>
                          <div className="w-full h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                            <div className="h-full bg-indigo-600 rounded-full" style={{ width: `${c.percentage}%` }} />
                          </div>
                        </div>
                      ))}
                    </div>
                  </Card>

                  {/* Authorized Member Comparison Table */}
                  <Card padding="none">
                    <div className="p-4 border-b border-slate-200 dark:border-slate-800 font-semibold text-xs">
                      Authorized Team Member Aggregates
                    </div>
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs">
                        <thead>
                          <tr className="border-b border-slate-200 dark:border-slate-800 text-[11px] font-semibold text-slate-400 uppercase bg-slate-50/50 dark:bg-slate-900/50">
                            <th className="py-2.5 px-4">Member</th>
                            <th className="py-2.5 px-4">Role</th>
                            <th className="py-2.5 px-4">Meetings</th>
                            <th className="py-2.5 px-4">Speaking Pace</th>
                            <th className="py-2.5 px-4">Filler Rate</th>
                            <th className="py-2.5 px-4">Proficiency Score</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                          {DEMO_TEAM_ANALYTICS.members.map((m, i) => (
                            <tr key={i} className="hover:bg-slate-50/80 dark:hover:bg-slate-800/40">
                              <td className="py-3 px-4 font-semibold text-slate-900 dark:text-slate-100">{m.name}</td>
                              <td className="py-3 px-4 text-slate-500">{m.role}</td>
                              <td className="py-3 px-4 text-slate-700 dark:text-slate-300">{m.meetings}</td>
                              <td className="py-3 px-4 text-slate-700 dark:text-slate-300">{m.pace} WPM</td>
                              <td className="py-3 px-4 text-slate-700 dark:text-slate-300">{m.fillerRate}</td>
                              <td className="py-3 px-4">
                                <Badge variant="success" size="sm">{m.score} / 100</Badge>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </Card>
                </>
              )}
            </div>
          )}

          {/* PAGE 15B: TEAM & WORKSPACE SEATS */}
          {currentPage === 'team-settings' && (
            <div className="space-y-6">
              <TeamSettings />
            </div>
          )}

          {/* PAGE 16: INTEGRATIONS */}
          {currentPage === 'integrations' && (
            <div className="space-y-6">
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
                  Meeting Integrations & Chrome Extension
                </h1>
                <p className="text-xs text-slate-500 mt-1">
                  Manage connection status with browser meeting platforms
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card className="space-y-3 border-2 border-indigo-500/40">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-sm text-slate-900 dark:text-white">Chrome Extension Side Panel</span>
                    <Badge variant="success" size="sm">Active (v1.0.2)</Badge>
                  </div>
                  <p className="text-xs text-slate-500 leading-relaxed">
                    Embedded side panel for Google Meet, Zoom Web, and Microsoft Teams. Streams audio safely without room bots.
                  </p>
                  <Button size="sm" variant="outline">
                    Re-pair Session Token
                  </Button>
                </Card>

                <Card className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <PlatformIcon platform="google-meet" size="lg" />
                      <div>
                        <span className="font-bold text-sm text-slate-900 dark:text-white block">Google Meet Web</span>
                        <span className="text-[11px] text-slate-400 font-mono">https://meet.google.com/*</span>
                      </div>
                    </div>
                    <Badge variant="success" size="sm">Full Support</Badge>
                  </div>
                  <p className="text-xs text-slate-500 leading-relaxed">
                    Automatic DOM discovery, participant roster scraping, and in-call recording arming with live captions.
                  </p>
                </Card>

                <Card className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <PlatformIcon platform="zoom" size="lg" />
                      <div>
                        <span className="font-bold text-sm text-slate-900 dark:text-white block">Zoom Web Client</span>
                        <span className="text-[11px] text-slate-400 font-mono">https://app.zoom.us/wc/*</span>
                      </div>
                    </div>
                    <Badge variant="primary" size="sm">Compatibility Ready</Badge>
                  </div>
                  <p className="text-xs text-slate-500 leading-relaxed">
                    Browser-based client capture via chrome.tabCapture stream and AI real-time whisper transcription.
                  </p>
                </Card>

                <Card className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <PlatformIcon platform="teams" size="lg" />
                      <div>
                        <span className="font-bold text-sm text-slate-900 dark:text-white block">Microsoft Teams Web</span>
                        <span className="text-[11px] text-slate-400 font-mono">https://teams.microsoft.com/*</span>
                      </div>
                    </div>
                    <Badge variant="primary" size="sm">Compatibility Ready</Badge>
                  </div>
                  <p className="text-xs text-slate-500 leading-relaxed">
                    Browser-based client capture for Teams meetings in Chrome with speaker diarization.
                  </p>
                </Card>
              </div>
            </div>
          )}

          {/* PAGE 16.5: CHROME EXTENSION DOWNLOAD CENTER */}
          {currentPage === 'chrome-extension' && (
            <ChromeExtensionPage />
          )}

          {/* PAGE 17: BILLING & USAGE */}
          {currentPage === 'billing' && (
            <div className="space-y-6">
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
                  Billing, Subscriptions & Metering
                </h1>
                <p className="text-xs text-slate-500 mt-1">
                  Multi-dimensional usage metering across meeting minutes, audio compute, and AI tokens
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card className="space-y-2">
                  <span className="text-xs text-slate-400 uppercase font-bold tracking-wider">Current Plan</span>
                  <span className="text-xl font-bold text-indigo-600 block">Enterprise Team</span>
                  <p className="text-xs text-slate-500">25 Provisioned Seats • Renewal: Dec 1, 2026</p>
                </Card>
                <Card className="space-y-2">
                  <span className="text-xs text-slate-400 uppercase font-bold tracking-wider">Meeting Minutes</span>
                  <span className="text-xl font-bold text-slate-900 dark:text-white block">320 / 1,000 mins</span>
                  <div className="w-full h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-indigo-600 w-[32%]" />
                  </div>
                </Card>
                <Card className="space-y-2">
                  <span className="text-xs text-slate-400 uppercase font-bold tracking-wider">AI Token Capacity</span>
                  <span className="text-xl font-bold text-slate-900 dark:text-white block">2.4M / 10M tokens</span>
                  <div className="w-full h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-emerald-500 w-[24%]" />
                  </div>
                </Card>
              </div>
            </div>
          )}

          {/* PAGE 18: PROFILE SETTINGS */}
          {currentPage === 'profile-settings' && (
            <div className="space-y-6 max-w-xl">
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
                  Profile Settings
                </h1>
                <p className="text-xs text-slate-500 mt-1">
                  Manage your personal professional credentials and language preferences
                </p>
              </div>

              <Card className="space-y-4">
                <Input label="Full Name" defaultValue="Priya Sharma" />
                <Input label="Work Email" defaultValue="priya.sharma@acme.com" disabled helperText="Managed by Acme Corp enterprise SSO" />
                <Input label="Primary Native Language" defaultValue="Hindi" helperText="Helps calibrate phoneme phonetic predictions" />
                <Button size="sm">Save Changes</Button>
              </Card>
            </div>
          )}

          {/* PAGE 19: PRIVACY SETTINGS */}
          {currentPage === 'privacy-settings' && (
            <div className="space-y-6 max-w-2xl">
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
                  Privacy & Audio Retention Policies
                </h1>
                <p className="text-xs text-slate-500 mt-1">
                  Enforce ephemeral audio retention and complete GDPR right to be forgotten
                </p>
              </div>

              <Card className="space-y-4">
                <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
                  Audio Storage Retention Window
                </h3>
                <p className="text-xs text-slate-500">
                  Select how long raw audio files are stored in encrypted cloud buckets before automated permanent purging:
                </p>
                <div className="space-y-2 text-xs">
                  <label className="flex items-center gap-2 p-2.5 rounded-lg border border-slate-200 dark:border-slate-800 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800/60">
                    <input type="radio" name="retention" defaultChecked />
                    <span><strong>7 Days (Recommended):</strong> Audio purged after 7 days; reports preserved indefinitely.</span>
                  </label>
                  <label className="flex items-center gap-2 p-2.5 rounded-lg border border-slate-200 dark:border-slate-800 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800/60">
                    <input type="radio" name="retention" />
                    <span><strong>Ephemeral:</strong> Purge audio immediately after report generation completes.</span>
                  </label>
                  <label className="flex items-center gap-2 p-2.5 rounded-lg border border-slate-200 dark:border-slate-800 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800/60">
                    <input type="radio" name="retention" />
                    <span><strong>30 Days:</strong> Standard monthly review window.</span>
                  </label>
                </div>

                <div className="pt-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
                  <div>
                    <h4 className="text-xs font-bold text-rose-600">Delete All Account Data</h4>
                    <p className="text-[11px] text-slate-400">Permanently erase all recordings, transcripts, and scores.</p>
                  </div>
                  <Button variant="destructive" size="sm" onClick={() => setShowDeleteModal(true)}>
                    Purge All Data
                  </Button>
                </div>
              </Card>
            </div>
          )}

          {/* PAGE 20: SECURITY SETTINGS */}
          {currentPage === 'security-settings' && (
            <div className="space-y-6 max-w-xl">
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
                  Security & Active Sessions
                </h1>
                <p className="text-xs text-slate-500 mt-1">
                  Manage active browser tokens and authentication safeguards
                </p>
              </div>

              <Card className="space-y-3">
                <div className="flex items-center justify-between text-xs">
                  <div>
                    <span className="font-semibold block text-slate-800 dark:text-slate-200">Chrome Extension Session</span>
                    <span className="text-slate-400">Chrome on Windows • Last active 4 mins ago</span>
                  </div>
                  <Badge variant="success" size="sm">Active</Badge>
                </div>
                <Button variant="outline" size="sm">
                  Revoke All Tokens
                </Button>
              </Card>
            </div>
          )}

          {/* PAGE 21: NOTIFICATION SETTINGS */}
          {currentPage === 'notification-settings' && (
            <div className="space-y-6 max-w-xl">
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
                  Notification Preferences
                </h1>
                <p className="text-xs text-slate-500 mt-1">
                  Configure post-meeting email alerts and daily micro-practice reminders
                </p>
              </div>

              <Card className="space-y-3 text-xs">
                <label className="flex items-center justify-between p-2 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 cursor-pointer">
                  <span>Send report summary email immediately after meeting</span>
                  <input type="checkbox" defaultChecked />
                </label>
                <label className="flex items-center justify-between p-2 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 cursor-pointer">
                  <span>Daily 3-minute practice drill push reminder (09:00 AM)</span>
                  <input type="checkbox" defaultChecked />
                </label>
              </Card>
            </div>
          )}
        </main>
      </div>

      {/* Confirmation Dialog for Destructive Actions */}
      <ConfirmationDialog
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        onConfirm={() => {
          setShowDeleteModal(false);
          alert('Demo data purge simulated successfully.');
        }}
        title="Permanently Purge All Data?"
        message="This will immediately delete all your meeting recordings, transcripts, and AI coaching scores. This action cannot be reversed."
        confirmLabel="Purge Everything"
        isDestructive
      />
    </div>
  );
};

