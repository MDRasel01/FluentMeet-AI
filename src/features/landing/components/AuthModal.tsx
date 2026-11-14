import React, { useState } from 'react';
import {
  X,
  Mail,
  Lock,
  User,
  Sparkles,
  ArrowRight,
  Eye,
  EyeOff,
  CheckCircle2,
  AlertCircle,
  Shield,
  Target,
  Zap
} from 'lucide-react';
import { AuthMode, AuthUser } from '../types';
import { DEMO_USERS } from '../useAuth';

interface AuthModalProps {
  isOpen: boolean;
  initialMode?: AuthMode;
  onClose: () => void;
  onSuccess: (user: AuthUser) => void;
  auth: ReturnType<typeof import('../useAuth').useAuth>;
}

export const AuthModal: React.FC<AuthModalProps> = ({
  isOpen,
  initialMode = 'signin',
  onClose,
  onSuccess,
  auth,
}) => {
  const [mode, setMode] = useState<AuthMode>(initialMode);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [goal, setGoal] = useState('Corporate Meetings & Discussion');
  const [showPassword, setShowPassword] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);
  const [forgotSubmitted, setForgotSubmitted] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);

    if (mode === 'forgot') {
      if (!email || !email.includes('@')) {
        setLocalError('Please enter a valid email address.');
        return;
      }
      setForgotSubmitted(true);
      return;
    }

    if (!email || !email.includes('@')) {
      setLocalError('Please enter a valid work or personal email.');
      return;
    }

    if (!password || password.length < 6) {
      setLocalError('Password must be at least 6 characters.');
      return;
    }

    try {
      if (mode === 'signin') {
        const user = await auth.signIn(email, password);
        onSuccess(user);
        onClose();
      } else {
        if (!name.trim()) {
          setLocalError('Please enter your full name.');
          return;
        }
        const user = await auth.signUp({ name, email, password, goal });
        onSuccess(user);
        onClose();
      }
    } catch (err: any) {
      setLocalError(err?.message || 'Authentication failed. Please try again.');
    }
  };

  const handleQuickDemo = (personaKey: 'priya' | 'alex' | 'marcus') => {
    const user = auth.quickFillDemo(personaKey);
    onSuccess(user);
    onClose();
  };

  const goals = [
    { id: 'Corporate Meetings & Discussion', label: '💼 Corporate Meetings', desc: 'Speak confidently in cross-border syncs' },
    { id: 'Job Interview Preparation', label: '🎯 Job Interviews', desc: 'Crack FAANG / global tech interviews' },
    { id: 'IELTS Speaking 7.5+', label: '🎓 IELTS / CEFR Prep', desc: 'Boost vocabulary & fluent pronunciation' },
    { id: 'Executive Leadership & Pitches', label: '🚀 Executive Pitches', desc: 'High-impact persuasion & client calls' },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 overflow-y-auto">
      {/* Blurred Backdrop */}
      <div
        className="fixed inset-0 bg-slate-900/60 backdrop-blur-md transition-opacity animate-in fade-in duration-200"
        onClick={onClose}
      />

      {/* Modal Card */}
      <div className="relative w-full max-w-md bg-white dark:bg-slate-900 rounded-3xl shadow-2xl border border-slate-200/80 dark:border-slate-800 p-6 md:p-8 z-10 my-8 transition-all animate-in zoom-in-95 duration-200">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-full text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          aria-label="Close"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Brand Header */}
        <div className="text-center space-y-1.5 mb-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 dark:bg-indigo-950/60 border border-indigo-200 dark:border-indigo-800 text-indigo-700 dark:text-indigo-300 text-xs font-semibold mb-1">
            <Sparkles className="w-3.5 h-3.5 text-indigo-500" />
            <span>FluentMeet AI Platform</span>
          </div>
          <h3 className="text-2xl font-black text-slate-900 dark:text-white tracking-tight">
            {mode === 'signin' && 'Welcome Back'}
            {mode === 'signup' && 'Create Your Account'}
            {mode === 'forgot' && 'Reset Password'}
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 max-w-xs mx-auto">
            {mode === 'signin' && 'Sign in to access your meeting transcripts, CEFR scores, and speech coaching analytics.'}
            {mode === 'signup' && 'Join 50,000+ professionals speaking confident, fluent English in daily meetings.'}
            {mode === 'forgot' && 'Enter your email and we will send you a secure password reset link.'}
          </p>
        </div>

        {/* Mode Switcher Tabs */}
        {mode !== 'forgot' && (
          <div className="grid grid-cols-2 gap-1 p-1 bg-slate-100 dark:bg-slate-800/80 rounded-2xl mb-5 text-xs font-semibold">
            <button
              type="button"
              onClick={() => {
                setMode('signin');
                setLocalError(null);
              }}
              className={`py-2 rounded-xl transition-all ${
                mode === 'signin'
                  ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm'
                  : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              Sign In
            </button>
            <button
              type="button"
              onClick={() => {
                setMode('signup');
                setLocalError(null);
              }}
              className={`py-2 rounded-xl transition-all ${
                mode === 'signup'
                  ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm'
                  : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              Create Account
            </button>
          </div>
        )}

        {/* Form Error Banner */}
        {(localError || auth.error) && (
          <div className="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/50 border border-rose-200 dark:border-rose-900 text-rose-600 dark:text-rose-300 text-xs flex items-center gap-2 mb-4">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span className="leading-tight">{localError || auth.error}</span>
          </div>
        )}

        {/* Forgot Password Success Notice */}
        {forgotSubmitted ? (
          <div className="text-center py-6 space-y-3">
            <div className="w-12 h-12 rounded-full bg-emerald-100 dark:bg-emerald-950/60 text-emerald-600 mx-auto flex items-center justify-center">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <h4 className="text-base font-bold text-slate-900 dark:text-white">Check Your Inbox</h4>
            <p className="text-xs text-slate-500 max-w-xs mx-auto">
              We sent a secure password reset link to <span className="font-semibold text-slate-700 dark:text-slate-300">{email}</span>.
            </p>
            <button
              type="button"
              onClick={() => {
                setForgotSubmitted(false);
                setMode('signin');
              }}
              className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:underline pt-2 block mx-auto"
            >
              Back to Sign In
            </button>
          </div>
        ) : (
          /* Main Form */
          <form onSubmit={handleSubmit} className="space-y-3.5">
            {mode === 'signup' && (
              <div>
                <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                  Full Name
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-3 w-4 h-4 text-slate-400" />
                  <input
                    type="text"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. Priya Sharma"
                    className="w-full pl-9 pr-3 py-2.5 text-xs rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-3 w-4 h-4 text-slate-400" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@company.com"
                  className="w-full pl-9 pr-3 py-2.5 text-xs rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>

            {mode !== 'forgot' && (
              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="text-xs font-medium text-slate-700 dark:text-slate-300">
                    Password
                  </label>
                  {mode === 'signin' && (
                    <button
                      type="button"
                      onClick={() => setMode('forgot')}
                      className="text-[11px] text-indigo-600 dark:text-indigo-400 hover:underline font-medium"
                    >
                      Forgot password?
                    </button>
                  )}
                </div>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 w-4 h-4 text-slate-400" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-9 pr-10 py-2.5 text-xs rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-3 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
            )}

            {/* Target Goal selection on Sign Up */}
            {mode === 'signup' && (
              <div className="pt-1">
                <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                  Primary English Goal
                </label>
                <div className="grid grid-cols-2 gap-1.5">
                  {goals.map((g) => (
                    <button
                      key={g.id}
                      type="button"
                      onClick={() => setGoal(g.id)}
                      className={`p-2 text-left rounded-xl border text-[11px] transition-all ${
                        goal === g.id
                          ? 'border-indigo-600 bg-indigo-50/70 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 font-semibold'
                          : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600 text-slate-700 dark:text-slate-300'
                      }`}
                    >
                      <div className="truncate">{g.label}</div>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Submit CTA */}
            <button
              type="submit"
              disabled={auth.isLoading}
              className="w-full mt-2 py-3 px-4 rounded-xl bg-gradient-to-r from-indigo-600 via-indigo-700 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold text-xs shadow-lg shadow-indigo-500/25 flex items-center justify-center gap-2 transition-all hover:scale-[1.01] active:scale-[0.99]"
            >
              {auth.isLoading ? (
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  <span>
                    {mode === 'signin' && 'Sign In to Dashboard'}
                    {mode === 'signup' && 'Create Free Account'}
                    {mode === 'forgot' && 'Send Reset Link'}
                  </span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          </form>
        )}

        {/* Demo Fast Login Personas */}
        <div className="mt-6 pt-5 border-t border-slate-100 dark:border-slate-800 space-y-2.5">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
              <Zap className="w-3.5 h-3.5 text-amber-500" />
              1-Click Demo Profiles (Instant Login)
            </span>
            <span className="text-[10px] text-slate-400">Preloaded data</span>
          </div>
          <div className="grid grid-cols-3 gap-2">
            <button
              type="button"
              onClick={() => handleQuickDemo('priya')}
              className="p-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700 hover:border-indigo-500 text-left transition-all group"
            >
              <div className="text-[11px] font-bold text-slate-800 dark:text-slate-200 group-hover:text-indigo-600 truncate">
                Priya S.
              </div>
              <div className="text-[9px] text-slate-400 truncate">Product Mgr</div>
            </button>

            <button
              type="button"
              onClick={() => handleQuickDemo('alex')}
              className="p-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700 hover:border-indigo-500 text-left transition-all group"
            >
              <div className="text-[11px] font-bold text-slate-800 dark:text-slate-200 group-hover:text-indigo-600 truncate">
                Alex Chen
              </div>
              <div className="text-[9px] text-slate-400 truncate">Tech Architect</div>
            </button>

            <button
              type="button"
              onClick={() => handleQuickDemo('marcus')}
              className="p-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700 hover:border-indigo-500 text-left transition-all group"
            >
              <div className="text-[11px] font-bold text-slate-800 dark:text-slate-200 group-hover:text-indigo-600 truncate">
                Marcus V.
              </div>
              <div className="text-[9px] text-slate-400 truncate">VP Global</div>
            </button>
          </div>
        </div>

        {/* Security / Privacy Assurance */}
        <div className="mt-4 flex items-center justify-center gap-2 text-[10px] text-slate-400 text-center">
          <Shield className="w-3 h-3 text-emerald-500 shrink-0" />
          <span>SOC2 Type II & GDPR Compliant • Audio processed with strict consent</span>
        </div>
      </div>
    </div>
  );
};
