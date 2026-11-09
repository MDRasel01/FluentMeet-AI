/**
 * FluentMeet AI - Step 10: Export Actions Bar Component
 */

import React from 'react';
import { FileSpreadsheet, FileCode, Loader2 } from 'lucide-react';

interface ExportActionsProps {
  onExportCsv: () => void;
  onExportHtml: () => void;
  isExporting?: boolean;
}

export const ExportActions: React.FC<ExportActionsProps> = ({
  onExportCsv,
  onExportHtml,
  isExporting = false,
}) => {
  return (
    <div className="flex items-center gap-2">
      <button
        onClick={onExportCsv}
        disabled={isExporting}
        className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg border border-slate-700 transition disabled:opacity-50"
      >
        {isExporting ? (
          <Loader2 className="w-3.5 h-3.5 animate-spin" />
        ) : (
          <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400" />
        )}
        <span>Export CSV</span>
      </button>

      <button
        onClick={onExportHtml}
        disabled={isExporting}
        className="flex items-center gap-2 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg shadow-sm transition disabled:opacity-50"
      >
        {isExporting ? (
          <Loader2 className="w-3.5 h-3.5 animate-spin" />
        ) : (
          <FileCode className="w-3.5 h-3.5" />
        )}
        <span>Print Report</span>
      </button>
    </div>
  );
};
