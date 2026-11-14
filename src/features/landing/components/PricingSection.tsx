import React, { useState } from 'react';
import {
  Check,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Zap,
  HelpCircle
} from 'lucide-react';
import { PricingPlan } from '../types';

interface PricingSectionProps {
  onSelectPlan: (planId: string) => void;
}

export const PricingSection: React.FC<PricingSectionProps> = ({ onSelectPlan }) => {
  const [isYearly, setIsYearly] = useState<boolean>(true);

  const plans: PricingPlan[] = [
    {
      id: 'free',
      name: 'Free Forever',
      badge: 'Starter',
      description: 'Ideal for trying out the Chrome extension and receiving basic grammar feedback.',
      monthlyPrice: 0,
      yearlyPrice: 0,
      ctaText: 'Get Started Free',
      features: [
        '5 hours meeting audio analysis per month',
        'Google Meet, Zoom & Teams Chrome Extension',
        'Real-time live speech transcription',
        'Basic grammar error detection',
        '7-day session history retention',
        'Community support',
      ],
    },
    {
      id: 'pro',
      name: 'Pro Coach',
      badge: 'Most Popular',
      description: 'Full real-time AI speech coaching, CEFR scoring, and personalized vocabulary drills.',
      monthlyPrice: 24,
      yearlyPrice: 18,
      isPopular: true,
      ctaText: 'Start 14-Day Free Trial',
      features: [
        'Unlimited meeting recording & coaching hours',
        'Gemini 1.5 Pro deep linguistic evaluation',
        'Real-time stealth sidepanel feedback',
        'CEFR (A1-C2) & IELTS Speaking Band calculation',
        'Speech pace & filler word counter (um, uh, like)',
        'Audio clip playback & phonetic pronunciation drills',
        'Unlimited meeting history & cloud export',
        'Personalized error flashcard drills',
        'Priority AI inference queue',
      ],
    },
    {
      id: 'enterprise',
      name: 'Team & Business',
      badge: 'For Global Teams',
      description: 'Comprehensive cross-border communication upgrade for engineering & product orgs.',
      monthlyPrice: 59,
      yearlyPrice: 45,
      ctaText: 'Contact Enterprise Sales',
      features: [
        'Everything in Pro Coach for all team seats',
        'Centralized Team Fluency & Performance Dashboard',
        'Custom company acronym & tech glossary whitelist',
        'Manager oversight & team benchmark reports',
        'HIPAA, GDPR & SOC2 Type II compliance controls',
        'SAML 2.0 / Okta / Azure AD Single Sign-On (SSO)',
        'Dedicated Customer Success & onboarding lead',
      ],
    },
  ];

  return (
    <section id="pricing" className="py-20 md:py-28 bg-slate-50/50 dark:bg-slate-900/40 border-t border-slate-200/80 dark:border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-12">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-50 dark:bg-indigo-950/60 border border-indigo-200 dark:border-indigo-800 text-indigo-700 dark:text-indigo-300 text-xs font-semibold">
            <Zap className="w-3.5 h-3.5" />
            <span>Transparent Pricing</span>
          </div>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-black text-slate-900 dark:text-white tracking-tight">
            Invest in your global career confidence.
          </h2>
          <p className="text-base text-slate-600 dark:text-slate-400">
            Start free with no credit card required. Upgrade when you need unlimited deep coaching.
          </p>

          {/* Billing Interval Toggle (Livo AI Style) */}
          <div className="pt-4 flex items-center justify-center gap-3">
            <span className={`text-xs font-semibold ${!isYearly ? 'text-slate-900 dark:text-white' : 'text-slate-400'}`}>
              Monthly
            </span>
            <button
              type="button"
              onClick={() => setIsYearly(!isYearly)}
              className="w-13 h-7 rounded-full bg-indigo-600 p-1 flex items-center transition-colors relative cursor-pointer"
              aria-label="Toggle annual billing"
            >
              <div
                className={`w-5 h-5 rounded-full bg-white shadow-md transition-transform ${
                  isYearly ? 'translate-x-6' : 'translate-x-0'
                }`}
              />
            </button>
            <span className={`text-xs font-semibold flex items-center gap-1.5 ${isYearly ? 'text-slate-900 dark:text-white' : 'text-slate-400'}`}>
              <span>Yearly</span>
              <span className="px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950/80 text-emerald-700 dark:text-emerald-300 text-[10px] font-bold">
                Save 25%
              </span>
            </span>
          </div>
        </div>

        {/* Pricing Cards Grid (Livo AI & Calliom Style) */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-stretch max-w-6xl mx-auto">
          {plans.map((p) => {
            const price = isYearly ? p.yearlyPrice : p.monthlyPrice;
            const isPro = p.isPopular;

            return (
              <div
                key={p.id}
                className={`relative rounded-3xl p-6 sm:p-8 flex flex-col justify-between transition-all duration-300 ${
                  isPro
                    ? 'bg-slate-900 text-white dark:bg-indigo-950/70 border-2 border-indigo-500 shadow-2xl shadow-indigo-500/25 scale-[1.03] z-10'
                    : 'bg-white dark:bg-slate-800 text-slate-900 dark:text-white border border-slate-200 dark:border-slate-700 shadow-lg hover:shadow-xl'
                }`}
              >
                {/* Popular Pill */}
                {isPro && (
                  <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 px-3.5 py-1 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 text-white text-[11px] font-black uppercase tracking-wider shadow-md">
                    ⭐ Top Choice
                  </div>
                )}

                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h4 className="text-lg font-bold">{p.name}</h4>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-md ${
                        isPro ? 'bg-white/15 text-indigo-300' : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300'
                      }`}
                    >
                      {p.badge}
                    </span>
                  </div>

                  <p className={`text-xs ${isPro ? 'text-slate-300' : 'text-slate-500 dark:text-slate-400'}`}>
                    {p.description}
                  </p>

                  {/* Price */}
                  <div className="pt-2">
                    <span className="text-4xl sm:text-5xl font-black tracking-tight">${price}</span>
                    <span className={`text-xs ml-1.5 ${isPro ? 'text-slate-400' : 'text-slate-500'}`}>
                      / month {isYearly && price > 0 ? '(billed annually)' : ''}
                    </span>
                  </div>

                  {/* Feature Checklist */}
                  <div className="pt-4 border-t border-slate-200/30 dark:border-slate-700 space-y-2.5">
                    <span className={`text-[10px] uppercase font-bold tracking-wider ${isPro ? 'text-indigo-300' : 'text-slate-400'}`}>
                      Included capabilities
                    </span>
                    {p.features.map((feat, i) => (
                      <div key={i} className="flex items-start gap-2.5 text-xs">
                        <Check className={`w-4 h-4 shrink-0 mt-0.5 ${isPro ? 'text-emerald-400' : 'text-indigo-600 dark:text-indigo-400'}`} />
                        <span className={isPro ? 'text-slate-200' : 'text-slate-600 dark:text-slate-300'}>{feat}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* CTA Button */}
                <div className="pt-8">
                  <button
                    onClick={() => onSelectPlan(p.id)}
                    className={`w-full py-3.5 px-4 rounded-xl font-bold text-xs flex items-center justify-center gap-2 transition-all ${
                      isPro
                        ? 'bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-400 hover:to-purple-500 text-white shadow-lg shadow-indigo-500/30 hover:scale-[1.02]'
                        : 'bg-slate-100 hover:bg-slate-200 dark:bg-slate-700 dark:hover:bg-slate-600 text-slate-900 dark:text-white'
                    }`}
                  >
                    <span>{p.ctaText}</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        {/* Enterprise Compliance Assurance */}
        <div className="mt-16 text-center text-xs text-slate-400 flex flex-wrap items-center justify-center gap-6">
          <span className="flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-500" />
            Zero training on customer audio without opt-in
          </span>
          <span className="flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-500" />
            256-bit AES encryption at rest & in-transit
          </span>
          <span className="flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-500" />
            Cancel anytime with 1-click
          </span>
        </div>
      </div>
    </section>
  );
};
