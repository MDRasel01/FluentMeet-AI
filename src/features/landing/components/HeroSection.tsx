import React, { useState } from 'react';
import {
  Sparkles,
  CheckCircle2,
  Mic,
  Volume2,
  TrendingUp,
  Award,
  Layers,
  Check,
  Star,
  Users
} from 'lucide-react';
import { PlatformIcon } from '../../../../design-system/components';

interface HeroSectionProps {
  onStartFree?: () => void;
  onOpenDemo?: () => void;
  onDownloadExtension?: () => void;
}

export const HeroSection: React.FC<HeroSectionProps> = () => {
  const [activePill, setActivePill] = useState<'coach' | 'grammar' | 'cefr'>('coach');

  return (
    <section className="relative overflow-hidden pt-10 pb-20 md:pt-16 md:pb-28">
      {/* Radiant Mesh Background Glows (Calliom Style) */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-[620px] pointer-events-none -z-10">
        <div className="absolute top-[-80px] left-[15%] w-[480px] h-[480px] rounded-full bg-gradient-to-tr from-purple-400/25 to-indigo-500/20 blur-[120px] dark:from-purple-900/30 dark:to-indigo-900/20" />
        <div className="absolute top-[40px] right-[10%] w-[420px] h-[420px] rounded-full bg-gradient-to-br from-pink-300/25 via-amber-200/20 to-purple-400/20 blur-[130px] dark:from-pink-900/20 dark:via-purple-900/20 dark:to-indigo-950/30" />
        <div className="absolute top-[200px] left-[35%] w-[360px] h-[360px] rounded-full bg-gradient-to-r from-cyan-300/20 to-blue-400/15 blur-[100px] dark:from-cyan-900/20 dark:to-blue-900/10" />
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Main Hero Headline */}
        <div className="flex flex-col items-center text-center max-w-5xl mx-auto">
          <h1 className="text-3xl xs:text-4xl sm:text-5xl md:text-6xl lg:text-[64px] font-black text-slate-900 dark:text-white tracking-tight leading-[1.15]">
            <span className="block">AI Meeting Coach for</span>
            <span className="block mt-1 sm:mt-2 sm:whitespace-nowrap">
              <span className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-500 bg-clip-text text-transparent">
                Flawless English
              </span>{' '}
              in Every Call.
            </span>
          </h1>
        </div>

        {/* Live Interactive Hero Canvas (Livo AI + Calliom Style) */}
        <div className="mt-8 md:mt-12 relative max-w-5xl mx-auto">
          {/* Decorative outer gradient halo */}
          <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/20 via-purple-500/20 to-pink-500/20 rounded-3xl blur-2xl -z-10" />

          {/* Main Card Container */}
          <div className="bg-white/95 dark:bg-slate-900/95 backdrop-blur-2xl rounded-3xl border border-slate-200/90 dark:border-slate-800 shadow-2xl overflow-hidden p-3 sm:p-6 md:p-8">
            {/* Top Interactive Mode Tabs (Calliom Style) */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 sm:pb-6 border-b border-slate-100 dark:border-slate-800">
              <div className="flex items-center gap-1.5 sm:gap-2 bg-slate-100 dark:bg-slate-800/80 p-1 rounded-2xl text-[11px] sm:text-xs font-semibold overflow-x-auto scrollbar-none max-w-full">
                <button
                  onClick={() => setActivePill('coach')}
                  className={`px-2.5 py-1.5 sm:px-4 sm:py-1.5 rounded-xl transition-all flex items-center gap-1.5 whitespace-nowrap shrink-0 ${
                    activePill === 'coach'
                      ? 'bg-white dark:bg-slate-700 text-indigo-600 dark:text-indigo-400 shadow-sm font-bold'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                  }`}
                >
                  <Mic className="w-3.5 h-3.5" />
                  <span>Real-Time Co-Pilot</span>
                </button>

                <button
                  onClick={() => setActivePill('grammar')}
                  className={`px-2.5 py-1.5 sm:px-4 sm:py-1.5 rounded-xl transition-all flex items-center gap-1.5 whitespace-nowrap shrink-0 ${
                    activePill === 'grammar'
                      ? 'bg-white dark:bg-slate-700 text-indigo-600 dark:text-indigo-400 shadow-sm font-bold'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                  }`}
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Grammar & Vocabulary</span>
                </button>

                <button
                  onClick={() => setActivePill('cefr')}
                  className={`px-2.5 py-1.5 sm:px-4 sm:py-1.5 rounded-xl transition-all flex items-center gap-1.5 whitespace-nowrap shrink-0 ${
                    activePill === 'cefr'
                      ? 'bg-white dark:bg-slate-700 text-indigo-600 dark:text-indigo-400 shadow-sm font-bold'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                  }`}
                >
                  <Award className="w-3.5 h-3.5" />
                  <span>CEFR Fluency Metrics</span>
                </button>
              </div>

              {/* Live Session Status Indicator */}
              <div className="flex items-center gap-1.5 sm:gap-2 px-2.5 py-1 rounded-full bg-emerald-50 dark:bg-emerald-950/50 border border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-300 text-[10px] sm:text-xs font-semibold self-start sm:self-auto shrink-0">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
                <span>Google Meet Audio Connected</span>
              </div>
            </div>

            {/* Simulated Live Call Window (Livo AI Style) */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 sm:gap-6 pt-4 sm:pt-6 items-center">
              {/* Left Column: Meeting Preview & Participants */}
              <div className="lg:col-span-7 space-y-4">
                {/* Meeting Header Bar */}
                <div className="p-2.5 sm:p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
                  <div className="flex items-center gap-2.5 sm:gap-3 min-w-0">
                    <PlatformIcon platform="google-meet" size={28} />
                    <div className="min-w-0">
                      <h4 className="text-xs sm:text-sm font-bold text-slate-900 dark:text-white leading-tight truncate">
                        Q4 Strategy & Architecture Review
                      </h4>
                      <div className="flex items-center gap-1.5 sm:gap-2 text-[10px] sm:text-[11px] text-slate-400 font-mono">
                        <span className="truncate max-w-[130px] sm:max-w-none">meet.google.com/xyz</span>
                        <span>•</span>
                        <span className="text-rose-500 font-bold flex items-center gap-1 shrink-0">
                          <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-pulse" />
                          00:18:42
                        </span>
                      </div>
                    </div>
                  </div>

                  <span className="px-2 py-0.5 sm:px-2.5 sm:py-1 rounded-lg bg-indigo-100 dark:bg-indigo-950/80 text-indigo-700 dark:text-indigo-300 text-[10px] sm:text-xs font-bold shrink-0 self-start sm:self-auto">
                    4 Active Speakers
                  </span>
                </div>

                {/* Participant Avatars & Live Audio Node Visualizer */}
                <div className="relative p-3.5 sm:p-5 rounded-2xl bg-gradient-to-b from-slate-50 to-slate-100/60 dark:from-slate-800/40 dark:to-slate-900/60 border border-slate-200/80 dark:border-slate-700/80 overflow-hidden">
                  <div className="text-[9px] sm:text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2.5 flex items-center justify-between gap-1">
                    <span>Live Speaker Diarization</span>
                    <span className="text-indigo-600 dark:text-indigo-400 font-medium truncate">Voice Fingerprint</span>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-3">
                    {/* You (Speaking Now) */}
                    <div className="p-2 sm:p-3 rounded-xl bg-white dark:bg-slate-800 border-2 border-indigo-500 shadow-md space-y-1 relative">
                      <div className="absolute -top-1.5 right-1.5 px-1.5 py-0.2 rounded-full bg-indigo-600 text-white font-bold text-[8px] uppercase">
                        Speaking
                      </div>
                      <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-indigo-600 text-white font-bold flex items-center justify-center text-xs sm:text-sm shadow">
                        You
                      </div>
                      <div className="text-[11px] sm:text-xs font-bold text-slate-900 dark:text-white truncate">Priya (You)</div>
                      <div className="text-[9px] sm:text-[10px] text-emerald-600 dark:text-emerald-400 font-medium flex items-center gap-1 truncate">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping shrink-0" />
                        Fluency: 94%
                      </div>
                    </div>

                    {/* Liam */}
                    <div className="p-2 sm:p-3 rounded-xl bg-white/70 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 space-y-1">
                      <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-purple-500 text-white font-bold flex items-center justify-center text-xs sm:text-sm">
                        LK
                      </div>
                      <div className="text-[11px] sm:text-xs font-bold text-slate-900 dark:text-white truncate">Liam Kane</div>
                      <div className="text-[9px] sm:text-[10px] text-slate-400 truncate">London, UK</div>
                    </div>

                    {/* Elena */}
                    <div className="p-2 sm:p-3 rounded-xl bg-white/70 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 space-y-1">
                      <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-emerald-500 text-white font-bold flex items-center justify-center text-xs sm:text-sm">
                        ER
                      </div>
                      <div className="text-[11px] sm:text-xs font-bold text-slate-900 dark:text-white truncate">Elena R.</div>
                      <div className="text-[9px] sm:text-[10px] text-slate-400 truncate">Berlin, DE</div>
                    </div>

                    {/* Marcus */}
                    <div className="p-2 sm:p-3 rounded-xl bg-white/70 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 space-y-1">
                      <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-amber-500 text-white font-bold flex items-center justify-center text-xs sm:text-sm">
                        MV
                      </div>
                      <div className="text-[11px] sm:text-xs font-bold text-slate-900 dark:text-white truncate">Marcus V.</div>
                      <div className="text-[9px] sm:text-[10px] text-slate-400 truncate">SF, US</div>
                    </div>
                  </div>

                  {/* Real-Time Waveform Equalizer */}
                  <div className="mt-3 pt-2.5 border-t border-slate-200 dark:border-slate-700 flex items-center justify-between text-xs">
                    <div className="flex items-center gap-1.5">
                      <Volume2 className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
                      <span className="text-[10px] sm:text-[11px] font-semibold text-slate-700 dark:text-slate-300">
                        Voice Clarity:
                      </span>
                    </div>

                    {/* Animated Waveform Bars */}
                    <div className="flex items-center gap-0.5 sm:gap-1 h-4 sm:h-5">
                      {[40, 75, 95, 60, 85, 30, 90, 100, 70, 50, 80, 65, 95, 45, 80, 90].map((h, i) => (
                        <span
                          key={i}
                          className={`w-0.5 sm:w-1 rounded-full bg-indigo-500 transition-all duration-300 ${i > 9 ? 'hidden sm:inline-block' : ''}`}
                          style={{
                            height: `${h}%`,
                            opacity: (i % 2 === 0 ? 0.9 : 0.6),
                          }}
                        />
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Right Column: AI Co-Pilot Bubble & Live Coaching Widget */}
              <div className="lg:col-span-5 space-y-3 sm:space-y-3.5">
                {/* Speech Transcript & AI Correction Box */}
                <div className="p-3 sm:p-4 rounded-2xl bg-gradient-to-br from-indigo-50/90 to-purple-50/70 dark:from-indigo-950/40 dark:to-purple-950/30 border border-indigo-200/80 dark:border-indigo-900/80 space-y-2.5 sm:space-y-3 shadow-md">
                  <div className="flex items-center justify-between">
                    <span className="text-[9px] sm:text-[10px] font-bold text-indigo-700 dark:text-indigo-400 uppercase tracking-wider flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5" />
                      Live AI Coaching Feedback
                    </span>
                    <span className="text-[9px] sm:text-[10px] font-mono text-slate-400">0.2s</span>
                  </div>

                  {/* Original Spoken Utterance */}
                  <div className="p-2 sm:p-2.5 rounded-xl bg-white/90 dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 text-[11px] sm:text-xs">
                    <span className="text-[9px] sm:text-[10px] font-semibold text-slate-400 block mb-0.5">What you just said:</span>
                    <p className="text-slate-800 dark:text-slate-200 font-medium">
                      "I think we <span className="bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300 px-1 py-0.5 rounded font-semibold underline decoration-wavy decoration-amber-500">must to discuss about</span> the budget before deploying."
                    </p>
                  </div>

                  {/* AI Instant Recommendation */}
                  <div className="p-2.5 sm:p-3 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800 text-[11px] sm:text-xs space-y-1">
                    <div className="flex items-center gap-1.5 font-bold text-emerald-800 dark:text-emerald-300">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                      <span>Better Native Phrasing:</span>
                    </div>
                    <p className="text-emerald-900 dark:text-emerald-200 font-semibold text-xs sm:text-[13px] leading-snug">
                      "We should address the budget allocation before deployment."
                    </p>
                    <p className="text-[9px] sm:text-[10px] text-emerald-700 dark:text-emerald-400 pt-0.5">
                      💡 Tip: "Discuss" doesn't take "about". Using "address" sounds more decisive.
                    </p>
                  </div>
                </div>

                {/* CEFR Fluency Score Preview Pill */}
                <div className="grid grid-cols-3 gap-1.5 sm:gap-2">
                  <div className="p-2 sm:p-3 rounded-xl bg-slate-50 dark:bg-slate-800/70 border border-slate-200/80 dark:border-slate-700 text-center">
                    <span className="text-[8px] sm:text-[10px] text-slate-400 uppercase font-semibold block truncate">CEFR Band</span>
                    <span className="text-base sm:text-lg font-black text-indigo-600 dark:text-indigo-400">C1</span>
                    <span className="text-[8px] sm:text-[9px] text-slate-400 block truncate">Proficient</span>
                  </div>

                  <div className="p-2 sm:p-3 rounded-xl bg-slate-50 dark:bg-slate-800/70 border border-slate-200/80 dark:border-slate-700 text-center">
                    <span className="text-[8px] sm:text-[10px] text-slate-400 uppercase font-semibold block truncate">Speaking Pace</span>
                    <span className="text-base sm:text-lg font-black text-emerald-600 dark:text-emerald-400">138</span>
                    <span className="text-[8px] sm:text-[9px] text-slate-400 block truncate">wpm (Ideal)</span>
                  </div>

                  <div className="p-2 sm:p-3 rounded-xl bg-slate-50 dark:bg-slate-800/70 border border-slate-200/80 dark:border-slate-700 text-center">
                    <span className="text-[8px] sm:text-[10px] text-slate-400 uppercase font-semibold block truncate">Filler Words</span>
                    <span className="text-base sm:text-lg font-black text-amber-600 dark:text-amber-400">1.8%</span>
                    <span className="text-[8px] sm:text-[9px] text-slate-400 block truncate">Low</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
