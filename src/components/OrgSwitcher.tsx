import { useState } from 'react';
import { apiFetch } from '../lib/api';
import { useAuth } from '../auth/AuthContext';

export function OrgSwitcher() {
  const { tenant, tenants, switchTenant, reloadTenants } = useAuth();
  const [creating, setCreating] = useState(false);
  const [name, setName] = useState('');
  const [error, setError] = useState<string | null>(null);

  if (!tenant) return null;

  async function createTeam(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      const { tenant_id } = await apiFetch<{ tenant_id: string }>('/orgs', { method: 'POST', json: { name } });
      await reloadTenants();
      await switchTenant(tenant_id);
      setCreating(false);
      setName('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not create team');
    }
  }

  return (
    <div className="space-y-2">
      <label className="block text-xs font-medium uppercase tracking-wide text-slate-500" htmlFor="org-switcher">Workspace</label>
      <select
        id="org-switcher"
        className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm"
        value={tenant.id}
        onChange={(e) => void switchTenant(e.target.value)}
      >
        {tenants.map((t) => (
          <option key={t.id} value={t.id}>{t.is_personal ? 'Personal' : t.name} · {t.role}</option>
        ))}
      </select>
      {creating ? (
        <form onSubmit={createTeam} className="flex gap-2">
          <input
            className="min-w-0 flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm"
            placeholder="Team name" value={name} minLength={2} maxLength={120} required
            onChange={(e) => setName(e.target.value)}
          />
          <button className="rounded-md bg-indigo-600 px-3 py-2 text-sm font-medium text-white" type="submit">Create</button>
        </form>
      ) : (
        <button className="text-sm text-indigo-600 hover:underline" onClick={() => setCreating(true)}>+ New team</button>
      )}
      {error && <p className="text-xs text-red-600">{error}</p>}
    </div>
  );
}
