import { useCallback, useEffect, useState } from 'react';
import { apiFetch, ApiError } from '../../../../../src/lib/api';
import { useAuth } from '../../../../../src/auth/AuthContext';

interface Member { id: string; email: string; full_name: string; role: 'owner' | 'admin' | 'member' }
interface Invite { id: string; email: string; role: 'admin' | 'member'; expires_at: string }

const ERRORS: Record<string, string> = {
  no_seats_available: 'No seats left. Upgrade your plan or revoke a pending invitation.',
  already_a_member: 'That person is already on the team.',
  invitation_already_pending: 'An invitation is already pending for that email.',
  only_owner_can_invite_admins: 'Only the owner can invite admins.',
};

export default function TeamSettings() {
  const { tenant, user } = useAuth();
  const [members, setMembers] = useState<Member[]>([]);
  const [invites, setInvites] = useState<Invite[]>([]);
  const [maxSeats, setMaxSeats] = useState(1);
  const [email, setEmail] = useState('');
  const [role, setRole] = useState<'member' | 'admin'>('member');
  const [message, setMessage] = useState<string | null>(null);

  const load = useCallback(async () => {
    const [m, i] = await Promise.all([
      apiFetch<{ max_seats: number; members: Member[] }>('/orgs/current/members'),
      apiFetch<Invite[]>('/orgs/current/invitations'),
    ]);
    setMembers(m.members); setMaxSeats(m.max_seats); setInvites(i);
  }, []);

  useEffect(() => { void load(); }, [load, tenant?.id]);

  const run = async (fn: () => Promise<unknown>) => {
    setMessage(null);
    try { await fn(); await load(); }
    catch (e: any) { setMessage(e instanceof ApiError ? (ERRORS[e.detail] ?? e.detail) : 'Something went wrong'); }
  };

  const used = members.length + invites.length;
  const isOwner = tenant?.role === 'owner';

  return (
    <div className="mx-auto max-w-3xl space-y-8 p-6">
      <header>
        <h1 className="text-xl font-semibold">Team · {tenant?.name}</h1>
        <p className="mt-1 text-sm text-slate-600">
          Seats used: <strong>{used}</strong> of <strong>{maxSeats}</strong> (members plus pending invitations)
        </p>
        <div className="mt-2 h-2 w-full overflow-hidden rounded bg-slate-200">
          <div className="h-full bg-indigo-600" style={{ width: `${Math.min(100, (used / maxSeats) * 100)}%` }} />
        </div>
      </header>

      <form className="flex flex-wrap gap-2" onSubmit={(e) => { e.preventDefault(); void run(async () => {
        await apiFetch('/orgs/current/invitations', { method: 'POST', json: { email, role } });
        setEmail('');
      }); }}>
        <input type="email" required placeholder="teammate@company.com" value={email} onChange={(e) => setEmail(e.target.value)}
          className="min-w-0 flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm" />
        <select value={role} onChange={(e) => setRole(e.target.value as 'member' | 'admin')} className="rounded-md border border-slate-300 px-2 py-2 text-sm">
          <option value="member">Member</option>
          {isOwner && <option value="admin">Admin</option>}
        </select>
        <button className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50" disabled={used >= maxSeats}>Invite</button>
      </form>
      {message && <p role="alert" className="text-sm text-red-600">{message}</p>}

      <section>
        <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-500">Members</h2>
        <ul className="divide-y rounded-md border">
          {members.map((m) => (
            <li key={m.id} className="flex items-center justify-between gap-3 p-3 text-sm">
              <span><span className="font-medium">{m.full_name || m.email}</span><span className="ml-2 text-slate-500">{m.email}</span></span>
              <span className="flex items-center gap-2">
                {m.role === 'owner' || m.id === user?.id ? (
                  <span className="rounded bg-slate-100 px-2 py-1 text-xs">{m.role}</span>
                ) : (
                  <>
                    <select value={m.role} className="rounded border px-2 py-1 text-xs" disabled={!isOwner && m.role === 'admin'}
                      onChange={(e) => void run(() => apiFetch(`/orgs/current/members/${m.id}`, { method: 'PATCH', json: { role: e.target.value } }))}>
                      <option value="member">member</option>
                      {isOwner && <option value="admin">admin</option>}
                    </select>
                    {(isOwner || m.role === 'member') && (
                      <button className="text-xs text-red-600 hover:underline"
                        onClick={() => window.confirm(`Remove ${m.email}?`) && void run(() => apiFetch(`/orgs/current/members/${m.id}`, { method: 'DELETE' }))}>
                        Remove
                      </button>
                    )}
                  </>
                )}
              </span>
            </li>
          ))}
        </ul>
      </section>

      {invites.length > 0 && (
        <section>
          <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-500">Pending invitations</h2>
          <ul className="divide-y rounded-md border">
            {invites.map((i) => (
              <li key={i.id} className="flex items-center justify-between p-3 text-sm">
                <span>{i.email} <span className="text-slate-500">({i.role}, expires {new Date(i.expires_at).toLocaleDateString()})</span></span>
                <button className="text-xs text-red-600 hover:underline" onClick={() => void run(() => apiFetch(`/orgs/current/invitations/${i.id}`, { method: 'DELETE' }))}>Revoke</button>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
