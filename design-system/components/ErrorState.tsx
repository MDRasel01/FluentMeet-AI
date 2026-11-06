import React from 'react';
import { clsx } from 'clsx';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { Button } from './Button';

export interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  className?: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Something went wrong',
  message,
  onRetry,
  className,
}) => {
  return (
    <div
      className={clsx(
        'p-6 rounded-xl border border-rose-200 dark:border-rose-900/60 bg-rose-50/50 dark:bg-rose-950/20 text-center max-w-md mx-auto space-y-3',
        className
      )}
    >
      <div className="w-10 h-10 rounded-full bg-rose-100 dark:bg-rose-900/40 text-rose-600 dark:text-rose-400 flex items-center justify-center mx-auto">
        <AlertTriangle className="w-5 h-5" />
      </div>

      <h4 className="text-sm font-semibold text-rose-900 dark:text-rose-200">
        {title}
      </h4>

      <p className="text-xs text-rose-700 dark:text-rose-400 leading-relaxed">
        {message}
      </p>

      {onRetry && (
        <div className="pt-2">
          <Button
            variant="outline"
            size="sm"
            onClick={onRetry}
            leadingIcon={<RefreshCw className="w-3.5 h-3.5" />}
          >
            Retry Connection
          </Button>
        </div>
      )}
    </div>
  );
};

