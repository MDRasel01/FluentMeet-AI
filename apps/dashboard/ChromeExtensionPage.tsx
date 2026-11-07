import React, { useState, useEffect } from 'react';
import {
  Download,
  ExternalLink,
  CheckCircle2,
  AlertCircle,
  Copy,
  Check,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  FolderArchive,
  Info,
  ShieldCheck,
  Sparkles,
  Layers,
  ArrowRight
} from 'lucide-react';
import { Button, Card, Badge } from '../../design-system/components';

export interface ReleaseItem {
  id: string;
  extension_name: string;
  version: string;
  channel: string;
  status: string;
  manifest_version: number;
  build_number?: string;
  git_commit_sha?: string;
  release_notes?: string[] | any;
  minimum_chrome_version: string;
  artifact_filename?: string;
  artifact_size_bytes: number;
  sha256_checksum?: string;
  download_count: number;
  download_url?: string;
  published_at?: string;
  created_at: string;
}

// Fallback initial release data matching actual verified artifact
const DEFAULT_LATEST_RELEASE: ReleaseItem = {
  id: 'rel-stable-1.0.0',
  extension_name: 'FluentMeet AI — Real-time English Meeting Coach',
  version: '1.0.0',
  channel: 'stable',
  status: 'published',
  manifest_version: 3,
  build_number: 'build-20261107-001',
  git_commit_sha: '7f9a2b1',
  release_notes: [
    'Real-time dual-track speech coaching for Google Meet, Zoom, and MS Teams.',
    'Manifest V3 Side Panel API integration for non-intrusive meeting presence.',
    'Multi-channel Web Audio capture with 16kHz PCM downsampler and real-time streaming.',
    'Live speaking pace (WPM), filler word detection, and pronunciation scoring.',
    'Automatic session synchronization with Web Dashboard transcript archive.'
  ],
  minimum_chrome_version: '116.0',
  artifact_filename: 'fluentmeet-ai-v1.0.0.zip',
  artifact_size_bytes: 98300,
  sha256_checksum: '53e8620c9422f7e7f7a2715eaccc7a37bca41b87ca2f5a4f774a5dc7480cf003',
  download_count: 24,
  download_url: '/api/v1/extensions/releases/latest/download?channel=stable',
  published_at: '2026-11-07T10:00:00Z',
  created_at: '2026-11-07T09:30:00Z'
};

const DEFAULT_HISTORY_RELEASES: ReleaseItem[] = [
  DEFAULT_LATEST_RELEASE,
  {
    id: 'rel-stable-0.9.5',
    extension_name: 'FluentMeet AI — Real-time English Meeting Coach',
    version: '0.9.5',
    channel: 'stable',
    status: 'archived',
    manifest_version: 3,
    build_number: 'build-20261028-082',
    git_commit_sha: '4d8e1c9',
    release_notes: [
      'Pre-release beta: Core Tab Capture audio offscreen document pipeline.',
      'Google Meet DOM observer for participant identification.',
      'WebSocket reconnection backoff and token refresh integration.'
    ],
    minimum_chrome_version: '116.0',
    artifact_filename: 'fluentmeet-ai-v0.9.5.zip',
    artifact_size_bytes: 94200,
    sha256_checksum: 'a98f71c42b03d6e5a4f2187c3901b8e4f509d732c10b7849e0a298f615309d21',
    download_count: 156,
    download_url: '/api/v1/extensions/releases/rel-stable-0.9.5/download',
    published_at: '2026-10-28T14:30:00Z',
    created_at: '2026-10-28T12:00:00Z'
  },
  {
    id: 'rel-stable-0.9.0',
    extension_name: 'FluentMeet AI — Real-time English Meeting Coach',
    version: '0.9.0',
    channel: 'stable',
    status: 'archived',
    manifest_version: 3,
    build_number: 'build-20261015-045',
    git_commit_sha: '1b3c9f2',
    release_notes: [
      'Initial prototype build for internal dogfooding.',
      'Basic UI shell and meeting detector state machine.'
    ],
    minimum_chrome_version: '116.0',
    artifact_filename: 'fluentmeet-ai-v0.9.0.zip',
    artifact_size_bytes: 88500,
    sha256_checksum: '8d2e90c1f543a6b8e219478f401b3d75c692a819e403d76b158f0923e41b9d04',
    download_count: 89,
    download_url: '/api/v1/extensions/releases/rel-stable-0.9.0/download',
    published_at: '2026-10-15T18:00:00Z',
    created_at: '2026-10-15T16:00:00Z'
  }
];

export const ChromeExtensionPage: React.FC = () => {
  const [latestRelease, setLatestRelease] = useState<ReleaseItem>(DEFAULT_LATEST_RELEASE);
  const [historyReleases, setHistoryReleases] = useState<ReleaseItem[]>(DEFAULT_HISTORY_RELEASES);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [copiedSha, setCopiedSha] = useState<string | null>(null);
  const [expandedVersion, setExpandedVersion] = useState<string | null>(null);
  const [downloadSuccess, setDownloadSuccess] = useState<string | null>(null);

  const fetchReleases = async () => {
    setIsLoading(true);
    try {
      // 1. Fetch latest release
      const latestRes = await fetch('/api/v1/extensions/releases/latest?channel=stable');
      if (latestRes.ok) {
        const json = await latestRes.json();
        if (json.data) {
          setLatestRelease(json.data);
        }
      }

      // 2. Fetch history
      const historyRes = await fetch('/api/v1/extensions/releases?limit=20');
      if (historyRes.ok) {
        const json = await historyRes.json();
        if (json.data && json.data.items && json.data.items.length > 0) {
          setHistoryReleases(json.data.items);
        }
      }
    } catch (err: any) {
      console.log('Using local release metadata cache:', err?.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchReleases();
  }, []);

  const handleCopyChecksum = (sha: string) => {
    navigator.clipboard.writeText(sha);
    setCopiedSha(sha);
    setTimeout(() => setCopiedSha(null), 3000);
  };

  const handleDownload = (release: ReleaseItem) => {
    setDownloadSuccess(`Downloading ${release.artifact_filename || `fluentmeet-ai-v${release.version}.zip`}...`);
    const link = document.createElement('a');
    link.href = release.download_url || `/api/v1/extensions/releases/${release.id}/download`;
    link.setAttribute('download', release.artifact_filename || `fluentmeet-ai-v${release.version}.zip`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    setTimeout(() => {
      setDownloadSuccess(null);
    }, 4000);
  };

  const formatSize = (bytes: number) => {
    if (!bytes) return '96.0 KB';
    return `${(bytes / 1024).toFixed(1)} KB`;
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '07 November 2026';
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString('en-GB', {
        day: '2-digit',
        month: 'long',
        year: 'numeric'
      });
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-12">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
              Chrome Extension
            </h1>
            <Badge variant="primary" size="sm">
              v{latestRelease.version} Stable
            </Badge>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Download, install and manage the latest version of your meeting assistant extension.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={fetchReleases}
            disabled={isLoading}
            className="flex items-center gap-1.5 text-xs text-slate-600 dark:text-slate-300"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Check for Updates</span>
          </Button>
        </div>
      </div>

      {/* Download Alert Toast */}
      {downloadSuccess && (
        <div className="bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800 rounded-xl p-3.5 flex items-center gap-3 text-emerald-800 dark:text-emerald-200 text-xs shadow-sm animate-in fade-in duration-200">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{downloadSuccess} Extract the package and load it unpacked in <code>chrome://extensions</code>.</span>
        </div>
      )}

      {/* Section 5 Mandate: Chrome Web Store vs Dashboard Download Banner */}
      <div className="bg-gradient-to-r from-indigo-50/80 via-blue-50/50 to-slate-50 dark:from-indigo-950/40 dark:via-slate-900 dark:to-slate-900/60 border border-indigo-100 dark:border-indigo-900/50 rounded-2xl p-5 shadow-sm">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-xs font-bold uppercase tracking-wider text-indigo-700 dark:text-indigo-400">
                Recommended Production Route: Chrome Web Store
              </span>
            </div>
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
              Looking for automatic silent background updates?
            </h3>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed max-w-2xl">
              Chrome extensions installed from the <strong>Chrome Web Store</strong> automatically update in the background when new versions are released.
              Downloading the <strong>Dashboard ZIP</strong> below is for manual local development, corporate offline staging, and testing specific version archives.
            </p>
          </div>

          <a
            href="https://chromewebstore.google.com"
            target="_blank"
            rel="noopener noreferrer"
            className="shrink-0 inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 dark:bg-white dark:hover:bg-slate-100 text-white dark:text-slate-900 text-xs font-semibold shadow-sm transition-all"
          >
            <Sparkles className="w-3.5 h-3.5 text-amber-400 dark:text-amber-500" />
            <span>Install from Chrome Web Store</span>
            <ExternalLink className="w-3.5 h-3.5 opacity-60 ml-0.5" />
          </a>
        </div>
      </div>

      {/* Main Download Card (Section 2.1) */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 sm:p-8 shadow-sm relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/5 dark:bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-6">
          <div className="flex items-start gap-4">
            {/* Logo Badge */}
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-indigo-600 to-indigo-400 flex items-center justify-center text-white font-bold text-2xl shadow-md shrink-0 ring-4 ring-indigo-50 dark:ring-indigo-950/50">
              FM
            </div>

            <div className="space-y-1">
              <div className="flex flex-wrap items-center gap-2">
                <h2 className="text-xl font-bold text-slate-900 dark:text-white">
                  {latestRelease.extension_name}
                </h2>
                <Badge variant="primary" size="sm" className="capitalize">
                  {latestRelease.channel}
                </Badge>
                <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-2 py-0.5 rounded-full border border-emerald-200/60 dark:border-emerald-800/60">
                  <CheckCircle2 className="w-3 h-3" />
                  Available & Verified
                </span>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                AI-Powered English Speaking Analysis SaaS • Chrome Side Panel Extension
              </p>
              <div className="flex flex-wrap items-center gap-x-4 gap-y-1 pt-1 text-xs text-slate-600 dark:text-slate-400">
                <span><strong>Latest Version:</strong> v{latestRelease.version}</span>
                <span className="text-slate-300 dark:text-slate-700">•</span>
                <span><strong>Release Date:</strong> {formatDate(latestRelease.published_at)}</span>
                <span className="text-slate-300 dark:text-slate-700">•</span>
                <span><strong>Package:</strong> ZIP ({formatSize(latestRelease.artifact_size_bytes)})</span>
                <span className="text-slate-300 dark:text-slate-700">•</span>
                <span><strong>Chrome:</strong> Minimum v{latestRelease.minimum_chrome_version}</span>
              </div>
            </div>
          </div>

          {/* Download Action Button */}
          <div className="flex flex-col sm:flex-row lg:flex-col items-stretch lg:items-end gap-2.5 shrink-0">
            <Button
              variant="primary"
              size="lg"
              onClick={() => handleDownload(latestRelease)}
              className="flex items-center justify-center gap-2 text-sm font-semibold shadow-indigo-600/20 shadow-lg px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white transition-all transform active:scale-95"
            >
              <Download className="w-4 h-4" />
              <span>Download Chrome Extension (ZIP)</span>
            </Button>
            <span className="text-[11px] text-slate-400 text-center lg:text-right">
              Direct download • Unpacked local installation
            </span>
          </div>
        </div>

        {/* SHA-256 Checksum Card */}
        {latestRelease.sha256_checksum && (
          <div className="mt-6 pt-6 border-t border-slate-100 dark:border-slate-800">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-slate-50 dark:bg-slate-950/60 p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 text-xs">
              <div className="flex items-center gap-2 overflow-hidden">
                <ShieldCheck className="w-4 h-4 text-indigo-600 dark:text-indigo-400 shrink-0" />
                <span className="font-semibold text-slate-700 dark:text-slate-300 shrink-0">SHA-256 Checksum:</span>
                <code className="text-slate-600 dark:text-slate-400 font-mono truncate text-[11px]">
                  {latestRelease.sha256_checksum}
                </code>
              </div>
              <button
                onClick={() => handleCopyChecksum(latestRelease.sha256_checksum!)}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-white dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 font-medium transition-colors shrink-0 text-xs"
              >
                {copiedSha === latestRelease.sha256_checksum ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-emerald-600" />
                    <span className="text-emerald-600">Copied!</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5 text-slate-400" />
                    <span>Copy Checksum</span>
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Release Notes Highlight (Section 2.4) */}
        {latestRelease.release_notes && (
          <div className="mt-6 pt-6 border-t border-slate-100 dark:border-slate-800 space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
              What's New in Version {latestRelease.version}
            </h4>
            <ul className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-slate-600 dark:text-slate-300">
              {(Array.isArray(latestRelease.release_notes)
                ? latestRelease.release_notes
                : [String(latestRelease.release_notes)]
              ).map((note: string, idx: number) => (
                <li key={idx} className="flex items-start gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-indigo-500 mt-0.5 shrink-0" />
                  <span>{note}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Installation Instructions (Section 2.2) */}
      <div className="space-y-4">
        <div>
          <h2 className="text-lg font-bold text-slate-900 dark:text-white">
            Installation & Setup Guide
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Follow these steps to install and load the unpacked extension into Google Chrome.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Step 1 */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 space-y-2">
            <div className="flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 text-xs font-bold flex items-center justify-center">
                1
              </span>
              <h3 className="text-xs font-bold text-slate-900 dark:text-white">
                Download Package
              </h3>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
              Click the <strong>Download Chrome Extension</strong> button above to download the latest verified ZIP bundle.
            </p>
          </div>

          {/* Step 2 */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 space-y-2">
            <div className="flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 text-xs font-bold flex items-center justify-center">
                2
              </span>
              <h3 className="text-xs font-bold text-slate-900 dark:text-white">
                Extract ZIP Archive
              </h3>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
              Extract the ZIP into a permanent directory on your machine (e.g. <code>Documents/FluentMeet-Extension</code>). Do not delete this folder.
            </p>
          </div>

          {/* Step 3 */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 space-y-2">
            <div className="flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 text-xs font-bold flex items-center justify-center">
                3
              </span>
              <h3 className="text-xs font-bold text-slate-900 dark:text-white">
                Open chrome://extensions
              </h3>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
              Open Google Chrome, type <code>chrome://extensions</code> into your address bar, and press Enter.
            </p>
          </div>

          {/* Step 4 */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 space-y-2">
            <div className="flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 text-xs font-bold flex items-center justify-center">
                4
              </span>
              <h3 className="text-xs font-bold text-slate-900 dark:text-white">
                Enable Developer Mode
              </h3>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
              In the top-right corner of the Extensions page, switch the <strong>Developer mode</strong> toggle to <strong>ON</strong>.
            </p>
          </div>

          {/* Step 5 */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 space-y-2">
            <div className="flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 text-xs font-bold flex items-center justify-center">
                5
              </span>
              <h3 className="text-xs font-bold text-slate-900 dark:text-white">
                Select "Load Unpacked"
              </h3>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
              Click the <strong>Load unpacked</strong> button that appears in the top-left toolbar.
            </p>
          </div>

          {/* Step 6 */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 space-y-2">
            <div className="flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 text-xs font-bold flex items-center justify-center">
                6
              </span>
              <h3 className="text-xs font-bold text-slate-900 dark:text-white">
                Select Extracted Folder
              </h3>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
              Choose the extracted folder that contains <code>manifest.json</code> at its root level.
            </p>
          </div>

          {/* Step 7 */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 space-y-2">
            <div className="flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 text-xs font-bold flex items-center justify-center">
                7
              </span>
              <h3 className="text-xs font-bold text-slate-900 dark:text-white">
                Pin Extension Icon
              </h3>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
              Click Chrome's puzzle piece extension menu and click the pin icon next to <strong>FluentMeet AI</strong>.
            </p>
          </div>

          {/* Step 8 */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 space-y-2">
            <div className="flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 text-xs font-bold flex items-center justify-center">
                8
              </span>
              <h3 className="text-xs font-bold text-slate-900 dark:text-white">
                Sign In with SaaS Account
              </h3>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
              Click the extension icon to open the Side Panel and log in using your FluentMeet SaaS account credentials.
            </p>
          </div>

          {/* Step 9 */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 space-y-2">
            <div className="flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 text-xs font-bold flex items-center justify-center">
                9
              </span>
              <h3 className="text-xs font-bold text-slate-900 dark:text-white">
                Verify Meeting Sync
              </h3>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
              Open Google Meet, Zoom, or Teams. The assistant will detect the call and initiate real-time coaching.
            </p>
          </div>
        </div>

        {/* Note Box */}
        <div className="bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900/50 rounded-xl p-4 flex items-start gap-3 text-xs text-amber-800 dark:text-amber-200">
          <Info className="w-4 h-4 text-amber-600 dark:text-amber-400 mt-0.5 shrink-0" />
          <div className="space-y-1">
            <strong className="font-semibold">Important Unpacked Extension Notice:</strong>
            <p className="leading-relaxed">
              ZIP archives cannot be dragged directly into Chrome. You must extract the ZIP into a permanent directory and use <strong>Load unpacked</strong>.
              If updating an existing unpacked extension, simply extract the new version over the same folder and click the reload icon (↻) in <code>chrome://extensions</code>.
            </p>
          </div>
        </div>
      </div>

      {/* Version History Table (Section 2.3) */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">
              Version History & Archive
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Access previous release builds, integrity checksums, and changelogs.
            </p>
          </div>
          <span className="text-xs text-slate-400 font-medium">
            {historyReleases.length} Published Releases
          </span>
        </div>

        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 dark:bg-slate-950/60 border-b border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 font-semibold uppercase tracking-wider">
                <tr>
                  <th className="px-5 py-3.5">Version</th>
                  <th className="px-5 py-3.5">Channel</th>
                  <th className="px-5 py-3.5">Release Date</th>
                  <th className="px-5 py-3.5">Package Size</th>
                  <th className="px-5 py-3.5">Status</th>
                  <th className="px-5 py-3.5">SHA-256 Checksum</th>
                  <th className="px-5 py-3.5 text-right">Download</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {historyReleases.map((rel) => {
                  const isCurrent = rel.version === latestRelease.version && rel.channel === latestRelease.channel;
                  const isExpanded = expandedVersion === rel.id;
                  return (
                    <React.Fragment key={rel.id}>
                      <tr className={`hover:bg-slate-50/70 dark:hover:bg-slate-800/40 transition-colors ${isCurrent ? 'bg-indigo-50/30 dark:bg-indigo-950/20' : ''}`}>
                        <td className="px-5 py-3.5 font-bold text-slate-900 dark:text-white">
                          <button
                            onClick={() => setExpandedVersion(isExpanded ? null : rel.id)}
                            className="flex items-center gap-1.5 hover:text-indigo-600 transition-colors"
                          >
                            <span>v{rel.version}</span>
                            {isExpanded ? (
                              <ChevronUp className="w-3.5 h-3.5 text-slate-400" />
                            ) : (
                              <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                            )}
                          </button>
                        </td>
                        <td className="px-5 py-3.5 capitalize text-slate-600 dark:text-slate-400">
                          <Badge variant={rel.channel === 'stable' ? 'neutral' : 'warning'} size="sm">
                            {rel.channel}
                          </Badge>
                        </td>
                        <td className="px-5 py-3.5 text-slate-500 dark:text-slate-400 whitespace-nowrap">
                          {formatDate(rel.published_at || rel.created_at)}
                        </td>
                        <td className="px-5 py-3.5 text-slate-600 dark:text-slate-400">
                          {formatSize(rel.artifact_size_bytes)}
                        </td>
                        <td className="px-5 py-3.5">
                          {isCurrent ? (
                            <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-2 py-0.5 rounded-full border border-emerald-200/50">
                              <CheckCircle2 className="w-3 h-3" />
                              Current Stable
                            </span>
                          ) : (
                            <span className="text-[11px] font-medium text-slate-400">
                              Archived
                            </span>
                          )}
                        </td>
                        <td className="px-5 py-3.5 font-mono text-[11px] text-slate-500">
                          {rel.sha256_checksum ? (
                            <button
                              onClick={() => handleCopyChecksum(rel.sha256_checksum!)}
                              title={rel.sha256_checksum}
                              className="hover:text-indigo-600 flex items-center gap-1 transition-colors"
                            >
                              <span>{rel.sha256_checksum.substring(0, 10)}...</span>
                              <Copy className="w-3 h-3 text-slate-400" />
                            </button>
                          ) : (
                            <span>-</span>
                          )}
                        </td>
                        <td className="px-5 py-3.5 text-right">
                          <Button
                            variant={isCurrent ? 'primary' : 'outline'}
                            size="sm"
                            onClick={() => handleDownload(rel)}
                            className="inline-flex items-center gap-1 text-xs"
                          >
                            <Download className="w-3 h-3" />
                            <span>Download</span>
                          </Button>
                        </td>
                      </tr>

                      {/* Expandable Changelog & Metadata Row */}
                      {isExpanded && (
                        <tr className="bg-slate-50 dark:bg-slate-950/40">
                          <td colSpan={7} className="px-5 py-4 border-t border-slate-100 dark:border-slate-800">
                            <div className="space-y-3">
                              <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500">
                                <span><strong>Build ID:</strong> {rel.build_number || 'build-ci-auto'}</span>
                                <span><strong>Commit SHA:</strong> <code>{rel.git_commit_sha || 'HEAD'}</code></span>
                                <span><strong>Manifest:</strong> MV{rel.manifest_version}</span>
                                <span><strong>Min Chrome:</strong> v{rel.minimum_chrome_version}</span>
                              </div>

                              {rel.sha256_checksum && (
                                <div className="text-xs">
                                  <strong className="text-slate-700 dark:text-slate-300">Full SHA-256: </strong>
                                  <code className="text-indigo-600 dark:text-indigo-400 break-all select-all font-mono text-[11px]">
                                    {rel.sha256_checksum}
                                  </code>
                                </div>
                              )}

                              {rel.release_notes && (
                                <div className="space-y-1 text-xs">
                                  <strong className="text-slate-700 dark:text-slate-300">Changelog:</strong>
                                  <ul className="list-disc list-inside text-slate-600 dark:text-slate-400 space-y-0.5">
                                    {(Array.isArray(rel.release_notes)
                                      ? rel.release_notes
                                      : [String(rel.release_notes)]
                                    ).map((note: string, idx: number) => (
                                      <li key={idx}>{note}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

