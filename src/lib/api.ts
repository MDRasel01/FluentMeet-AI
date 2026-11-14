/**
 * Browser API client. The access token lives in module memory only (never localStorage), so XSS cannot
 * exfiltrate a long-lived credential. The refresh token is an HTTP-only SameSite=Strict cookie.
 */
const API = ((import.meta as any).env?.VITE_API_URL as string | undefined) ?? 'http://localhost:8000';

export interface User { id: string; email: string; full_name: string; goal: string | null; avatar_url: string | null }
export interface Tenant { id: string; name: string; slug: string; tier: 'free' | 'pro' | 'team' | 'enterprise'; role: 'owner' | 'admin' | 'member' }
export interface SessionOut { access_token: string; expires_in: number; user: User; tenant: Tenant }

export class ApiError extends Error {
  constructor(public status: number, public detail: string) {
    super(detail);
  }
}

let access: { token: string; exp: number } | null = null;
let inflight: Promise<SessionOut | null> | null = null;
export const authEvents = new EventTarget(); // dispatches "signedout" when refresh fails

export function accessExpiresAt(): number {
  return access?.exp ?? 0;
}

function remember(s: SessionOut): void {
  access = { token: s.access_token, exp: Date.now() + s.expires_in * 1000 };
}

export function clearAccess(): void {
  access = null;
}

async function errorOf(r: Response): Promise<ApiError> {
  const j = await r.json().catch(() => ({}));
  return new ApiError(r.status, typeof j.detail === 'string' ? j.detail : r.statusText);
}

/** Rotates the refresh cookie. Web Locks serialises tabs so two tabs never replay the same cookie. */
export async function refreshSession(): Promise<SessionOut | null> {
  if (inflight) return inflight;
  if (typeof navigator !== 'undefined' && navigator.locks) {
    inflight = (async () => {
      try {
        const result = await navigator.locks.request('fm-refresh', async () => {
          const r = await fetch(`${API}/api/v1/auth/refresh`, {
            method: 'POST',
            credentials: 'include',
            headers: { 'X-Requested-With': 'fluentmeet' },
          });
          if (!r.ok) {
            clearAccess();
            return null;
          }
          const s = (await r.json()) as SessionOut;
          remember(s);
          return s;
        });
        return result as SessionOut | null;
      } catch (_) {
        return null;
      } finally {
        inflight = null;
      }
    })();
    return inflight;
  }
  return null;
}

export async function apiFetch<T>(path: string, init: RequestInit & { json?: unknown } = {}): Promise<T> {
  if (access && access.exp - Date.now() < 15_000) await refreshSession(); // refresh before it expires, not after a 401
  const send = () =>
    fetch(`${API}/api/v1${path}`, {
      ...init,
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'fluentmeet',
        ...(access ? { Authorization: `Bearer ${access.token}` } : {}),
        ...(init.headers ?? {}),
      },
      body: init.json === undefined ? init.body : JSON.stringify(init.json),
    });
  let r = await send();
  if (r.status === 401) {
    const s = await refreshSession();
    if (!s) {
      authEvents.dispatchEvent(new Event('signedout'));
      throw new ApiError(401, 'session_expired');
    }
    r = await send();
  }
  if (!r.ok) throw await errorOf(r);
  return r.status === 204 ? (undefined as T) : ((await r.json()) as T);
}

async function authCall(path: string, json?: unknown): Promise<SessionOut> {
  const r = await fetch(`${API}/api/v1/auth${path}`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'fluentmeet' },
    body: json === undefined ? undefined : JSON.stringify(json),
  });
  if (!r.ok) throw await errorOf(r);
  const s = (await r.json()) as SessionOut;
  remember(s);
  return s;
}

export const loginRequest = (email: string, password: string) => authCall('/login', { email, password });
export const signupRequest = (b: { email: string; password: string; full_name: string; goal?: string }) => authCall('/signup', b);

export async function logoutRequest(): Promise<void> {
  await fetch(`${API}/api/v1/auth/logout`, { method: 'POST', credentials: 'include', headers: { 'X-Requested-With': 'fluentmeet' } }).catch(() => undefined);
  clearAccess();
}

export async function switchTenantRequest(tenantId: string): Promise<SessionOut> {
  // Needs the current access token (membership proof) and the refresh cookie (rotated server side).
  const s = await apiFetch<SessionOut>('/auth/switch-tenant', { method: 'POST', json: { tenant_id: tenantId } });
  remember(s);
  return s;
}
