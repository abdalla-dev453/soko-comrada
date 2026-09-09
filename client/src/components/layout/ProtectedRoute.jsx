import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "../../hooks/useAuth";
import { SectionLoader } from "../common/Loader";

/**
 * Wraps a set of routes that require an authenticated session.
 * Usage in App.jsx:
 *
 *   <Route element={<ProtectedRoute />}>
 *     <Route path="/dashboard" element={<Dashboard />} />
 *   </Route>
 *
 * While the auth session is bootstrapping (page refresh with a
 * stored token) we show a loader instead of bouncing to /login and
 * back — avoids a flash of the login page for an already-logged-in
 * person.
 */
export function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return <SectionLoader label="Checking your session…" />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}

/** Inverse guard for auth pages (login/register) — an already-logged-in
 * person shouldn't see the login form again. */
export function GuestOnlyRoute() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <SectionLoader label="Checking your session…" />;
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}