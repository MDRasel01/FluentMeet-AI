import React, { type ReactNode } from 'react';
import { useAuth } from './AuthContext';

export function ProtectedRoute({ children, fallback }: { children: ReactNode; fallback?: ReactNode }) {
  const { status } = useAuth();
  if (status === 'loading') {
    return <div className="grid min-h-screen place-items-center text-sm text-slate-500">Loading…</div>;
  }
  if (status === 'unauthenticated') {
    return fallback ? <>{fallback}</> : <div className="p-8 text-center text-sm text-slate-500">Please sign in to access this page.</div>;
  }
  return <>{children}</>;
}

export function RoleGuard({
  allow,
  children,
  fallback,
}: {
  allow: Array<'owner' | 'admin' | 'member'>;
  children: ReactNode;
  fallback?: ReactNode;
}) {
  const { tenant } = useAuth();
  // UI convenience only: the API and RLS enforce the real permission on every request.
  if (!tenant || !allow.includes(tenant.role)) {
    return fallback ? <>{fallback}</> : null;
  }
  return <>{children}</>;
}
