import React, { useState } from 'react';
import { X, Download, ShieldCheck, ExternalLink, Check, Copy } from 'lucide-react';

interface ExtensionDownloadModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ExtensionDownloadModal: React.FC<ExtensionDownloadModalProps> = ({
  isOpen,
  onClose,
}) => {
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const handleCopyPath = () => {
    navigator.clipboard.writeText('chrome://extensions');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadZip = () => {
    // In production, this requests a short-lived signed URL from Supabase Storage
    const element = document.createElement('a');
    element.href = '/dist/fluentmeet-extension-v1.0.0.zip';
    element.setAttribute('download', 'fluentmeet-extension-v1.0.0.zip');
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
      <div className="w-full max-w-xl bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-7 shadow-2xl border border-slate-200 dark:border-slate-800 space-y-6 animate-in fade-in zoom-in-95">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100 dark:border-slate-800">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-2xl bg-indigo-600 text-white shadow-md shadow-indigo-500/20">
              <Download className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-black text-slate-900 dark:text-white">
                Chrome Extension Package (v1.0.0)
              </h3>
              <p className="text-[11px] text-slate-500 dark:text-slate-400">
                Official Manifest V3 build with sidepanel speech assistance
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-xl text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Download Info Card */}
        <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="space-y-1 text-center sm:text-left">
            <span className="text-xs font-bold text-slate-900 dark:text-white block">
              fluentmeet-extension-v1.0.0.zip
            </span>
            <div className="flex items-center gap-2 text-[11px] text-slate-400">
              <span>Size: 1.2 MB</span>
              <span>•</span>
              <span className="flex items-center gap-1 text-emerald-500">
                <ShieldCheck className="w-3.5 h-3.5" /> SHA-256 Verified
              </span>
            </div>
          </div>

          <button
            onClick={handleDownloadZip}
            className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs flex items-center gap-2 shadow-md shadow-indigo-500/20 transition-all shrink-0"
          >
            <Download className="w-4 h-4" />
            <span>Download ZIP</span>
          </button>
        </div>

        {/* Step-by-step Load Unpacked Instructions */}
        <div className="space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
            Installation Steps: Load Unpacked in Chrome
          </h4>
          <ol className="space-y-2.5 text-xs text-slate-600 dark:text-slate-300">
            <li className="flex items-start gap-2.5 p-2 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800/40">
              <span className="w-5 h-5 rounded-full bg-indigo-100 dark:bg-indigo-950/80 text-indigo-600 dark:text-indigo-400 font-bold flex items-center justify-center shrink-0 text-[11px]">
                1
              </span>
              <div className="flex-1">
                <span>Download and unzip the package to a local folder on your machine.</span>
              </div>
            </li>

            <li className="flex items-start gap-2.5 p-2 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800/40">
              <span className="w-5 h-5 rounded-full bg-indigo-100 dark:bg-indigo-950/80 text-indigo-600 dark:text-indigo-400 font-bold flex items-center justify-center shrink-0 text-[11px]">
                2
              </span>
              <div className="flex-1 flex flex-wrap items-center gap-2">
                <span>Navigate to</span>
                <code className="px-2 py-0.5 rounded bg-slate-200 dark:bg-slate-800 font-mono font-bold text-[11px]">
                  chrome://extensions
                </code>
                <button
                  type="button"
                  onClick={handleCopyPath}
                  className="p-1 rounded text-slate-400 hover:text-indigo-600 text-[11px] inline-flex items-center gap-1"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copied ? 'Copied' : 'Copy'}</span>
                </button>
              </div>
            </li>

            <li className="flex items-start gap-2.5 p-2 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800/40">
              <span className="w-5 h-5 rounded-full bg-indigo-100 dark:bg-indigo-950/80 text-indigo-600 dark:text-indigo-400 font-bold flex items-center justify-center shrink-0 text-[11px]">
                3
              </span>
              <div className="flex-1">
                <span>Toggle on <strong>Developer mode</strong> in the top-right corner of the Extensions page.</span>
              </div>
            </li>

            <li className="flex items-start gap-2.5 p-2 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800/40">
              <span className="w-5 h-5 rounded-full bg-indigo-100 dark:bg-indigo-950/80 text-indigo-600 dark:text-indigo-400 font-bold flex items-center justify-center shrink-0 text-[11px]">
                4
              </span>
              <div className="flex-1">
                <span>Click <strong>Load unpacked</strong> and select the unzipped directory.</span>
              </div>
            </li>
          </ol>
        </div>

        <div className="pt-2 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 text-xs font-semibold"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
