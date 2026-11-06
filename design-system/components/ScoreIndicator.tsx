import React from 'react';
import { clsx } from 'clsx';

export interface ScoreIndicatorProps {
  score: number;
  maxScore?: number;
  label?: string;
  size?: 'sm' | 'md' | 'lg';
  insufficientData?: boolean;
  className?: string;
}

export const ScoreIndicator: React.FC<ScoreIndicatorProps> = ({
  score,
  maxScore = 100,
  label,
  size = 'md',
  insufficientData = false,
  className,
}) => {
  if (insufficientData) {
    return (
      <div className={clsx('inline-flex flex-col items-center justify-center', className)}>
        <div className="px-2.5 py-1 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 text-xs font-medium">
          Insufficient Data
        </div>
        {label && <span className="mt-1 text-xs text-slate-400">{label}</span>}
      </div>
    );
  }

  // Calculate percentage
  const percentage = (score / maxScore) * 100;

  // Semantic color logic
  let colorClass = 'text-rose-600 bg-rose-50 border-rose-200 dark:bg-rose-950/40 dark:text-rose-400 dark:border-rose-900';
  let badgeColor = 'bg-rose-500';

  if (percentage >= 85) {
    colorClass = 'text-emerald-600 bg-emerald-50 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-400 dark:border-emerald-900';
    badgeColor = 'bg-emerald-500';
  } else if (percentage >= 70) {
    colorClass = 'text-indigo-600 bg-indigo-50 border-indigo-200 dark:bg-indigo-950/40 dark:text-indigo-400 dark:border-indigo-900';
    badgeColor = 'bg-indigo-500';
  } else if (percentage >= 50) {
    colorClass = 'text-amber-600 bg-amber-50 border-amber-200 dark:bg-amber-950/40 dark:text-amber-400 dark:border-amber-900';
    badgeColor = 'bg-amber-500';
  }

  const sizeStyles = {
    sm: 'w-10 h-10 text-sm',
    md: 'w-14 h-14 text-lg',
    lg: 'w-20 h-20 text-2xl',
  };

  return (
    <div className={clsx('inline-flex flex-col items-center justify-center text-center', className)}>
      <div
        className={clsx(
          'rounded-full border-2 flex items-center justify-center font-bold tabular-nums shadow-xs',
          colorClass,
          sizeStyles[size]
        )}
      >
        {score}
      </div>
      {label && (
        <span className="mt-1.5 text-xs font-medium text-slate-600 dark:text-slate-300">
          {label}
        </span>
      )}
    </div>
  );
};

