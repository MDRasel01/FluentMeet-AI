import React from 'react';
import { clsx } from 'clsx';
import { Play } from 'lucide-react';

export interface MistakeSpan {
  id: string;
  original: string;
  corrected: string;
  explanation: string;
  type: 'grammar' | 'vocabulary' | 'pronunciation';
}

export interface TranscriptSegmentProps {
  speakerName: string;
  speakerAvatar?: string;
  speakerColor?: string;
  timestamp: string;
  text: string;
  mistakes?: MistakeSpan[];
  isActive?: boolean;
  onPlayClick?: () => void;
  onMistakeClick?: (mistake: MistakeSpan) => void;
  className?: string;
}

export const TranscriptSegment: React.FC<TranscriptSegmentProps> = ({
  speakerName,
  speakerAvatar,
  speakerColor = '#6366F1',
  timestamp,
  text,
  mistakes = [],
  isActive = false,
  onPlayClick,
  onMistakeClick,
  className,
}) => {
  return (
    <div
      className={clsx(
        'group p-3.5 rounded-xl border transition-all duration-150',
        isActive
          ? 'bg-indigo-50/70 border-indigo-200 dark:bg-indigo-950/30 dark:border-indigo-800/80 shadow-xs'
          : 'bg-white dark:bg-slate-900 border-slate-200/80 dark:border-slate-800/80 hover:border-slate-300 dark:hover:border-slate-700',
        className
      )}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          {speakerAvatar ? (
            <img src={speakerAvatar} alt={speakerName} className="w-5 h-5 rounded-full object-cover" />
          ) : (
            <div
              className="w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold text-white uppercase shadow-xs"
              style={{ backgroundColor: speakerColor }}
            >
              {speakerName[0]}
            </div>
          )}
          <span className="text-xs font-semibold text-slate-800 dark:text-slate-200">
            {speakerName}
          </span>
          <span className="text-[11px] font-mono text-slate-400 dark:text-slate-500">
            {timestamp}
          </span>
        </div>

        {onPlayClick && (
          <button
            onClick={onPlayClick}
            className="opacity-0 group-hover:opacity-100 transition-opacity p-1 text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400"
            title="Play from this sentence"
          >
            <Play className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      <p className="text-sm leading-relaxed text-slate-700 dark:text-slate-300">
        {text}
      </p>

      {mistakes.length > 0 && (
        <div className="mt-2.5 pt-2 border-t border-slate-100 dark:border-slate-800 flex flex-wrap gap-2">
          {mistakes.map((m) => (
            <button
              key={m.id}
              onClick={() => onMistakeClick && onMistakeClick(m)}
              className={clsx(
                'inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-medium border transition-colors',
                m.type === 'grammar' && 'bg-rose-50 border-rose-200 text-rose-700 hover:bg-rose-100 dark:bg-rose-950/40 dark:border-rose-900 dark:text-rose-300',
                m.type === 'vocabulary' && 'bg-amber-50 border-amber-200 text-amber-700 hover:bg-amber-100 dark:bg-amber-950/40 dark:border-amber-900 dark:text-amber-300',
                m.type === 'pronunciation' && 'bg-sky-50 border-sky-200 text-sky-700 hover:bg-sky-100 dark:bg-sky-950/40 dark:border-sky-900 dark:text-sky-300'
              )}
            >
              <span className="line-through opacity-70">{m.original}</span>
              <span>→</span>
              <span className="font-semibold">{m.corrected}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

