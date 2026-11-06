import React from 'react';
import { clsx } from 'clsx';
import { Play, Check, BookmarkPlus, AlertCircle } from 'lucide-react';
import { Badge } from './Badge';
import { Button } from './Button';
import { Card } from './Card';

export interface GrammarErrorCardProps {
  originalSentence: string;
  correctedSentence: string;
  errorCategory: string;
  severity?: 'high' | 'medium' | 'low';
  explanation: string;
  timestamp?: string;
  onPlayAudio?: () => void;
  onAddToPractice?: () => void;
  isSaved?: boolean;
  className?: string;
}

export const GrammarErrorCard: React.FC<GrammarErrorCardProps> = ({
  originalSentence,
  correctedSentence,
  errorCategory,
  severity = 'medium',
  explanation,
  timestamp,
  onPlayAudio,
  onAddToPractice,
  isSaved = false,
  className,
}) => {
  return (
    <Card className={clsx('space-y-3.5', className)}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Badge variant="danger" size="sm">
            {errorCategory}
          </Badge>
          {severity && (
            <span
              className={clsx(
                'text-[11px] font-semibold uppercase tracking-wider',
                severity === 'high' && 'text-rose-600 dark:text-rose-400',
                severity === 'medium' && 'text-amber-600 dark:text-amber-400',
                severity === 'low' && 'text-slate-500 dark:text-slate-400'
              )}
            >
              {severity} impact
            </span>
          )}
        </div>

        {timestamp && (
          <span className="text-xs font-mono text-slate-400 dark:text-slate-500">
            {timestamp}
          </span>
        )}
      </div>

      <div className="space-y-2 text-sm">
        <div className="p-2.5 rounded-lg bg-rose-50/60 dark:bg-rose-950/20 border border-rose-200/60 dark:border-rose-900/40">
          <p className="text-xs font-medium text-rose-800 dark:text-rose-300 mb-1">What you said:</p>
          <p className="text-rose-900 dark:text-rose-200">{originalSentence}</p>
        </div>

        <div className="p-2.5 rounded-lg bg-emerald-50/60 dark:bg-emerald-950/20 border border-emerald-200/60 dark:border-emerald-900/40">
          <p className="text-xs font-medium text-emerald-800 dark:text-emerald-300 mb-1">Better alternative:</p>
          <p className="text-emerald-900 dark:text-emerald-200 font-medium">{correctedSentence}</p>
        </div>
      </div>

      <div className="flex items-start gap-2 pt-1 text-xs text-slate-600 dark:text-slate-400">
        <AlertCircle className="w-4 h-4 text-indigo-500 shrink-0 mt-0.5" />
        <p className="leading-relaxed">{explanation}</p>
      </div>

      <div className="flex items-center justify-between pt-2 border-t border-slate-100 dark:border-slate-800">
        {onPlayAudio ? (
          <Button
            variant="ghost"
            size="sm"
            leadingIcon={<Play className="w-3.5 h-3.5" />}
            onClick={onPlayAudio}
          >
            Play Clip
          </Button>
        ) : <div />}

        {onAddToPractice && (
          <Button
            variant={isSaved ? 'secondary' : 'outline'}
            size="sm"
            leadingIcon={isSaved ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <BookmarkPlus className="w-3.5 h-3.5" />}
            onClick={onAddToPractice}
          >
            {isSaved ? 'In Practice Deck' : 'Add to Practice'}
          </Button>
        )}
      </div>
    </Card>
  );
};

