import React, { useState } from 'react';
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
  onNavigateApp: (app: 'dashboard' | 'extension') => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({
  isDark,
  onToggleTheme,
  onNavigateApp,
}) => {
  const auth = useAuth();
  const [authModalOpen, setAuthModalOpen] = useState<boolean>(false);
  const [authModalMode, setAuthModalMode] = useState<AuthMode>('signin');

  const handleOpenAuth = (mode: AuthMode = 'signin') => {
    setAuthModalMode(mode);
    setAuthModalOpen(true);
  };

  const handleAuthSuccess = (user: AuthUser) => {
    // Optionally navigate straight to dashboard or keep user on landing page with logged-in status
    console.log('[FluentMeet Landing] User authenticated successfully:', user.name);
  };

  const handleSelectPlan = (planId: string) => {
    if (auth.user) {
      onNavigateApp('dashboard');
    } else {
      handleOpenAuth('signup');
    }
  };

  return (
    <div className="min-h-screen bg-white dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex flex-col font-sans selection:bg-indigo-500 selection:text-white transition-colors duration-200">
      {/* Top Navbar */}
      <Navbar
        user={auth.user}
        isDark={isDark}
        onToggleTheme={onToggleTheme}
        onOpenAuth={(mode) => handleOpenAuth(mode)}
        onSignOut={() => auth.signOut()}
        onNavigateApp={onNavigateApp}
      />

      {/* Main Landing Page Content */}
      <main className="flex-1">
        {/* 1. Hero Section (Calliom + Livo AI Fusion) */}
        <HeroSection
          onStartFree={() => handleOpenAuth('signup')}
          onOpenDemo={() => {
            const demoEl = document.getElementById('live-demo');
            if (demoEl) {
              demoEl.scrollIntoView({ behavior: 'smooth' });
            }
          }}
          onDownloadExtension={() => onNavigateApp('extension')}
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
        <PricingSection onSelectPlan={handleSelectPlan} />

        {/* 7. Large Quote Testimonial Showcase */}
        <TestimonialSection />

        {/* 8. Frequently Asked Questions */}
        <FaqSection />
      </main>

      {/* Footer */}
      <Footer
        onOpenAuth={(mode) => handleOpenAuth(mode)}
        onNavigateApp={onNavigateApp}
      />

      {/* Authentication Modal (Sign In / Sign Up / Forgot Password / Demo Profiles) */}
      <AuthModal
        isOpen={authModalOpen}
        initialMode={authModalMode}
        onClose={() => setAuthModalOpen(false)}
        onSuccess={handleAuthSuccess}
        auth={auth}
      />
    </div>
  );
};
