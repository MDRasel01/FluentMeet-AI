import React from 'react';
import { Navbar } from './components/Navbar';
import { HeroSection } from './components/HeroSection';
import { LogosTicker } from './components/LogosTicker';
import { FeatureTabsSection } from './components/FeatureTabsSection';
import { InteractiveAudioDemo } from './components/InteractiveAudioDemo';
import { UseCasesSection } from './components/UseCasesSection';
import { PricingSection } from './components/PricingSection';
import { TestimonialSection } from './components/TestimonialSection';
import { FaqSection } from './components/FaqSection';
import { Footer } from './components/Footer';
import { AuthModal } from './components/AuthModal';
import { useAuth } from './useAuth';
import { AuthMode, AuthUser } from './types';

interface LandingPageProps {
  isDark: boolean;
  onToggleTheme: () => void;
  onGatedAction: (destination: 'dashboard' | 'extension', preferredMode?: 'signin' | 'signup') => void;
  auth: ReturnType<typeof useAuth>;
  authModalOpen: boolean;
  authModalMode: AuthMode;
  noticeMessage: string | null;
  onOpenAuth: (mode: AuthMode, notice?: string) => void;
  onCloseAuth: () => void;
  onAuthSuccess: (user: AuthUser) => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({
  isDark,
  onToggleTheme,
  onGatedAction,
  auth,
  authModalOpen,
  authModalMode,
  noticeMessage,
  onOpenAuth,
  onCloseAuth,
  onAuthSuccess,
}) => {
  return (
    <div className="min-h-dvh overflow-x-clip bg-white dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex flex-col font-sans selection:bg-indigo-500 selection:text-white transition-colors duration-200">
      {/* Top Navbar */}
      <Navbar
        user={auth.user}
        isDark={isDark}
        onToggleTheme={onToggleTheme}
        onOpenAuth={(mode) => onOpenAuth(mode)}
        onSignOut={() => auth.signOut()}
        onGatedAction={onGatedAction}
      />

      {/* Main Landing Page Content */}
      <main className="flex-1">
        {/* 1. Hero Section (Calliom + Livo AI Fusion) */}
        <HeroSection
          onStartFree={() => onGatedAction('dashboard', 'signup')}
          onOpenDemo={() => {
            const demoEl = document.getElementById('live-demo');
            if (demoEl) {
              demoEl.scrollIntoView({ behavior: 'smooth' });
            }
          }}
          onDownloadExtension={() => onGatedAction('extension', 'signup')}
        />

        {/* 2. Platform Logos Ticker */}
        <LogosTicker />

        {/* 3. Three-Stage Meeting Value Tabs (Ai Notely Style) */}
        <FeatureTabsSection />

        {/* 4. Interactive Audio Waveform Demo (Calliom Style) */}
        <InteractiveAudioDemo />

        {/* 5. Career Scenarios & Use Cases (Livo AI Style) */}
        <UseCasesSection />

        {/* 6. Pricing Plans (Monthly / Yearly toggle with Top Choice) */}
        <PricingSection onSelectPlan={() => onGatedAction('dashboard', 'signup')} />

        {/* 7. Large Quote Testimonial Showcase */}
        <TestimonialSection />

        {/* 8. Frequently Asked Questions */}
        <FaqSection />
      </main>

      {/* Footer */}
      <Footer
        onOpenAuth={(mode) => onOpenAuth(mode)}
        onGatedAction={onGatedAction}
      />

      {/* Authentication Modal (Sign In / Sign Up / Forgot Password / Demo Profiles) */}
      <AuthModal
        isOpen={authModalOpen}
        initialMode={authModalMode}
        noticeMessage={noticeMessage}
        onClose={onCloseAuth}
        onSuccess={onAuthSuccess}
        auth={auth}
      />
    </div>
  );
};
