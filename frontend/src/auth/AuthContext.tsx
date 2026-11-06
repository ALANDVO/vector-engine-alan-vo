/**
 * Authentication context for managing user session.
 */
import { createContext, useContext, useState, useEffect, ReactNode, useCallback } from "react";
import {
  fetchUser,
  type UserInfo,
  type TokenResponse,
} from "../api/client";

interface AuthContextType {
  user: UserInfo | null;
  tokens: TokenResponse | null;
  loading: boolean;
  error: string | null;
  login: (redirectUri: string) => Promise<void>;
  logout: () => Promise<void>;
  setTokens: (tokens: TokenResponse) => void;
  clearAuth: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const STORAGE_KEY = "vector-engine-auth";

function getStoredAuth(): { user: UserInfo | null; tokens: TokenResponse | null } {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      return JSON.parse(stored);
    }
  } catch {
    // Ignore parse errors
  }
  return { user: null, tokens: null };
}

function setStoredAuth(user: UserInfo | null, tokens: TokenResponse | null) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ user, tokens }));
  } catch {
    // Ignore storage errors
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserInfo | null>(null);
  const [tokens, setTokensState] = useState<TokenResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const { user: storedUser, tokens: storedTokens } = getStoredAuth();
    if (storedUser && storedTokens) {
      setUser(storedUser);
      setTokensState(storedTokens);
    }
    setLoading(false);
  }, []);

  const setTokens = useCallback((newTokens: TokenResponse) => {
    setTokensState(newTokens);
    if (newTokens.access_token) {
      try {
        const payload = JSON.parse(atob(newTokens.access_token.split(".")[1]));
        const userInfo: UserInfo = {
          id: payload.sub || "",
          email: payload.email || "",
          username: payload.preferred_username || "",
          full_name: payload.name,
          avatar_url: payload.picture,
          email_verified: payload.email_verified || false,
          roles: payload.realm_access?.roles ? JSON.stringify(payload.realm_access.roles) : undefined,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };
        setUser(userInfo);
        setStoredAuth(userInfo, newTokens);
      } catch {
        setStoredAuth(null, newTokens);
      }
    }
  }, []);

  const clearAuth = useCallback(() => {
    setUser(null);
    setTokensState(null);
    setStoredAuth(null, null);
  }, []);

  const login = useCallback(async (redirectUri: string) => {
    setError(null);
    try {
      const { initiateLogin } = await import("../api/client");
      const { auth_url } = await initiateLogin(redirectUri);
      window.location.href = auth_url;
    } catch (e) {
      setError(e instanceof Error ? e.message : "Login failed");
      throw e;
    }
  }, []);

  const logout = useCallback(async () => {
    setError(null);
    try {
      const { logoutKeycloak } = await import("../api/client");
      const idTokenHint = tokens?.access_token;
      await logoutKeycloak(idTokenHint, window.location.origin);
      clearAuth();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Logout failed");
      clearAuth();
    }
  }, [tokens, clearAuth]);

  return (
    <AuthContext.Provider value={{ user, tokens, loading, error, login, logout, setTokens, clearAuth }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
