import React, { useState, useEffect, useRef, type TouchEvent } from 'react';
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
  Zap,
  Crown
} from 'lucide-react';
import { AuthMode, AuthUser } from '../types';
import { useLockBodyScroll } from '../../../hooks/useLockBodyScroll';

interface AuthModalProps {
  isOpen: boolean;
  initialMode?: AuthMode;
  noticeMessage?: string | null;
  onClose: () => void;
  onSuccess: (user: AuthUser) => void;
  auth: ReturnType<typeof import('../useAuth').useAuth>;
}

export const AuthModal: React.FC<AuthModalProps> = ({
  isOpen,
  initialMode = 'signin',
  noticeMessage = null,
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
  const [dragY, setDragY] = useState(0);
  const startY = useRef<number | null>(null);

  useLockBodyScroll(isOpen);

  useEffect(() => {
    if (isOpen) {
      setMode(initialMode);
      setDragY(0);
      setLocalError(null);
    }
  }, [isOpen, initialMode]);

  useEffect(() => {
    if (!isOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [isOpen, onClose]);

  // Mobile swipe down to close
  const onTouchStart = (e: TouchEvent) => {
    startY.current = e.touches[0].clientY;
  };
  const onTouchMove = (e: TouchEvent) => {
    if (startY.current === null) return;
    const delta = e.touches[0].clientY - startY.current;
    if (delta > 0) setDragY(delta);
  };
  const onTouchEnd = () => {
    if (dragY > 100) onClose();
    setDragY(0);
    startY.current = null;
  };

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
      setLocalError('Password must be at least 6 characters long.');
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
      setLocalError(err?.message || 'Authentication failed. Please verify your credentials.');
    }
  };

  const handleQuickDemo = (personaKey: 'founder' | 'priya' | 'alex' | 'marcus') => {
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
    <div className="fixed inset-0 z-50 flex items-end justify-center sm:items-center sm:p-4">
      {/* Blurred Backdrop */}
      <div
        className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      {/* Sheet Dialog Container */}
      <div
        className="relative w-full sm:max-w-md bg-white dark:bg-slate-900 rounded-t-3xl sm:rounded-3xl shadow-2xl border border-slate-200 dark:border-slate-800 z-10 max-h-[92dvh] sm:max-h-[88dvh] overflow-y-auto overscroll-contain transition-transform"
        style={{ transform: dragY > 0 ? `translateY(${dragY}px)` : undefined }}
      >
        {/* Mobile drag handle */}
        <div
          className="sm:hidden w-full pt-3 pb-1 flex justify-center cursor-grab active:cursor-grabbing touch-none"
          onTouchStart={onTouchStart}
          onTouchMove={onTouchMove}
          onTouchEnd={onTouchEnd}
        >
          <div className="w-12 h-1.5 rounded-full bg-slate-300 dark:bg-slate-700" />
        </div>

        <div className="p-6 sm:p-7">
          {/* Header */}
          <div className="flex items-center justify-between pb-4 border-b border-slate-100 dark:border-slate-800">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-2xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-500 flex items-center justify-center text-white font-black text-lg shadow-md shadow-indigo-500/20">
                F
              </div>
              <div>
                <h3 className="text-base font-black text-slate-900 dark:text-white leading-tight">
                  {mode === 'signin' && 'Sign in to FluentMeet'}
                  {mode === 'signup' && 'Create Your Account'}
                  {mode === 'forgot' && 'Reset Your Password'}
                </h3>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">
                  {mode === 'signin' && 'Access real-time coaching & speech feedback'}
                  {mode === 'signup' && 'Get 14-day free access • No credit card required'}
                  {mode === 'forgot' && "We'll send password recovery instructions"}
                </p>
              </div>
            </div>

            <button
              onClick={onClose}
              className="p-1.5 rounded-xl text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              aria-label="Close modal"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Notice message if user was redirected from a gated feature */}
          {noticeMessage && (
            <div className="mt-3 p-3 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 border border-indigo-200 dark:border-indigo-800 text-indigo-800 dark:text-indigo-300 text-xs flex items-center gap-2">
              <Zap className="w-4 h-4 text-indigo-600 shrink-0" />
              <span>{noticeMessage}</span>
            </div>
          )}

          {/* Mode Switcher Tabs */}
          {mode !== 'forgot' && (
            <div className="grid grid-cols-2 gap-1 p-1 bg-slate-100 dark:bg-slate-800/80 rounded-xl my-4 text-xs font-bold">
              <button
                type="button"
                onClick={() => {
                  setMode('signin');
                  setLocalError(null);
                }}
                className={`py-2 rounded-lg transition-all ${
                  mode === 'signin'
                    ? 'bg-white dark:bg-slate-700 text-indigo-600 dark:text-white shadow-sm'
                    : 'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
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
                className={`py-2 rounded-lg transition-all ${
                  mode === 'signup'
                    ? 'bg-white dark:bg-slate-700 text-indigo-600 dark:text-white shadow-sm'
                    : 'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                Create Account
              </button>
            </div>
          )}

          {/* Error Message Banner */}
          {(localError || auth.error) && (
            <div className="mb-4 p-3 rounded-xl bg-rose-50 dark:bg-rose-950/50 border border-rose-200 dark:border-rose-900 text-rose-700 dark:text-rose-300 text-xs flex items-start gap-2 animate-in fade-in">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-500" />
              <div className="leading-relaxed">{localError || auth.error}</div>
            </div>
          )}

          {/* Form */}
          {forgotSubmitted ? (
            <div className="py-6 text-center space-y-3">
              <div className="w-12 h-12 rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-600 flex items-center justify-center mx-auto">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <h4 className="text-sm font-bold text-slate-900 dark:text-white">Check your email</h4>
              <p className="text-xs text-slate-500 dark:text-slate-400 max-w-xs mx-auto">
                We sent password reset instructions to <span className="font-semibold text-slate-700 dark:text-slate-300">{email}</span>.
              </p>
              <button
                onClick={() => {
                  setForgotSubmitted(false);
                  setMode('signin');
                }}
                className="mt-3 px-4 py-2 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs font-bold rounded-xl hover:bg-slate-200"
              >
                Back to Sign In
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-3.5">
              {/* Name field on Sign Up */}
              {mode === 'signup' && (
                <div>
                  <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                    Full Name
                  </label>
                  <div className="relative">
                    <User className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                    <input
                      type="text"
                      required
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      placeholder="e.g. Priya Sharma"
                      className="w-full pl-9 pr-3 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white text-xs placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                </div>
              )}

              {/* Email */}
              <div>
                <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                  Work or Personal Email
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@company.com"
                    className="w-full pl-9 pr-3 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white text-xs placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              </div>

              {/* Password */}
              {mode !== 'forgot' && (
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <label className="block text-xs font-medium text-slate-700 dark:text-slate-300">
                      Password
                    </label>
                    {mode === 'signin' && (
                      <button
                        type="button"
                        onClick={() => {
                          setMode('forgot');
                          setLocalError(null);
                        }}
                        className="text-[11px] text-indigo-600 dark:text-indigo-400 hover:underline"
                      >
                        Forgot?
                      </button>
                    )}
                  </div>
                  <div className="relative">
                    <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      required
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder={mode === 'signup' ? 'Min 6 characters' : 'Enter your password'}
                      className="w-full pl-9 pr-10 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white text-xs placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
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
          <div className="mt-5 pt-4 border-t border-slate-100 dark:border-slate-800 space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
                <Zap className="w-3.5 h-3.5 text-amber-500" />
                1-Click Fast Login Test Roles
              </span>
              <span className="text-[10px] text-slate-400">Owner vs Member</span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              <button
                type="button"
                onClick={() => handleQuickDemo('founder')}
                className="p-2 rounded-xl bg-amber-50/80 dark:bg-amber-950/40 border border-amber-300/80 dark:border-amber-700 hover:border-amber-500 text-left transition-all group shadow-sm"
                title="Sign in as Founder / Owner (Enables Step 02 Workbench)"
              >
                <div className="flex items-center gap-1 text-[11px] font-bold text-amber-900 dark:text-amber-200 group-hover:text-amber-600 truncate">
                  <Crown className="w-3 h-3 text-amber-500 shrink-0" />
                  <span>Founder</span>
                </div>
                <div className="text-[9px] text-amber-700 dark:text-amber-400 font-semibold truncate">Role: Owner</div>
              </button>

              <button
                type="button"
                onClick={() => handleQuickDemo('priya')}
                className="p-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700 hover:border-indigo-500 text-left transition-all group"
                title="Sign in as Priya (Regular Member - No Workbench in DOM)"
              >
                <div className="text-[11px] font-bold text-slate-800 dark:text-slate-200 group-hover:text-indigo-600 truncate">
                  Priya S.
                </div>
                <div className="text-[9px] text-slate-400 truncate">Role: Member</div>
              </button>

              <button
                type="button"
                onClick={() => handleQuickDemo('alex')}
                className="p-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700 hover:border-indigo-500 text-left transition-all group"
                title="Sign in as Alex (Regular Member - No Workbench in DOM)"
              >
                <div className="text-[11px] font-bold text-slate-800 dark:text-slate-200 group-hover:text-indigo-600 truncate">
                  Alex Chen
                </div>
                <div className="text-[9px] text-slate-400 truncate">Role: Member</div>
              </button>

              <button
                type="button"
                onClick={() => handleQuickDemo('marcus')}
                className="p-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700 hover:border-indigo-500 text-left transition-all group"
                title="Sign in as Marcus (Team Admin - No Workbench in DOM)"
              >
                <div className="text-[11px] font-bold text-slate-800 dark:text-slate-200 group-hover:text-indigo-600 truncate">
                  Marcus V.
                </div>
                <div className="text-[9px] text-slate-400 truncate">Role: Admin</div>
              </button>
            </div>
          </div>

          {/* Security / Privacy Assurance */}
          <div className="mt-4 flex items-center justify-center gap-2 text-[10px] text-slate-400 text-center pb-2">
            <Shield className="w-3 h-3 text-emerald-500 shrink-0" />
            <span>SOC2 Type II & GDPR Compliant • Audio processed with strict consent</span>
          </div>
        </div>
      </div>
    </div>
  );
};
