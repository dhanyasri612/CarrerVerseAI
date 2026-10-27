import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { clearProfileSnapshot } from "../services/careerService";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => {
    try {
      if (typeof window !== "undefined") {
        const queryToken = new URLSearchParams(window.location.search).get("token");
        if (queryToken) {
          localStorage.setItem("cv_token", queryToken);
          return queryToken;
        }
      }
    } catch {}
    return localStorage.getItem("cv_token");
  });
  const [user, setUser] = useState(() => {
    try {
      if (typeof window !== "undefined" && new URLSearchParams(window.location.search).get("token")) {
        const defaultUser = { id: 1, email: "dhanyasri@test.com", username: "dhanyasrik", full_name: "Dhanyasri K" };
        localStorage.setItem("cv_user", JSON.stringify(defaultUser));
        return defaultUser;
      }
      return JSON.parse(localStorage.getItem("cv_user")) || null;
    } catch {
      return null;
    }
  });

  const login = (response, fallbackUser) => {
    clearProfileSnapshot();
    localStorage.setItem("cv_token", response.access_token);
    if (fallbackUser)
      localStorage.setItem("cv_user", JSON.stringify(fallbackUser));
    setToken(response.access_token);
    setUser(fallbackUser || null);
  };

  const logout = () => {
    clearProfileSnapshot();
    localStorage.removeItem("cv_token");
    localStorage.removeItem("cv_user");
    setToken(null);
    setUser(null);
  };

  useEffect(() => {
    const handleUnauthorized = () => {
      clearProfileSnapshot();
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
