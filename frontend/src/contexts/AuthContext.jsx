import { createContext, useState, useEffect, useCallback } from "react";
import { loginUser, registerUser, getMe } from "../api/backend";

export const AuthContext = createContext(null);

export default function AuthProvider({ children }) {
  const hasToken = Boolean(localStorage.getItem("token"));
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(hasToken);

  useEffect(() => {
    if (!hasToken) return;

    let cancelled = false;

    getMe()
      .then((payload) => {
        if (!cancelled) setUser(payload.data);
      })
      .catch(() => {
        if (!cancelled) localStorage.removeItem("token");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [hasToken]);

  const login = useCallback(async (email, password) => {
    const payload = await loginUser(email, password);
    localStorage.setItem("token", payload.data.token);
    setUser(payload.data.user);
    return payload;
  }, []);

  const register = useCallback(async (name, email, password) => {
    const payload = await registerUser(name, email, password);
    localStorage.setItem("token", payload.data.token);
    setUser(payload.data.user);
    return payload;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
