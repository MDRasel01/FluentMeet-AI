import React, { useState } from 'react';
import { clsx } from 'clsx';
import { Play, Pause, RotateCcw, RotateCw, Volume2, VolumeX } from 'lucide-react';
import { Button } from './Button';

export interface AudioPlayerProps {
  currentTime?: number;
  duration?: number;
  isPlaying?: boolean;
  onPlayPause?: () => void;
  onSeek?: (seconds: number) => void;
  className?: string;
}

export const AudioPlayer: React.FC<AudioPlayerProps> = ({
  currentTime = 142,
  duration = 840,
  isPlaying: externalIsPlaying,
  onPlayPause,
  onSeek,
  className,
}) => {
  const [internalPlaying, setInternalPlaying] = useState(false);
  const [speed, setSpeed] = useState<number>(1);
  const [isMuted, setIsMuted] = useState(false);

  const isPlaying = externalIsPlaying !== undefined ? externalIsPlaying : internalPlaying;

  const togglePlay = () => {
    if (onPlayPause) {
      onPlayPause();
    } else {
      setInternalPlaying(!internalPlaying);
    }
  };

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const progressPercent = Math.min(100, Math.max(0, (currentTime / duration) * 100));

  const speeds = [0.75, 1, 1.25, 1.5];

  const cycleSpeed = () => {
    const nextIdx = (speeds.indexOf(speed) + 1) % speeds.length;
    setSpeed(speeds[nextIdx]);
  };

  return (
    <div
      className={clsx(
        'w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-3 shadow-md flex flex-col md:flex-row items-center gap-3',
        className
      )}
    >
      <div className="flex items-center gap-2">
        <button
          onClick={() => onSeek && onSeek(Math.max(0, currentTime - 5))}
          className="p-1.5 text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 transition-colors"
          title="Rewind 5 seconds"
        >
          <RotateCcw className="w-4 h-4" />
        </button>

        <button
          onClick={togglePlay}
          className="w-10 h-10 rounded-full bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 text-white flex items-center justify-center shadow-sm transition-transform active:scale-95"
          aria-label={isPlaying ? 'Pause' : 'Play'}
        >
          {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5 ml-0.5" />}
        </button>

        <button
          onClick={() => onSeek && onSeek(Math.min(duration, currentTime + 5))}
          className="p-1.5 text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 transition-colors"
          title="Forward 5 seconds"
        >
          <RotateCw className="w-4 h-4" />
        </button>
      </div>

      <div className="flex-1 w-full flex items-center gap-2">
        <span className="text-xs font-mono text-slate-500 dark:text-slate-400 tabular-nums shrink-0">
          {formatTime(currentTime)}
        </span>

        {/* Timeline Scrubber */}
        <div
          className="relative flex-1 h-6 flex items-center cursor-pointer group"
          onClick={(e) => {
            const rect = e.currentTarget.getBoundingClientRect();
            const clickPos = (e.clientX - rect.left) / rect.width;
            if (onSeek) onSeek(Math.floor(clickPos * duration));
          }}
        >
          <div className="w-full h-1.5 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-indigo-600 rounded-full transition-all duration-75"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
          {/* Thumb marker */}
          <div
            className="absolute w-3 h-3 bg-indigo-600 border-2 border-white dark:border-slate-900 rounded-full shadow-sm -ml-1.5 transition-all opacity-0 group-hover:opacity-100"
            style={{ left: `${progressPercent}%` }}
          />
        </div>

        <span className="text-xs font-mono text-slate-500 dark:text-slate-400 tabular-nums shrink-0">
          {formatTime(duration)}
        </span>
      </div>

      <div className="flex items-center gap-2 shrink-0">
        <button
          onClick={cycleSpeed}
          className="px-2 py-1 text-xs font-mono font-semibold rounded bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
          title="Change playback speed"
        >
          {speed}x
        </button>

        <button
          onClick={() => setIsMuted(!isMuted)}
          className="p-1.5 text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 transition-colors"
        >
          {isMuted ? <VolumeX className="w-4 h-4 text-rose-500" /> : <Volume2 className="w-4 h-4" />}
        </button>
      </div>
    </div>
  );
};

