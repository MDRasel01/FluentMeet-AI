import React from 'react';
import { clsx } from 'clsx';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { Card } from './Card';

export interface StatCardProps {
  title: string;
  value: string | number;
  change?: string;
  trend?: 'up' | 'down' | 'neutral';
  supportingText?: string;
  icon?: React.ReactNode;
  className?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  change,
  trend = 'neutral',
  supportingText,
  icon,
  className,
}) => {
  return (
    <Card className={clsx('relative overflow-hidden', className)}>
      <div className="flex items-center justify-between">
        <p className="text-xs font-medium text-slate-500 dark:text-slate-400">{title}</p>
        {icon && (
          <div className="w-8 h-8 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-slate-600 dark:text-slate-300">
            {icon}
          </div>
        )}
      </div>

      <div className="mt-3 flex items-baseline gap-2">
        <span className="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-50 tabular-nums">
          {value}
        </span>
        {change && (
          <span
            className={clsx(
              'inline-flex items-center text-xs font-semibold px-1.5 py-0.5 rounded',
              trend === 'up' && 'text-emerald-700 bg-emerald-50 dark:text-emerald-300 dark:bg-emerald-950/60',
              trend === 'down' && 'text-rose-700 bg-rose-50 dark:text-rose-300 dark:bg-rose-950/60',
              trend === 'neutral' && 'text-slate-600 bg-slate-100 dark:text-slate-400 dark:bg-slate-800'
            )}
          >
            {trend === 'up' && <TrendingUp className="w-3 h-3 mr-0.5" />}
            {trend === 'down' && <TrendingDown className="w-3 h-3 mr-0.5" />}
            {trend === 'neutral' && <Minus className="w-3 h-3 mr-0.5" />}
            {change}
          </span>
        )}
      </div>

      {supportingText && (
        <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{supportingText}</p>
      )}
    </Card>
  );
};

