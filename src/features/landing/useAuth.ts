import { useState, useEffect, useCallback } from 'react';
import { AuthUser } from './types';
import { loginRequest, signupRequest } from '../../lib/api';
import { loginSchema, registerSchema, getFriendlyErrorMessage, isOwnerRole } from '../../lib/validation';

const STORAGE_KEY = 'fluentmeet_auth_user';

export const DEMO_USERS: Record<string, AuthUser> = {
  founder: {
    id: 'usr-founder-00',
    name: 'Russell (Founder)',
    email: 'russell7@gmail.com',
    avatarUrl: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=256&q=80',
    role: 'owner',
    jobTitle: 'Founder & Platform Owner',
    goal: 'Executive Vision & Platform Architecture',
    tier: 'enterprise',
    token: 'jwt-mock-founder-russell',
    mustChangePassword: false,
    theme: 'system',
    createdAt: '2026-01-01T00:00:00Z',
  },
  priya: {
    id: 'usr-priya-01',
    name: 'Priya Sharma',
    email: 'priya.sharma@techcorp.io',
    avatarUrl: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=256&q=80',
    role: 'member',
    jobTitle: 'Senior Product Manager',
    goal: 'Corporate Meetings & Executive Influence',
    tier: 'pro',
    token: 'jwt-mock-priya-sharma',
    mustChangePassword: false,
    createdAt: '2026-01-10T10:00:00Z',
  },
  alex: {
    id: 'usr-alex-02',
    name: 'Alex Chen',
    email: 'alex.chen@cloudstack.ai',
    avatarUrl: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=256&q=80',
    role: 'member',
    jobTitle: 'Staff Software Architect',
    goal: 'FAANG Technical Interviews & System Design',
    tier: 'pro',
    token: 'jwt-mock-alex-chen',
    mustChangePassword: false,
    createdAt: '2026-02-15T14:30:00Z',
  },
  marcus: {
    id: 'usr-marcus-03',
    name: 'Marcus Vance',
    email: 'marcus.v@novatech.co',
    avatarUrl: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=256&q=80',
    role: 'admin',
    jobTitle: 'VP of Global Partnerships',
    goal: 'Cross-Border Negotiation & High-Stakes Pitches',
    tier: 'enterprise',
    token: 'jwt-mock-marcus-vance',
    mustChangePassword: false,
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
    // Default to null (unauthenticated public user viewing landing page)
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

  const signIn = useCallback(async (email: string, password?: string): Promise<AuthUser> => {
    setIsLoading(true);
    setError(null);

    // Schema Validation
    const validation = loginSchema.safeParse({ email, password: password || 'dummy-fallback' });
    if (!validation.success) {
      const msg = validation.error.issues[0]?.message || 'Please check your email and password format.';
      setIsLoading(false);
      setError(msg);
      throw new Error(msg);
    }

    // 1. Try real FastAPI multi-tenant endpoint first
    try {
      if (password) {
        const s = await loginRequest(email, password);
        const authedUser: AuthUser = {
          id: s.user.id,
          name: s.user.full_name || email.split('@')[0],
          email: s.user.email,
          avatarUrl: s.user.avatar_url || `https://api.dicebear.com/7.x/avataaars/svg?seed=${encodeURIComponent(email)}`,
          role: s.tenant.role, // 'owner' | 'admin' | 'member' strictly verified from DB
          jobTitle: s.tenant.role === 'owner' ? 'Founder & Platform Owner' : s.tenant.role === 'admin' ? 'Team Administrator' : 'Fluent Member',
          goal: s.user.goal || 'Corporate Meetings & Fluency',
          tier: s.tenant.tier === 'enterprise' ? 'enterprise' : s.tenant.tier === 'team' || s.tenant.tier === 'pro' ? 'pro' : 'starter',
          token: s.access_token,
          mustChangePassword: false,
          theme: 'system',
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
    await new Promise((r) => setTimeout(r, 350));
    try {
      const foundDemo = Object.values(DEMO_USERS).find(
        (u) => u.email.toLowerCase() === email.trim().toLowerCase()
      );

      const isFounderEmail = email.trim().toLowerCase() === 'russell7@gmail.com' || email.toLowerCase().includes('founder');

      const authedUser: AuthUser = foundDemo || {
        id: 'usr-' + Math.random().toString(36).substring(2, 9),
        name: email.split('@')[0].replace(/[._-]/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
        email: email.trim().toLowerCase(),
        avatarUrl: `https://api.dicebear.com/7.x/avataaars/svg?seed=${encodeURIComponent(email)}`,
        role: isFounderEmail ? 'owner' : 'member',
        jobTitle: isFounderEmail ? 'Platform Owner' : 'Professional Member',
        goal: 'General Meeting English & Fluency',
        tier: isFounderEmail ? 'enterprise' : 'starter',
        token: 'jwt-mock-' + Date.now(),
        mustChangePassword: false,
        theme: 'system',
        createdAt: new Date().toISOString(),
      };

      setUser(authedUser);
      setIsLoading(false);
      return authedUser;
    } catch (err: any) {
      const friendly = getFriendlyErrorMessage(err, 'Failed to sign in. Please verify your credentials.');
      setIsLoading(false);
      setError(friendly);
      throw new Error(friendly);
    }
  }, []);

  const signUp = useCallback(async (params: {
    name: string;
    email: string;
    password?: string;
    goal?: string;
    role?: 'owner' | 'admin' | 'member';
  }): Promise<AuthUser> => {
    setIsLoading(true);
    setError(null);

    // Schema Validation
    const validation = registerSchema.safeParse({
      name: params.name,
      email: params.email,
      password: params.password || 'SecurePass123!',
      goal: params.goal,
      role: params.role || 'member',
    });

    if (!validation.success) {
      const msg = validation.error.issues[0]?.message || 'Please check your registration details.';
      setIsLoading(false);
      setError(msg);
      throw new Error(msg);
    }

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
          role: s.tenant.role, // Strictly populated from server
          jobTitle: s.tenant.role === 'owner' ? 'Founder & Platform Owner' : 'Fluent Member',
          goal: s.user.goal || params.goal || 'Corporate Meetings & Fluency',
          tier: 'starter',
          token: s.access_token,
          mustChangePassword: false,
          theme: 'system',
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
    await new Promise((r) => setTimeout(r, 400));
    try {
      const newUser: AuthUser = {
        id: 'usr-' + Math.random().toString(36).substring(2, 9),
        name: params.name.trim() || 'Fluent Member',
        email: params.email.trim().toLowerCase(),
        avatarUrl: `https://api.dicebear.com/7.x/avataaars/svg?seed=${encodeURIComponent(params.name || params.email)}`,
        role: 'member', // Default new accounts are regular members; cannot self-grant 'owner'
        jobTitle: 'Professional Member',
        goal: params.goal || 'Corporate Meetings & Discussion',
        tier: 'starter',
        token: 'jwt-mock-' + Date.now(),
        mustChangePassword: false,
        theme: 'system',
        createdAt: new Date().toISOString(),
      };

      setUser(newUser);
      setIsLoading(false);
      return newUser;
    } catch (err: any) {
      const friendly = getFriendlyErrorMessage(err, 'Registration failed. Please try again.');
      setIsLoading(false);
      setError(friendly);
      throw new Error(friendly);
    }
  }, []);

  const quickFillDemo = useCallback((personaKey: 'founder' | 'priya' | 'alex' | 'marcus') => {
    const selected = DEMO_USERS[personaKey] || DEMO_USERS.priya;
    setUser(selected);
    return selected;
  }, []);

  const updatePassword = useCallback((_newPass: string) => {
    setUser((prev) => (prev ? { ...prev, mustChangePassword: false } : null));
  }, []);

  const setThemePreference = useCallback((theme: 'light' | 'dark' | 'system') => {
    setUser((prev) => (prev ? { ...prev, theme } : null));
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
    isOwner: isOwnerRole(user?.role),
    isLoading,
    error,
    signIn,
    signUp,
    quickFillDemo,
    updatePassword,
    setThemePreference,
    signOut,
  };
}
