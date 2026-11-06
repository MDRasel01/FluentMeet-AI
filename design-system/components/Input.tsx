import React from 'react';
import { clsx } from 'clsx';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  helperText?: string;
  error?: string;
  leadingIcon?: React.ReactNode;
  trailingIcon?: React.ReactNode;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(({
  className,
  label,
  helperText,
  error,
  leadingIcon,
  trailingIcon,
  disabled,
  id,
  ...props
}, ref) => {
  const generatedId = id || React.useId();

  return (
    <div className="w-full space-y-1.5 text-left">
      {label && (
        <label
          htmlFor={generatedId}
          className="block text-xs font-medium text-slate-700 dark:text-slate-300"
        >
          {label}
        </label>
      )}
      <div className="relative rounded-lg shadow-sm">
        {leadingIcon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
            {leadingIcon}
          </div>
        )}
        <input
          id={generatedId}
          ref={ref}
          disabled={disabled}
          className={clsx(
            'block w-full rounded-lg border bg-white px-3 py-2 text-sm text-slate-900 transition-colors placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-offset-1 dark:bg-slate-900 dark:text-slate-100 dark:placeholder:text-slate-500',
            leadingIcon && 'pl-9',
            trailingIcon && 'pr-9',
            error
              ? 'border-rose-300 text-rose-900 focus:border-rose-500 focus:ring-rose-500 dark:border-rose-700'
              : 'border-slate-300 focus:border-indigo-500 focus:ring-indigo-500 dark:border-slate-700',
            disabled && 'bg-slate-100 cursor-not-allowed opacity-60 dark:bg-slate-800',
            className
          )}
          {...props}
        />
        {trailingIcon && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400">
            {trailingIcon}
          </div>
        )}
      </div>
      {error ? (
        <p className="text-xs text-rose-600 dark:text-rose-400">{error}</p>
      ) : helperText ? (
        <p className="text-xs text-slate-500 dark:text-slate-400">{helperText}</p>
      ) : null}
    </div>
  );
});

Input.displayName = 'Input';

