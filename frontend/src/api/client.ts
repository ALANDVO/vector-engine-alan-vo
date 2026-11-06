const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

export interface HealthResponse {
  status: string;
  app: string;
  version: string;
}

export interface DbHealthResponse {
  status: string;
  database: string;
  detail?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  refresh_token?: string;
  scope?: string;
}

export interface UserInfo {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  avatar_url?: string;
  email_verified: boolean;
  roles?: string;
  created_at: string;
  updated_at: string;
  last_login_at?: string;
}

export interface LoginResponse {
  auth_url: string;
  state: string;
}

export async function fetchHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE}/health`, {
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    throw new Error(`Health check failed: ${response.status}`);
  }
  return response.json();
}

export async function fetchDbHealth(): Promise<DbHealthResponse> {
  const response = await fetch(`${API_BASE}/health/db`, {
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    throw new Error(`DB health check failed: ${response.status}`);
  }
  return response.json();
}

export async function initiateLogin(redirectUri: string): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE}/auth/login?redirect_uri=${encodeURIComponent(redirectUri)}`, {
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || `Login failed: ${response.status}`);
  }
  return response.json();
}

export async function fetchUser(userId: string): Promise<UserInfo> {
  const response = await fetch(`${API_BASE}/auth/me?user_id=${encodeURIComponent(userId)}`, {
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    throw new Error(`Fetch user failed: ${response.status}`);
  }
  return response.json();
}

export async function logoutKeycloak(
  idTokenHint?: string,
  postLogoutRedirectUri?: string
): Promise<{ logout_url: string }> {
  const params = new URLSearchParams();
  if (idTokenHint) params.append("id_token_hint", idTokenHint);
  if (postLogoutRedirectUri) params.append("post_logout_redirect_uri", postLogoutRedirectUri);
  
  const response = await fetch(`${API_BASE}/auth/logout/keycloak?${params.toString()}`, {
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    throw new Error(`Logout failed: ${response.status}`);
  }
  return response.json();
}