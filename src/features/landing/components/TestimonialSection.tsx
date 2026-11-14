import React, { useState } from 'react';
import { Star, ChevronLeft, ChevronRight, Quote } from 'lucide-react';
import { Testimonial } from '../types';

const TESTIMONIALS: Testimonial[] = [
  {
    id: '1',
    quote:
      'FluentMeet completely transformed our engineering syncs. Our developers across Tokyo, Berlin, and Bangalore now pitch technical designs with immense confidence. It’s like having an executive speech coach sitting right beside you in Google Meet.',
    author: 'Joey Wang Sandra',
    role: 'VP of Engineering',
    company: 'CloudWave Global',
    avatar: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=256&q=80',
    rating: 5,
    verified: true,
  },
  {
    id: '2',
    quote:
      'I was always anxious about speaking up in global leadership syncs because of grammatical slips. In just 3 weeks with FluentMeet, my speaking pace stabilized at 140 WPM, and I finally stopped using filler words. I was promoted to Principal PM last month!',
    author: 'Rajiv Mukherjee',
    role: 'Principal Product Manager',
    company: 'Fintech Solutions UK',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=256&q=80',
    rating: 5,
    verified: true,
  },
  {
    id: '3',
    quote:
      'Preparing for US tech interviews as a non-native speaker was terrifying. FluentMeet analyzed my mock recordings, pointed out repetitive phrasing, and taught me STAR framework answers. I landed an L6 offer at a Silicon Valley giant.',
    author: 'Elena Gomez',
    role: 'Senior Staff SRE',
    company: 'DataPlatform Corp',
    avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=256&q=80',
    rating: 5,
    verified: true,
  },
];

export const TestimonialSection: React.FC = () => {
  const [index, setIndex] = useState(0);
  const current = TESTIMONIALS[index];

  const handlePrev = () => {
    setIndex((prev) => (prev === 0 ? TESTIMONIALS.length - 1 : prev - 1));
  };

  const handleNext = () => {
    setIndex((prev) => (prev === TESTIMONIALS.length - 1 ? 0 : prev + 1));
  };

  return (
    <section className="py-20 md:py-28 relative overflow-hidden">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="p-8 sm:p-14 rounded-3xl bg-gradient-to-br from-indigo-50/80 via-white to-purple-50/80 dark:from-slate-800/80 dark:via-slate-900/90 dark:to-indigo-950/40 border border-slate-200 dark:border-slate-800 shadow-2xl relative">
          <Quote className="absolute top-8 right-8 w-16 h-16 text-indigo-200/40 dark:text-indigo-800/20 pointer-events-none" />

          {/* Rating Stars */}
          <div className="flex items-center gap-1 mb-6">
            {[...Array(current.rating)].map((_, i) => (
              <Star key={i} className="w-5 h-5 fill-amber-400 text-amber-400" />
            ))}
            <span className="text-xs font-bold text-slate-500 ml-2">5.0 Star Rating</span>
          </div>

          {/* Quote Typography (Calliom Style) */}
          <blockquote className="text-xl sm:text-2xl md:text-3xl font-medium text-slate-900 dark:text-white leading-relaxed tracking-tight mb-8">
            "{current.quote}"
          </blockquote>

          {/* Author Meta & Controls */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-6 border-t border-slate-200/80 dark:border-slate-800">
            <div className="flex items-center gap-3.5">
              <img
                src={current.avatar}
                alt={current.author}
                className="w-12 h-12 rounded-full object-cover border-2 border-indigo-400 shadow-sm"
              />
              <div>
                <h5 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
                  <span>{current.author}</span>
                  {current.verified && (
                    <span className="text-[10px] bg-indigo-100 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400 px-1.5 py-0.2 rounded font-semibold">
                      Verified User
                    </span>
                  )}
                </h5>
                <span className="text-xs text-slate-500 dark:text-slate-400">
                  {current.role} • <span className="font-semibold text-slate-700 dark:text-slate-300">{current.company}</span>
                </span>
              </div>
            </div>

            {/* Carousel Nav Buttons */}
            <div className="flex items-center gap-2">
              <button
                onClick={handlePrev}
                className="p-2.5 rounded-full border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 hover:border-indigo-500 transition-colors"
                aria-label="Previous testimonial"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                onClick={handleNext}
                className="p-2.5 rounded-full border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 hover:border-indigo-500 transition-colors"
                aria-label="Next testimonial"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
