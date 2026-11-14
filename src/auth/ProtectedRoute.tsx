import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from './AuthContext';

/**
 * Usage:
 *   <AuthProvider>
 *     <Routes>
 *       <Route path="/login" element={<LoginPage />} />
 *       <Route path="/accept-invite" element={<AcceptInvite />} />
 *       <Route element={<ProtectedRoute />}>
 *         <Route path="/dashboard" element={<Dashboard />} />
 *         <Route element={<RoleGuard allow={['owner', 'admin']} />}>
 *           <Route path="/team" element={<TeamSettings />} />
 *         </Route>
 *       </Route>
 *     </Routes>
 *   </AuthProvider>
 */
export function ProtectedRoute() {
  const { status } = useAuth();
  const location = useLocation();
  if (status === 'loading') return <div className="grid min-h-screen place-items-center text-sm text-slate-500">Loading…</div>;
  if (status === 'unauthenticated') {
    return <Navigate to="/login" replace state={{ from: location.pathname + location.search }} />;
  }
  return <Outlet />;
}

export function RoleGuard({ allow, redirectTo = '/dashboard' }: { allow: Array<'owner' | 'admin' | 'member'>; redirectTo?: string }) {
  const { tenant } = useAuth();
  // UI convenience only: the API and RLS enforce the real permission on every request.
  if (!tenant || !allow.includes(tenant.role)) return <Navigate to={redirectTo} replace />;
  return <Outlet />;
}
