import { createContext, useCallback, useEffect, useMemo, useState } from "react";

import * as authApi from "../api/auth";
import { getStoredTokens } from "../api/client";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [status, setStatus] = useState("loading"); // loading | authenticated | anonymous

  useEffect(() => {
    let cancelled = false;

    async function bootstrap() {
      const tokens = getStoredTokens();
      if (!tokens?.access_token) {
        if (!cancelled) setStatus("anonymous");
        return;
      }
      try {
        const me = await authApi.fetchMe();
        if (!cancelled) {
          setUser(me);
          setStatus("authenticated");
        }
      } catch {
        if (!cancelled) setStatus("anonymous");
      }
    }

    bootstrap();
    return () => {
      cancelled = true;
    };
  }, []);

  const login = useCallback(async (email, password) => {
    const loggedInUser = await authApi.login(email, password);
    setUser(loggedInUser);
    setStatus("authenticated");
    return loggedInUser;
  }, []);

  const register = useCallback(async (payload) => {
    const registeredUser = await authApi.register(payload);
    setUser(registeredUser);
    setStatus("authenticated");
    return registeredUser;
  }, []);

  const logout = useCallback(() => {
    authApi.logout();
    setUser(null);
    setStatus("anonymous");
  }, []);

  const refreshProfile = useCallback(async () => {
    const me = await authApi.fetchMe();
    setUser(me);
    return me;
  }, []);

  const value = useMemo(
    () => ({
      user,
      status,
      isAuthenticated: status === "authenticated",
      isLoading: status === "loading",
      login,
      register,
      logout,
      refreshProfile,
    }),
    [user, status, login, register, logout, refreshProfile]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}