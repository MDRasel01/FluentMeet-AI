import { useEffect, useRef, useState } from 'react';
import { Navigate, useLocation, useNavigate, useSearchParams } from 'react-router-dom';
import { apiFetch, ApiError } from '../../../../../src/lib/api';
import { useAuth } from '../../../../../src/auth/AuthContext';

export default function AcceptInvite() {
  const [params] = useSearchParams();
  const token = params.get('token') ?? '';
  const { status, switchTenant } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const started = useRef(false);

  useEffect(() => {
    if (status !== 'authenticated' || !token || started.current) return;
    started.current = true; // the token is single use: never submit it twice (React strict mode)
    apiFetch<{ tenant_id: string }>('/orgs/invitations/accept', { method: 'POST', json: { token } })
      .then(async ({ tenant_id }) => { await switchTenant(tenant_id); navigate('/dashboard', { replace: true }); })
      .catch((e) => setError(e instanceof ApiError && e.detail === 'no_seats_available'
        ? 'This team has no free seats. Ask the owner to add one.'
        : 'This invitation is invalid, expired, or was sent to a different email address.'));
  }, [status, token, switchTenant, navigate]);

  if (!token) return <p className="p-8 text-center">Missing invitation token.</p>;
  if (status === 'unauthenticated') {
    // Sign in (or sign up with the invited email), then come straight back here.
    return <Navigate to="/login" replace state={{ from: location.pathname + location.search }} />;
  }
  return <p className="p-8 text-center text-sm">{error ?? 'Joining your team…'}</p>;
}
