import React, { useState } from 'react';
import {
  Code2,
  Briefcase,
  GraduationCap,
  TrendingUp,
  CheckCircle2,
  Users,
  Building,
  Target
} from 'lucide-react';

interface UseCase {
  id: string;
  title: string;
  icon: React.ReactNode;
  tag: string;
  headline: string;
  description: string;
  bullets: string[];
  stat: string;
  statLabel: string;
}

const USE_CASES: UseCase[] = [
  {
    id: 'engineers',
    title: 'Software Engineers & Tech Leads',
    icon: <Code2 className="w-5 h-5 text-indigo-500" />,
    tag: 'Technical Communication',
    headline: 'Articulate complex architecture without stumbling over English terms',
    description:
      'Engineers often know the technical solution deeply but struggle to explain trade-offs decisively in English. FluentMeet coaches you on concise explanations and decisive phrasing during sprint syncs and design reviews.',
    bullets: [
      'Concise phrasing for code reviews and trade-off debates',
      'Eliminates passive hesitations ("maybe we can try...")',
      'Domain terms for distributed systems, cloud & security',
      'Confidence in cross-timezone standups with US/EU leads',
    ],
    stat: '42%',
    statLabel: 'Higher technical interview pass rate',
  },
  {
    id: 'pm',
    title: 'Product Managers & Executives',
    icon: <Briefcase className="w-5 h-5 text-purple-500" />,
    tag: 'Leadership & Influence',
    headline: 'Command cross-functional stakeholder rooms with authority',
    description:
      'Influence stakeholders and lead client discovery calls with assertive, polished executive presence. FluentMeet gives you high-impact synonyms, reduces rambling, and sharpens your messaging.',
    bullets: [
      'Assertive vocabulary for executive alignment',
      'Pacing coaching to avoid fast, rushed non-native delivery',
      'Clear structured framing (Situation, Complication, Resolution)',
      'Automated executive recap notes for follow-ups',
    ],
    stat: '85%',
    statLabel: 'Reported greater stakeholder confidence',
  },
  {
    id: 'interviews',
    title: 'Job Seekers & Global Candidates',
    icon: <GraduationCap className="w-5 h-5 text-pink-500" />,
    tag: 'Interview Coaching',
    headline: 'Ace FAANG & global remote job interviews in English',
    description:
      'Practice answering behavioral and scenario questions using STAR methodology. Get immediate feedback on grammar, filler words, and whether your answers sound natural to native hiring managers.',
    bullets: [
      'STAR method response framework validation',
      'Reduces filler words (um, ah, like, you know) below 2%',
      'Customized feedback on past interview recording files',
      'IELTS Speaking 7.5+ equivalent vocabulary drills',
    ],
    stat: '3.2x',
    statLabel: 'More job offers received',
  },
];

export const UseCasesSection: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('engineers');
  const current = USE_CASES.find((u) => u.id === activeTab) || USE_CASES[0];

  return (
    <section id="use-cases" className="py-20 md:py-28">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-12">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-pink-50 dark:bg-pink-950/60 border border-pink-200 dark:border-pink-800 text-pink-700 dark:text-pink-300 text-xs font-semibold">
            <Target className="w-3.5 h-3.5" />
            <span>Targeted Scenarios</span>
          </div>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-black text-slate-900 dark:text-white tracking-tight">
            Tailored to your professional career goals.
          </h2>
          <p className="text-base text-slate-600 dark:text-slate-400">
            Whether leading high-stakes team syncs or cracking your dream global job offer, FluentMeet accelerates your professional English.
          </p>
        </div>

        {/* Tab Selection */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-10">
          {USE_CASES.map((uc) => {
            const isActive = activeTab === uc.id;
            return (
              <button
                key={uc.id}
                onClick={() => setActiveTab(uc.id)}
                className={`p-4 rounded-2xl border text-left transition-all flex items-start gap-3.5 ${
                  isActive
                    ? 'border-indigo-600 bg-white dark:bg-slate-800 shadow-lg shadow-indigo-500/10 dark:border-indigo-500'
                    : 'border-slate-200 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-900/40 hover:border-slate-300 dark:hover:border-slate-700'
                }`}
              >
                <div className={`p-2.5 rounded-xl ${isActive ? 'bg-indigo-50 dark:bg-indigo-950 text-indigo-600' : 'bg-slate-100 dark:bg-slate-800 text-slate-500'}`}>
                  {uc.icon}
                </div>
                <div>
                  <h4 className="text-sm font-bold text-slate-900 dark:text-white">{uc.title}</h4>
                  <span className="text-[11px] text-slate-400">{uc.tag}</span>
                </div>
              </button>
            );
          })}
        </div>

        {/* Active Use Case Deep Dive Card */}
        <div className="bg-gradient-to-br from-indigo-900 via-slate-900 to-purple-950 text-white rounded-3xl p-8 sm:p-12 shadow-2xl relative overflow-hidden">
          {/* Subtle Glows */}
          <div className="absolute top-0 right-0 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl pointer-events-none" />

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center relative z-10">
            <div className="lg:col-span-8 space-y-5">
              <span className="inline-block px-3 py-1 rounded-full bg-white/10 text-indigo-300 font-bold text-xs uppercase tracking-wider">
                {current.tag}
              </span>
              <h3 className="text-2xl sm:text-3xl font-black tracking-tight leading-tight">
                {current.headline}
              </h3>
              <p className="text-sm sm:text-base text-slate-300 leading-relaxed max-w-2xl">
                {current.description}
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-3">
                {current.bullets.map((b, i) => (
                  <div key={i} className="flex items-center gap-2.5 text-xs text-slate-200 font-medium">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                    <span>{b}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="lg:col-span-4 bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/15 text-center space-y-2">
              <span className="text-5xl font-black text-amber-300 block">{current.stat}</span>
              <h5 className="text-sm font-bold text-white">{current.statLabel}</h5>
              <p className="text-[11px] text-slate-300 pt-1">
                Measured across 2,400+ professionals after 30 days of active meeting coaching.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
