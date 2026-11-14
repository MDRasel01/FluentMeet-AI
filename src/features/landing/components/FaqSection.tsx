import React, { useState } from 'react';
import { ChevronDown, HelpCircle } from 'lucide-react';

interface FaqItem {
  q: string;
  a: string;
}

const FAQS: FaqItem[] = [
  {
    q: 'Do other meeting participants know that FluentMeet is analyzing my English?',
    a: 'No. FluentMeet runs completely in your private Chrome Extension sidepanel or local window. It does not invite any external bot or AI attendee to your meeting call, and only you see your real-time feedback and metrics.',
  },
  {
    q: 'How does FluentMeet capture audio from Google Meet, Zoom, and Teams?',
    a: 'FluentMeet uses standard Chrome tab capture APIs alongside your microphone input. It cleanly separates your own voice from remote speakers (speaker diarization) so your feedback is strictly focused on your spoken English.',
  },
  {
    q: 'Does it work if I don’t have a local backend server running?',
    a: 'Yes! FluentMeet includes a built-in client-side Web Speech recognition engine. You can practice, test your voice, and analyze spoken utterances right inside Google Chrome even without an external backend.',
  },
  {
    q: 'Is my meeting conversation data kept private and secure?',
    a: 'Absolutely. We comply with GDPR and SOC2 Type II standards. Meeting transcripts and audio clips are encrypted with AES-256 and are never used to train public AI models without explicit enterprise opt-in.',
  },
  {
    q: 'What is the CEFR scoring system used in the reports?',
    a: 'The Common European Framework of Reference (CEFR) grades language proficiency from A1 (Beginner) to C2 (Mastery). FluentMeet evaluates your spoken grammar complexity, vocabulary richness, and coherence to calculate your exact CEFR band and IELTS Speaking equivalent.',
  },
];

export const FaqSection: React.FC = () => {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  const toggle = (idx: number) => {
    setOpenIndex(openIndex === idx ? null : idx);
  };

  return (
    <section className="py-20 md:py-28 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="text-center space-y-3 mb-12">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs font-semibold">
          <HelpCircle className="w-3.5 h-3.5 text-indigo-500" />
          <span>Frequently Asked Questions</span>
        </div>
        <h2 className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white tracking-tight">
          Everything you need to know.
        </h2>
      </div>

      <div className="space-y-3">
        {FAQS.map((faq, idx) => {
          const isOpen = openIndex === idx;
          return (
            <div
              key={idx}
              className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 overflow-hidden shadow-sm transition-all"
            >
              <button
                type="button"
                onClick={() => toggle(idx)}
                className="w-full p-5 text-left flex items-center justify-between gap-4 font-bold text-sm sm:text-base text-slate-900 dark:text-white hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
              >
                <span>{faq.q}</span>
                <ChevronDown
                  className={`w-4 h-4 text-slate-400 shrink-0 transition-transform duration-200 ${
                    isOpen ? 'rotate-180 text-indigo-600' : ''
                  }`}
                />
              </button>

              {isOpen && (
                <div className="px-5 pb-5 text-xs sm:text-sm text-slate-600 dark:text-slate-400 leading-relaxed border-t border-slate-100 dark:border-slate-800/60 pt-3 animate-in fade-in duration-200">
                  {faq.a}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
};
