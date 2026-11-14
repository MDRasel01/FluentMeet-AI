import { useState, useEffect, useCallback } from 'react';
import { AuthUser } from './types';
import { loginRequest, signupRequest } from '../../lib/api';

const STORAGE_KEY = 'fluentmeet_auth_user';

export const DEMO_USERS: Record<string, AuthUser> = {
  priya: {
    id: 'usr-priya-01',
    name: 'Priya Sharma',
    email: 'priya.sharma@techcorp.io',
    avatarUrl: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=256&q=80',
    role: 'Senior Product Manager',
    goal: 'Corporate Meetings & Executive Influence',
    tier: 'pro',
    token: 'jwt-mock-priya-sharma',
    createdAt: '2026-01-10T10:00:00Z',
  },
  alex: {
    id: 'usr-alex-02',
    name: 'Alex Chen',
    email: 'alex.chen@cloudstack.ai',
    avatarUrl: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=256&q=80',
    role: 'Staff Software Architect',
    goal: 'FAANG Technical Interviews & System Design',
    tier: 'pro',
    token: 'jwt-mock-alex-chen',
    createdAt: '2026-02-15T14:30:00Z',
  },
  marcus: {
    id: 'usr-marcus-03',
    name: 'Marcus Vance',
    email: 'marcus.v@novatech.co',
    avatarUrl: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=256&q=80',
    role: 'VP of Global Partnerships',
    goal: 'Cross-Border Negotiation & High-Stakes Pitches',
    tier: 'enterprise',
    token: 'jwt-mock-marcus-vance',
    createdAt: '2026-03-01T08:15:00Z',
  },
};

export function useAuth() {
  const [user, setUser] = useState<AuthUser | null>(() => {
    try {
      if (typeof window !== 'undefined') {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
          return JSON.parse(stored);
        }
      }
    } catch (e) {
      console.warn('Failed to parse auth user from localStorage:', e);
    }
    // Default to null (unauthenticated user viewing landing page)
    return null;
  });

  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Sync state to localStorage
  useEffect(() => {
    try {
      if (typeof window !== 'undefined') {
        if (user) {
          localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
        } else {
          localStorage.removeItem(STORAGE_KEY);
        }
      }
    } catch (e) {
      console.warn('Failed to save auth user to localStorage:', e);
    }
  }, [user]);

  const signIn = useCallback(async (email: string, _password?: string): Promise<AuthUser> => {
    setIsLoading(true);
    setError(null);

    // 1. Try real FastAPI multi-tenant endpoint first
    try {
      if (_password) {
        const s = await loginRequest(email, _password);
        const authedUser: AuthUser = {
          id: s.user.id,
          name: s.user.full_name || email.split('@')[0],
          email: s.user.email,
          avatarUrl: s.user.avatar_url || `https://api.dicebear.com/7.x/avataaars/svg?seed=${encodeURIComponent(email)}`,
          role: s.tenant.role,
          goal: s.user.goal || 'Corporate Meetings & Fluency',
          tier: s.tenant.tier === 'enterprise' ? 'enterprise' : s.tenant.tier === 'team' || s.tenant.tier === 'pro' ? 'pro' : 'starter',
          token: s.access_token,
          createdAt: new Date().toISOString(),
        };
        setUser(authedUser);
        setIsLoading(false);
        return authedUser;
      }
    } catch (apiErr) {
      console.warn('[FluentMeet Auth] Live backend login skipped or offline, falling back to local session:', apiErr);
    }

    // 2. Demo fallback
    await new Promise((r) => setTimeout(r, 400));
    try {
      const foundDemo = Object.values(DEMO_USERS).find(
        (u) => u.email.toLowerCase() === email.trim().toLowerCase()
      );

      const authedUser: AuthUser = foundDemo || {
        id: 'usr-' + Math.random().toString(36).substring(2, 9),
        name: email.split('@')[0].replace(/[._-]/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
        email: email.trim(),
        avatarUrl: `https://api.dicebear.com/7.x/avataaars/svg?seed=${encodeURIComponent(email)}`,
        role: 'Professional Speaker',
        goal: 'General Meeting English & Fluency',
        tier: 'pro',
        token: 'jwt-mock-' + Date.now(),
        createdAt: new Date().toISOString(),
      };

      setUser(authedUser);
      setIsLoading(false);
      return authedUser;
    } catch (err: any) {
      setIsLoading(false);
      setError(err?.message || 'Failed to sign in. Please verify your credentials.');
      throw err;
    }
  }, []);

  const signUp = useCallback(async (params: {
    name: string;
    email: string;
    password?: string;
    goal?: string;
    role?: string;
  }): Promise<AuthUser> => {
    setIsLoading(true);
    setError(null);

    // 1. Try real FastAPI multi-tenant endpoint first
    try {
      if (params.password) {
        const s = await signupRequest({
          email: params.email,
          password: params.password,
          full_name: params.name,
          goal: params.goal,
        });
        const authedUser: AuthUser = {
          id: s.user.id,
          name: s.user.full_name || params.name,
          email: s.user.email,
          avatarUrl: s.user.avatar_url || `https://api.dicebear.com/7.x/avataaars/svg?seed=${encodeURIComponent(params.name || params.email)}`,
          role: s.tenant.role,
          goal: s.user.goal || params.goal || 'Corporate Meetings & Fluency',
          tier: 'starter',
          token: s.access_token,
          createdAt: new Date().toISOString(),
        };
        setUser(authedUser);
        setIsLoading(false);
        return authedUser;
      }
    } catch (apiErr) {
      console.warn('[FluentMeet Auth] Live backend signup skipped or offline, falling back to local session:', apiErr);
    }

    // 2. Demo fallback
    await new Promise((r) => setTimeout(r, 450));
    try {
      const newUser: AuthUser = {
        id: 'usr-' + Math.random().toString(36).substring(2, 9),
        name: params.name.trim() || 'Fluent Member',
        email: params.email.trim(),
        avatarUrl: `https://api.dicebear.com/7.x/avataaars/svg?seed=${encodeURIComponent(params.name || params.email)}`,
        role: params.role || 'Professional Speaker',
        goal: params.goal || 'Corporate Meetings & Discussion',
        tier: 'starter',
        token: 'jwt-mock-' + Date.now(),
        createdAt: new Date().toISOString(),
      };

      setUser(newUser);
      setIsLoading(false);
      return newUser;
    } catch (err: any) {
      setIsLoading(false);
      setError(err?.message || 'Registration failed.');
      throw err;
    }
  }, []);

  const quickFillDemo = useCallback((personaKey: 'priya' | 'alex' | 'marcus') => {
    const selected = DEMO_USERS[personaKey] || DEMO_USERS.priya;
    setUser(selected);
    return selected;
  }, []);

  const signOut = useCallback(() => {
    setUser(null);
    setError(null);
    if (typeof window !== 'undefined') {
      localStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  return {
    user,
    isAuthenticated: Boolean(user),
    isLoading,
    error,
    signIn,
    signUp,
    quickFillDemo,
    signOut,
  };
}
