import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { apiLogin, apiLogout, apiMe } from "../api/auth";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);       // {user_id, role} | null
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  async function refresh() {
    setError(null);
    setLoading(true);
    try {
      const u = await apiMe();
      setUser(u);
    } catch (e) {
      setUser(null);
      setError(e.message || String(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh(); // restore session on first load
  }, []);

  async function login(email, password) {
    setError(null);
    await apiLogin(email, password);
    const u = await apiMe();
    setUser(u);
    return u;
  }

  async function logout() {
    setError(null);
    await apiLogout();
    setUser(null);
  }

  const value = useMemo(() => ({
    user,
    loading,
    error,
    login,
    logout,
    refresh,
    isAuthed: !!user,
    isAdmin: user?.role === "ADMIN",
  }), [user, loading, error]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
