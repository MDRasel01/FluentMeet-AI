import React, { useState, useRef, useEffect } from 'react';
import { PlatformIcon, PlatformType } from './PlatformIcon';
import { ChevronDown, Check } from 'lucide-react';

export interface PlatformOption {
  value: PlatformType;
  label: string;
  domain?: string;
  badge?: string;
}

export const PLATFORM_OPTIONS: PlatformOption[] = [
  {
    value: 'all',
    label: 'All Platforms',
    domain: 'All meeting sources',
    badge: 'Universal',
  },
  {
    value: 'google-meet',
    label: 'Google Meet',
    domain: 'meet.google.com',
    badge: 'Dual Track',
  },
  {
    value: 'zoom',
    label: 'Zoom Web',
    domain: 'app.zoom.us / zoom.us',
    badge: 'Tab Audio',
  },
  {
    value: 'teams',
    label: 'Microsoft Teams',
    domain: 'teams.microsoft.com',
    badge: 'Tab Audio',
  },
];

export interface PlatformSelectProps {
  value: PlatformType;
  onChange: (value: PlatformType) => void;
  options?: PlatformOption[];
  variant?: 'pills' | 'dropdown';
  size?: 'sm' | 'md' | 'lg';
  label?: string;
  className?: string;
  disabled?: boolean;
}

export const PlatformSelect: React.FC<PlatformSelectProps> = ({
  value,
  onChange,
  options = PLATFORM_OPTIONS,
  variant = 'pills',
  size = 'md',
  label,
  className = '',
  disabled = false,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown on click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const currentOption = options.find((o) => o.value === value) || options[0];

  // PILL / SEGMENTED BUTTONS VARIANT
  if (variant === 'pills') {
    return (
      <div className={`flex flex-col gap-1.5 ${className}`}>
        {label && (
          <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">
            {label}
          </span>
        )}
        <div
          className="inline-flex flex-wrap items-center gap-1.5 p-1 rounded-xl bg-slate-100 dark:bg-slate-800/90 border border-slate-200 dark:border-slate-700 shadow-inner select-none"
          role="radiogroup"
          aria-label={label || 'Select Meeting Platform'}
        >
          {options.map((opt) => {
            const isSelected = opt.value === value;
            return (
              <button
                key={opt.value}
                type="button"
                role="radio"
                aria-checked={isSelected}
                disabled={disabled}
                onClick={() => onChange(opt.value)}
                className={`group relative flex items-center gap-2 rounded-lg font-semibold transition-all duration-200 ${
                  size === 'sm'
                    ? 'px-2.5 py-1 text-xs'
                    : size === 'lg'
                    ? 'px-4 py-2 text-sm'
                    : 'px-3 py-1.5 text-xs'
                } ${
                  isSelected
                    ? 'bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-md border border-slate-200 dark:border-slate-700'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-white/60 dark:hover:bg-slate-800'
                } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
              >
                {/* 3D Platform Icon */}
                <PlatformIcon
                  platform={opt.value}
                  size={size === 'sm' ? 18 : size === 'lg' ? 26 : 22}
                  showGlow={isSelected}
                />

                <span className="truncate">{opt.label}</span>

                {/* Subtle active glow dot */}
                {isSelected && (
                  <span
                    className={`w-1.5 h-1.5 rounded-full animate-pulse ${
                      opt.value === 'google-meet'
                        ? 'bg-emerald-500'
                        : opt.value === 'zoom'
                        ? 'bg-sky-500'
                        : opt.value === 'teams'
                        ? 'bg-indigo-500'
                        : 'bg-indigo-600'
                    }`}
                  />
                )}
              </button>
            );
          })}
        </div>
      </div>
    );
  }

  // DROPDOWN VARIANT
  return (
    <div className={`relative inline-block text-left ${className}`} ref={dropdownRef}>
      {label && (
        <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
          {label}
        </label>
      )}

      {/* Trigger Button with prominent 3D Icon */}
      <button
        type="button"
        disabled={disabled}
        onClick={() => !disabled && setIsOpen(!isOpen)}
        className={`w-full flex items-center justify-between gap-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl shadow-sm transition-all text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 hover:border-slate-300 dark:hover:border-slate-600 ${
          size === 'sm' ? 'px-2.5 py-1.5 text-xs' : size === 'lg' ? 'px-4 py-3 text-sm' : 'px-3 py-2 text-xs'
        } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
      >
        <div className="flex items-center gap-2.5 truncate">
          <PlatformIcon platform={currentOption.value} size={size === 'sm' ? 20 : 26} />
          <span className="font-bold truncate">{currentOption.label}</span>
          {currentOption.domain && (
            <span className="text-[10px] text-slate-400 font-mono hidden sm:inline">
              ({currentOption.domain})
            </span>
          )}
        </div>
        <ChevronDown
          className={`w-4 h-4 text-slate-400 transition-transform duration-200 shrink-0 ${
            isOpen ? 'rotate-180 text-indigo-600' : ''
          }`}
        />
      </button>

      {/* Floating Animated Dropdown Menu with 3D Icons */}
      {isOpen && (
        <div
          className="absolute z-50 mt-1.5 w-64 min-w-full rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-2xl p-1.5 space-y-1 animate-in fade-in zoom-in-95 duration-100"
          role="listbox"
        >
          <div className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-slate-400 border-b border-slate-100 dark:border-slate-800">
            Select Meeting Platform
          </div>

          {options.map((opt) => {
            const isSelected = opt.value === value;
            return (
              <div
                key={opt.value}
                role="option"
                aria-selected={isSelected}
                onClick={() => {
                  onChange(opt.value);
                  setIsOpen(false);
                }}
                className={`flex items-center justify-between p-2 rounded-xl cursor-pointer transition-all ${
                  isSelected
                    ? 'bg-indigo-50/80 dark:bg-indigo-950/50 text-indigo-900 dark:text-indigo-200 border border-indigo-200/60 dark:border-indigo-800/60'
                    : 'hover:bg-slate-50 dark:hover:bg-slate-800/70 text-slate-700 dark:text-slate-300'
                }`}
              >
                <div className="flex items-center gap-3">
                  <PlatformIcon platform={opt.value} size={28} />
                  <div>
                    <span className="text-xs font-bold block leading-tight">{opt.label}</span>
                    {opt.domain && (
                      <span className="text-[10px] text-slate-400 font-mono block">{opt.domain}</span>
                    )}
                  </div>
                </div>

                {isSelected && (
                  <div className="w-5 h-5 rounded-full bg-indigo-600 text-white flex items-center justify-center shrink-0 shadow-sm">
                    <Check className="w-3 h-3 stroke-[3]" />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
