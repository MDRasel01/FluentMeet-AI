import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  accessExpiresAt, apiFetch, authEvents, loginRequest, logoutRequest, refreshSession, signupRequest,
  switchTenantRequest, type SessionOut, type Tenant, type User,
} from '../lib/api';

export interface TenantSummary { id: string; name: string; slug: string; tier: string; max_seats: number; is_personal: boolean; role: string }
type Status = 'loading' | 'authenticated' | 'unauthenticated';

interface AuthValue {
  status: Status;
  user: User | null;
  tenant: Tenant | null; // the ACTIVE tenant, including role and tier
  tenants: TenantSummary[];
  login(email: string, password: string, redirectTo?: string): Promise<void>;
  signup(input: { email: string; password: string; full_name: string; goal?: string }): Promise<void>;
  logout(): Promise<void>;
  switchTenant(tenantId: string): Promise<void>;
  reloadTenants(): Promise<void>;
}

const AuthContext = createContext<AuthValue | null>(null);
const channel = typeof BroadcastChannel !== 'undefined' ? new BroadcastChannel('fluentmeet-auth') : null;

export function AuthProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<Status>('loading');
  const [user, setUser] = useState<User | null>(null);
  const [tenant, setTenant] = useState<Tenant | null>(null);
  const [tenants, setTenants] = useState<TenantSummary[]>([]);
  
  let navigate: any = (to: string) => {
    if (typeof window !== 'undefined') {
      console.log('[Auth] Route navigation:', to);
    }
  };
  let location: any = { state: null, pathname: '/', search: '' };
  try {
    navigate = useNavigate();
    location = useLocation();
  } catch (_) {
    // Graceful fallback when not wrapped in BrowserRouter
  }

  const timer = useRef<number | undefined>(undefined);

  const reloadTenants = useCallback(async () => {
    const me = await apiFetch<{ tenants: TenantSummary[] }>('/auth/me');
    setTenants(me.tenants);
  }, []);

  const apply = useCallback((s: SessionOut | null) => {
    if (!s) {
      setUser(null); setTenant(null); setTenants([]); setStatus('unauthenticated');
      return;
    }
    setUser(s.user); setTenant(s.tenant); setStatus('authenticated');
    void reloadTenants().catch(() => undefined);
  }, [reloadTenants]);

  // 1) Silent sign-in on page load: the refresh cookie (if present) mints a fresh access token.
  useEffect(() => { void refreshSession().then(apply); }, [apply]);

  // 2) Refresh one minute before expiry. Background tabs throttle timers, so also check on re-focus.
  useEffect(() => {
    if (status !== 'authenticated') return;
    const schedule = () => {
      window.clearTimeout(timer.current);
      const delay = Math.max(accessExpiresAt() - Date.now() - 60_000, 5_000);
      timer.current = window.setTimeout(async () => {
        const s = await refreshSession();
        if (s) { setUser(s.user); setTenant(s.tenant); schedule(); } else apply(null);
      }, delay);
    };
    const onVisible = async () => {
      if (document.visibilityState !== 'visible' || accessExpiresAt() - Date.now() > 60_000) return;
      const s = await refreshSession();
      if (s) { setTenant(s.tenant); schedule(); } else apply(null);
    };
    schedule();
    document.addEventListener('visibilitychange', onVisible);
    return () => { window.clearTimeout(timer.current); document.removeEventListener('visibilitychange', onVisible); };
  }, [status, apply]);

  // 3) Cross-tab sync and server-driven sign-out.
  useEffect(() => {
    const onSignedOut = () => apply(null);
    authEvents.addEventListener('signedout', onSignedOut);
    const onMsg = async (e: MessageEvent<{ type: 'logout' | 'tenant-switched' }>) => {
      if (e.data.type === 'logout') apply(null);
      if (e.data.type === 'tenant-switched') apply(await refreshSession()); // cookie now carries the new tenant
    };
    channel?.addEventListener('message', onMsg);
    return () => { authEvents.removeEventListener('signedout', onSignedOut); channel?.removeEventListener('message', onMsg); };
  }, [apply]);

  const fromPath = (location.state as { from?: string } | null)?.from;

  const login = useCallback(async (email: string, password: string, redirectTo?: string) => {
    apply(await loginRequest(email, password));
    navigate(redirectTo ?? fromPath ?? '/dashboard', { replace: true });
  }, [apply, navigate, fromPath]);

  const signup = useCallback(async (input: { email: string; password: string; full_name: string; goal?: string }) => {
    apply(await signupRequest(input));
    navigate(fromPath ?? '/dashboard', { replace: true });
  }, [apply, navigate, fromPath]);

  const logout = useCallback(async () => {
    await logoutRequest();
    channel?.postMessage({ type: 'logout' });
    apply(null);
    navigate('/login', { replace: true });
  }, [apply, navigate]);

  const switchTenant = useCallback(async (tenantId: string) => {
    const s = await switchTenantRequest(tenantId);
    setUser(s.user); setTenant(s.tenant);
    channel?.postMessage({ type: 'tenant-switched' });
    navigate('/dashboard', { replace: true }); // never leave the user on a page that belonged to the old tenant
  }, [navigate]);

  const value = useMemo<AuthValue>(
    () => ({ status, user, tenant, tenants, login, signup, logout, switchTenant, reloadTenants }),
    [status, user, tenant, tenants, login, signup, logout, switchTenant, reloadTenants],
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
}
