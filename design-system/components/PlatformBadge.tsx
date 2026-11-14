import React from 'react';
import { PlatformIcon, PlatformType } from './PlatformIcon';

export interface PlatformBadgeProps {
  platform: PlatformType;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  showIconOnly?: boolean;
}

export const PlatformBadge: React.FC<PlatformBadgeProps> = ({
  platform,
  size = 'md',
  className = '',
  showIconOnly = false,
}) => {
  const normalized = platform.toLowerCase().trim();

  let label = 'Online Meeting';
  let badgeStyles = 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700';

  if (normalized === 'google-meet' || normalized === 'google' || normalized === 'meet') {
    label = 'Google Meet';
    badgeStyles = 'bg-emerald-50/90 dark:bg-emerald-950/50 text-emerald-800 dark:text-emerald-300 border-emerald-200/80 dark:border-emerald-800/60 shadow-sm shadow-emerald-500/5';
  } else if (normalized === 'zoom' || normalized === 'zoom-us') {
    label = 'Zoom Web';
    badgeStyles = 'bg-sky-50/90 dark:bg-sky-950/50 text-sky-800 dark:text-sky-300 border-sky-200/80 dark:border-sky-800/60 shadow-sm shadow-sky-500/5';
  } else if (normalized === 'teams' || normalized === 'ms-teams' || normalized === 'microsoft-teams') {
    label = 'MS Teams';
    badgeStyles = 'bg-indigo-50/90 dark:bg-indigo-950/50 text-indigo-800 dark:text-indigo-300 border-indigo-200/80 dark:border-indigo-800/60 shadow-sm shadow-indigo-500/5';
  } else if (normalized === 'all' || normalized === 'all-platforms') {
    label = 'All Platforms';
    badgeStyles = 'bg-purple-50/90 dark:bg-purple-950/50 text-purple-800 dark:text-purple-300 border-purple-200/80 dark:border-purple-800/60 shadow-sm shadow-purple-500/5';
  }

  const iconSizes = {
    sm: 16,
    md: 20,
    lg: 26,
  };

  const containerSizes = {
    sm: 'px-2 py-0.5 text-[11px] gap-1.5',
    md: 'px-2.5 py-1 text-xs gap-2',
    lg: 'px-3 py-1.5 text-sm gap-2.5',
  };

  if (showIconOnly) {
    return (
      <span
        title={label}
        className={`inline-flex items-center justify-center rounded-lg p-1 border ${badgeStyles} ${className}`}
      >
        <PlatformIcon platform={platform} size={iconSizes[size]} />
      </span>
    );
  }

  return (
    <span
      className={`inline-flex items-center font-semibold rounded-full border transition-all ${containerSizes[size]} ${badgeStyles} ${className}`}
    >
      <PlatformIcon platform={platform} size={iconSizes[size]} />
      <span>{label}</span>
    </span>
  );
};
