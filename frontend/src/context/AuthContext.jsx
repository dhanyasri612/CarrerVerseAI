import { createContext, useContext, useEffect, useMemo, useState } from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("cv_token"));
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("cv_user")) || null;
    } catch {
      return null;
    }
  });

  const login = (response, fallbackUser) => {
    localStorage.setItem("cv_token", response.access_token);
    if (fallbackUser)
      localStorage.setItem("cv_user", JSON.stringify(fallbackUser));
    setToken(response.access_token);
    setUser(fallbackUser || null);
  };

  const logout = () => {
    localStorage.removeItem("cv_token");
    localStorage.removeItem("cv_user");
    setToken(null);
    setUser(null);
  };

  useEffect(() => {
    const handleUnauthorized = () => {
      setToken(null);
      setUser(null);
    };
    window.addEventListener("cv:logout", handleUnauthorized);
    return () => window.removeEventListener("cv:logout", handleUnauthorized);
  }, []);

  const value = useMemo(
    () => ({ token, user, isAuthenticated: Boolean(token), login, logout }),
    [token, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
