const API_BASE = import.meta.env.VITE_API_BASE || "/health";

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

export async function fetchHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE}`, {
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    throw new Error(`Health check failed: ${response.status}`);
  }
  return response.json();
}

export async function fetchDbHealth(): Promise<DbHealthResponse> {
  const response = await fetch(`${API_BASE}/db`, {
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    throw new Error(`DB health check failed: ${response.status}`);
  }
  return response.json();
}