import { useEffect, useRef, useState } from 'react';
import { apiFetch, ApiError } from '../../../../../src/lib/api';
import { useAuth } from '../../../../../src/auth/AuthContext';

export default function AcceptInvite() {
  const token = typeof window !== 'undefined'
    ? new URLSearchParams(window.location.search).get('token') ?? ''
    : '';
  const { status, switchTenant } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const started = useRef(false);

  useEffect(() => {
    if (status !== 'authenticated' || !token || started.current) return;
    started.current = true; // the token is single use: never submit it twice (React strict mode)
    apiFetch<{ tenant_id: string }>('/orgs/invitations/accept', { method: 'POST', json: { token } })
      .then(async ({ tenant_id }) => {
        await switchTenant(tenant_id);
        if (typeof window !== 'undefined') {
          window.location.href = '/#dashboard';
        }
      })
      .catch((e) => setError(e instanceof ApiError && e.detail === 'no_seats_available'
        ? 'This team has no free seats. Ask the owner to add one.'
        : 'This invitation is invalid, expired, or was sent to a different email address.'));
  }, [status, token, switchTenant]);

  if (!token) return <p className="p-8 text-center text-slate-400">Missing invitation token.</p>;
  if (status === 'unauthenticated') {
    return (
      <div className="p-8 text-center max-w-md mx-auto space-y-4">
        <p className="text-slate-200 font-medium">Please sign in to accept this team invitation.</p>
        <button
          onClick={() => {
            if (typeof window !== 'undefined') {
              window.location.href = '/?action=login';
            }
          }}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-semibold transition"
        >
          Sign In to Continue
        </button>
      </div>
    );
  }
  return <p className="p-8 text-center text-sm text-slate-300">{error ?? 'Joining your team…'}</p>;
}
