import React, { useState, useEffect } from 'react';
import {
  Play,
  Pause,
  RotateCcw,
  Volume2,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  Award,
  Mic,
  ArrowRight
} from 'lucide-react';

interface DemoSnippet {
  id: string;
  title: string;
  speaker: string;
  role: string;
  duration: string;
  originalText: string;
  highlightMistake: string;
  correction: string;
  explanation: string;
  fluencyScore: number;
  cefrLevel: string;
}

const DEMO_SNIPPETS: DemoSnippet[] = [
  {
    id: 'sprint',
    title: 'Sprint Planning & Architecture Sync',
    speaker: 'Priya Sharma',
    role: 'Product Lead',
    duration: '0:14',
    originalText: 'We should consider this feature because the client is demanding it since two weeks.',
    highlightMistake: 'since two weeks',
    correction: 'for the past two weeks',
    explanation: 'Use "for" when specifying duration of time, and "since" for a specific point in time.',
    fluencyScore: 92,
    cefrLevel: 'C1',
  },
  {
    id: 'pitch',
    title: 'Executive Stakeholder Presentation',
    speaker: 'Alex Chen',
    role: 'Staff Architect',
    duration: '0:18',
    originalText: 'If we will deploy this now, the downtime might impact the transactions.',
    highlightMistake: 'If we will deploy',
    correction: 'If we deploy this now',
    explanation: 'In first conditional clauses with "if", use the simple present tense instead of "will".',
    fluencyScore: 89,
    cefrLevel: 'B2+',
  },
  {
    id: 'interview',
    title: 'Senior Engineer Technical Interview',
    speaker: 'Marcus Vance',
    role: 'Candidate',
    duration: '0:22',
    originalText: 'I am agree with your approach, but let us look into the throughput bottlenecks.',
    highlightMistake: 'I am agree',
    correction: 'I agree with your approach',
    explanation: '"Agree" is a verb in English, so say "I agree" rather than "I am agree".',
    fluencyScore: 95,
    cefrLevel: 'C1',
  },
];

export const InteractiveAudioDemo: React.FC = () => {
  const [selectedSnippet, setSelectedSnippet] = useState<DemoSnippet>(DEMO_SNIPPETS[0]);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);

  useEffect(() => {
    let timer: number;
    if (isPlaying) {
      timer = window.setInterval(() => {
        setProgress((prev) => {
          if (prev >= 100) {
            setIsPlaying(false);
            return 0;
          }
          return prev + 5;
        });
      }, 200);
    } else {
      setProgress(0);
    }
    return () => clearInterval(timer);
  }, [isPlaying]);

  const togglePlay = () => {
    setIsPlaying(!isPlaying);
  };

  return (
    <section id="live-demo" className="py-20 bg-slate-50/70 dark:bg-slate-900/60 border-y border-slate-200/80 dark:border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-12">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-300 text-xs font-semibold">
            <Volume2 className="w-3.5 h-3.5" />
            <span>Interactive Voice Player</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white tracking-tight">
            Hear the difference AI coaching makes in real calls.
          </h2>
          <p className="text-sm sm:text-base text-slate-600 dark:text-slate-400">
            Click any scenario below to listen to actual meeting audio and observe how FluentMeet catches nuance in real-time.
          </p>
        </div>

        {/* Scenario Switcher Pills */}
        <div className="flex flex-wrap items-center justify-center gap-2 mb-8">
          {DEMO_SNIPPETS.map((s) => (
            <button
              key={s.id}
              onClick={() => {
                setSelectedSnippet(s);
                setIsPlaying(false);
                setProgress(0);
              }}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all border ${
                selectedSnippet.id === s.id
                  ? 'bg-indigo-600 text-white border-indigo-600 shadow-md shadow-indigo-500/20'
                  : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:border-slate-300'
              }`}
            >
              {s.title}
            </button>
          ))}
        </div>

        {/* Audio Player Interactive Card (Calliom Glass Card) */}
        <div className="max-w-3xl mx-auto bg-white dark:bg-slate-800/90 rounded-3xl border border-slate-200 dark:border-slate-700 shadow-2xl p-6 sm:p-8 space-y-6">
          {/* Player Top Meta */}
          <div className="flex items-center justify-between">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-600 dark:text-indigo-400 block">
                Scenario Track
              </span>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white">{selectedSnippet.title}</h3>
              <span className="text-xs text-slate-400">
                Speaker: <span className="font-semibold text-slate-700 dark:text-slate-300">{selectedSnippet.speaker}</span> ({selectedSnippet.role})
              </span>
            </div>

            <div className="text-right">
              <span className="text-2xl font-black text-indigo-600 dark:text-indigo-400">{selectedSnippet.cefrLevel}</span>
              <span className="text-[10px] text-slate-400 block font-medium">CEFR Equivalent</span>
            </div>
          </div>

          {/* Audio Waveform & Play Controller */}
          <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-700/80 flex items-center gap-4">
            <button
              onClick={togglePlay}
              className="w-12 h-12 rounded-2xl bg-indigo-600 hover:bg-indigo-500 text-white flex items-center justify-center shrink-0 shadow-lg shadow-indigo-500/30 transition-transform active:scale-95"
            >
              {isPlaying ? <Pause className="w-5 h-5 fill-current" /> : <Play className="w-5 h-5 fill-current ml-0.5" />}
            </button>

            {/* Simulated Animated Audio Waveform */}
            <div className="flex-1 space-y-1">
              <div className="flex items-center gap-1 h-8">
                {[15, 30, 65, 90, 45, 80, 100, 75, 40, 85, 95, 60, 45, 90, 70, 50, 85, 95, 40, 60, 80, 50, 30, 20].map((h, i) => {
                  const isCurrent = (i / 24) * 100 <= progress;
                  return (
                    <span
                      key={i}
                      className={`flex-1 rounded-full transition-all duration-150 ${
                        isCurrent
                          ? 'bg-indigo-600 dark:bg-indigo-400'
                          : 'bg-slate-200 dark:bg-slate-700'
                      }`}
                      style={{
                        height: isPlaying ? `${Math.max(20, (h * (progress % 20 + 80)) / 100)}%` : `${h}%`,
                      }}
                    />
                  );
                })}
              </div>

              <div className="flex justify-between text-[10px] text-slate-400 font-mono">
                <span>0:00</span>
                <span>{selectedSnippet.duration}</span>
              </div>
            </div>
          </div>

          {/* Transcript with Highlighted Mistake */}
          <div className="p-4 rounded-2xl bg-slate-50/80 dark:bg-slate-900/40 border border-slate-200/80 dark:border-slate-700 space-y-2">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              Live Spoken Utterance
            </span>
            <p className="text-sm text-slate-800 dark:text-slate-200 leading-relaxed font-medium">
              "{selectedSnippet.originalText.split(selectedSnippet.highlightMistake)[0]}
              <span className="bg-rose-100 dark:bg-rose-950/80 text-rose-700 dark:text-rose-300 px-1.5 py-0.5 rounded font-bold underline decoration-wavy decoration-rose-500">
                {selectedSnippet.highlightMistake}
              </span>
              {selectedSnippet.originalText.split(selectedSnippet.highlightMistake)[1]}"
            </p>
          </div>

          {/* AI Correction & Teaching Card */}
          <div className="p-4 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 space-y-2">
            <div className="flex items-center justify-between text-xs font-bold text-emerald-800 dark:text-emerald-300">
              <span className="flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                Recommended Phrasing
              </span>
              <span className="text-[10px] bg-emerald-200 dark:bg-emerald-900 text-emerald-900 dark:text-emerald-100 px-2 py-0.5 rounded-full">
                Native Fluency
              </span>
            </div>
            <p className="text-sm font-bold text-emerald-900 dark:text-emerald-200">
              "{selectedSnippet.correction}"
            </p>
            <p className="text-xs text-emerald-700 dark:text-emerald-400 leading-relaxed">
              💡 {selectedSnippet.explanation}
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};
