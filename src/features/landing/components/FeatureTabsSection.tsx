import React, { useState } from 'react';
import {
  CheckCircle2,
  Sparkles,
  Mic,
  FileText,
  Clock,
  Layers,
  Award,
  Zap,
  ArrowRight,
  TrendingUp,
  BookOpen
} from 'lucide-react';
import { FeatureTabItem } from '../types';

export const FeatureTabsSection: React.FC = () => {
  const [activeTabId, setActiveTabId] = useState<'prepare' | 'live' | 'followup'>('live');

  const tabContent: Record<string, FeatureTabItem> = {
    prepare: {
      id: 'prepare',
      title: 'Prepare With Confidence',
      badge: 'Before Meeting',
      headline: 'Never stumble over industry vocabulary or opening arguments',
      description:
        'Upload your agenda or paste meeting topics. FluentMeet generates high-impact English talking points, executive phrasing, and idioms tailored to your industry.',
      bullets: [
        'AI Agenda Primer with C1/C2 executive phrasing',
        'Industry vocabulary flashcards (Tech, Finance, Health, Design)',
        'Pronunciation warm-up before entering the call',
        'Anticipated stakeholder questions & polished answers',
      ],
      mockupTag: 'Pre-Meeting Briefing Dossier',
    },
    live: {
      id: 'live',
      title: 'Stay Engaged Live',
      badge: 'During Meeting (Sidepanel)',
      headline: 'Discreet, real-time coaching without breaking your conversational flow',
      description:
        'As you speak, the lightweight Chrome extension transcribes your voice, measures your pace, counts filler words, and flashes discreet suggestions right in your sidepanel.',
      bullets: [
        'Subtle grammar nudges visible only to you',
        'Real-time Speaking Pace monitor (ideal 120-150 WPM)',
        'Filler word alert (um, uh, you know, like) with live counter',
        'Dual-stream tab capture: separates your speech from teammates',
      ],
      mockupTag: 'Live Chrome Sidepanel Overlay',
    },
    followup: {
      id: 'followup',
      title: 'Follow Up Effortlessly',
      badge: 'After Meeting',
      headline: 'CEFR scorecards, grammar flashcards & audio mistake drills',
      description:
        'Within seconds after ending your call, view a comprehensive meeting report with grammar analysis, audio playback of mispronounced words, and customized practice quizzes.',
      bullets: [
        'Official CEFR score (A1 to C2) & IELTS Speaking Band estimate',
        'Audio clip playback for every caught grammatical slip',
        '1-Click Interactive Practice Drills to reinforce learning',
        'Automated executive meeting minutes and action items export',
      ],
      mockupTag: 'Comprehensive Post-Call Analysis Report',
    },
  };

  const current = tabContent[activeTabId];

  return (
    <section id="how-it-works" className="py-20 md:py-28">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-12">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-50 dark:bg-indigo-950/60 border border-indigo-200 dark:border-indigo-800 text-indigo-700 dark:text-indigo-300 text-xs font-semibold">
            <Layers className="w-3.5 h-3.5 text-indigo-500" />
            <span>End-to-End Meeting Workflow</span>
          </div>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-black text-slate-900 dark:text-white tracking-tight">
            FluentMeet supports you before, during, and after every meeting.
          </h2>
          <p className="text-base text-slate-600 dark:text-slate-400">
            Engineered specifically for non-native English speakers working in global tech, enterprise, and consulting teams.
          </p>
        </div>

        {/* Tab Buttons (Ai Notely Style) */}
        <div className="flex justify-center mb-10">
          <div className="inline-flex p-1.5 bg-slate-100 dark:bg-slate-800/80 rounded-2xl border border-slate-200/80 dark:border-slate-700 shadow-sm max-w-full overflow-x-auto">
            {(['prepare', 'live', 'followup'] as const).map((id) => {
              const item = tabContent[id];
              const isActive = activeTabId === id;
              return (
                <button
                  key={id}
                  onClick={() => setActiveTabId(id)}
                  className={`px-5 py-2.5 rounded-xl text-xs sm:text-sm font-bold transition-all whitespace-nowrap flex items-center gap-2 ${
                    isActive
                      ? 'bg-white dark:bg-slate-700 text-indigo-600 dark:text-white shadow-md'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                  }`}
                >
                  {id === 'prepare' && <BookOpen className="w-4 h-4" />}
                  {id === 'live' && <Mic className="w-4 h-4" />}
                  {id === 'followup' && <Award className="w-4 h-4" />}
                  <span>{item.title}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Feature Display Card */}
        <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-xl overflow-hidden p-6 sm:p-10 transition-all duration-300">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center">
            {/* Left Content Column */}
            <div className="lg:col-span-6 space-y-6">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-50 dark:bg-purple-950/60 border border-purple-200 dark:border-purple-800 text-purple-700 dark:text-purple-300 text-xs font-bold">
                <Sparkles className="w-3.5 h-3.5" />
                <span>{current.badge}</span>
              </div>

              <h3 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white leading-tight">
                {current.headline}
              </h3>

              <p className="text-sm sm:text-base text-slate-600 dark:text-slate-400 leading-relaxed">
                {current.description}
              </p>

              {/* Bullet Points */}
              <div className="space-y-3 pt-2">
                {current.bullets.map((b, idx) => (
                  <div key={idx} className="flex items-start gap-3">
                    <div className="w-5 h-5 rounded-full bg-emerald-100 dark:bg-emerald-950/80 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0 mt-0.5">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                    </div>
                    <span className="text-sm font-medium text-slate-700 dark:text-slate-300">{b}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Right Interactive Mockup Display */}
            <div className="lg:col-span-6">
              <div className="relative p-6 rounded-2xl bg-gradient-to-br from-indigo-50/80 via-white to-purple-50/60 dark:from-slate-800/70 dark:via-slate-900 dark:to-indigo-950/40 border border-indigo-100 dark:border-slate-700 shadow-inner space-y-4">
                <div className="flex items-center justify-between border-b border-slate-200/80 dark:border-slate-700 pb-3">
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full bg-rose-500" />
                    <span className="w-3 h-3 rounded-full bg-amber-500" />
                    <span className="w-3 h-3 rounded-full bg-emerald-500" />
                  </div>
                  <span className="text-xs font-mono font-bold text-slate-500 dark:text-slate-400">
                    {current.mockupTag}
                  </span>
                </div>

                {activeTabId === 'prepare' && (
                  <div className="space-y-3 text-xs">
                    <div className="p-3 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 space-y-1">
                      <span className="text-[10px] uppercase font-bold text-indigo-600 dark:text-indigo-400">
                        Agenda Goal: Lead Architectural Sign-off
                      </span>
                      <p className="font-semibold text-slate-800 dark:text-slate-200">
                        Key Talking Point: "We advocate for an event-driven decoupled service to mitigate latency under peak holiday traffic."
                      </p>
                    </div>

                    <div className="grid grid-cols-2 gap-2">
                      <div className="p-2.5 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
                        <span className="text-[10px] text-slate-400 font-semibold block">Executive Synonym</span>
                        <span className="font-bold text-slate-900 dark:text-white">"Spearhead"</span>
                        <span className="text-[9px] text-slate-500 block">instead of "lead"</span>
                      </div>
                      <div className="p-2.5 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
                        <span className="text-[10px] text-slate-400 font-semibold block">Idiom of the Day</span>
                        <span className="font-bold text-slate-900 dark:text-white">"Move the needle"</span>
                        <span className="text-[9px] text-slate-500 block">meaningful progress</span>
                      </div>
                    </div>
                  </div>
                )}

                {activeTabId === 'live' && (
                  <div className="space-y-3 text-xs">
                    <div className="p-3 rounded-xl bg-indigo-600 text-white space-y-1 shadow-md">
                      <div className="flex items-center justify-between text-[10px] opacity-80">
                        <span>Sidepanel Live Coach</span>
                        <span className="flex items-center gap-1 font-bold">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-300 animate-ping" />
                          Listening
                        </span>
                      </div>
                      <div className="text-xs font-medium">
                        "Your pace is currently 142 WPM. You used 0 filler words in the last 3 minutes!"
                      </div>
                    </div>

                    <div className="p-3 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 space-y-1.5">
                      <div className="flex justify-between items-center text-[10px]">
                        <span className="font-bold text-slate-500 uppercase">Live Grammar Alert</span>
                        <span className="text-emerald-600 font-bold">Corrected</span>
                      </div>
                      <p className="text-slate-700 dark:text-slate-300">
                        <span className="line-through text-rose-500 mr-1">"According to me"</span>
                        <span className="font-bold text-emerald-600 dark:text-emerald-400">"In my perspective"</span>
                      </p>
                    </div>
                  </div>
                )}

                {activeTabId === 'followup' && (
                  <div className="space-y-3 text-xs">
                    <div className="p-3 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 flex items-center justify-between">
                      <div>
                        <span className="text-[10px] text-slate-400 font-bold uppercase block">Meeting CEFR Score</span>
                        <span className="text-xl font-black text-indigo-600 dark:text-indigo-400">C1 Advanced (88/100)</span>
                      </div>
                      <div className="px-3 py-1 rounded-full bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 font-bold text-xs">
                        +4 pts vs Last Week
                      </div>
                    </div>

                    <div className="p-3 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 space-y-1">
                      <span className="text-[10px] text-slate-400 font-bold uppercase block">Interactive Flashcard Drill</span>
                      <div className="flex items-center justify-between font-semibold text-slate-800 dark:text-slate-200">
                        <span>Mispronounced: "Hierarchy"</span>
                        <span className="text-indigo-600 font-bold hover:underline cursor-pointer">Listen Audio 🔊</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
