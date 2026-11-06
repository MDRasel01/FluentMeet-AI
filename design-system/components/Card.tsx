import React from 'react';
import { clsx } from 'clsx';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'subtle' | 'outline' | 'elevated';
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(({
  className,
  variant = 'default',
  padding = 'md',
  children,
  ...props
}, ref) => {
  const variantStyles = {
    default: 'bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm',
    subtle: 'bg-slate-50 dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800/80',
    outline: 'bg-transparent border border-slate-300 dark:border-slate-700',
    elevated: 'bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-md',
  };

  const paddingStyles = {
    none: 'p-0',
    sm: 'p-3',
    md: 'p-5',
    lg: 'p-6',
  };

  return (
    <div
      ref={ref}
      className={clsx(
        'rounded-xl transition-all',
        variantStyles[variant],
        paddingStyles[padding],
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
});

Card.displayName = 'Card';

