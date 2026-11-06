import { useState, useEffect } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./auth/AuthContext";
import { AuthCallback } from "./auth/AuthCallback";
import { fetchHealth, fetchDbHealth, type HealthResponse, type DbHealthResponse } from "./api/client";

function HealthDashboard() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [dbHealth, setDbHealth] = useState<DbHealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadHealth() {
      try {
        setLoading(true);
        const [h, db] = await Promise.all([fetchHealth(), fetchDbHealth()]);
        setHealth(h);
        setDbHealth(db);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    }
    loadHealth();
  }, []);

  return (
    <div className="container">
      <header style={{ marginBottom: "2rem" }}>
        <h1>vector-engine-alan-vo</h1>
        <p style={{ color: "#718096" }}>Vector embedding and similarity search engine for AI/ML applications</p>
      </header>

      <section className="card">
        <h2>Application Health</h2>
        {loading ? (
          <p className="loading">Checking...</p>
        ) : error ? (
          <div className="status-error">{error}</div>
        ) : health ? (
          <div className="status-ok">
            <pre>{JSON.stringify(health, null, 2)}</pre>
          </div>
        ) : null}
      </section>

      <section className="card">
        <h2>Database Health</h2>
        {loading ? (
          <p className="loading">Checking...</p>
        ) : dbHealth ? (
          dbHealth.status === "ok" ? (
            <div className="status-ok">
              <pre>{JSON.stringify(dbHealth, null, 2)}</pre>
            </div>
          ) : (
            <div className="status-error">
              <pre>{JSON.stringify(dbHealth, null, 2)}</pre>
            </div>
          )
        ) : null}
      </section>

      <footer style={{ marginTop: "2rem", color: "#a0aec0", fontSize: "0.875rem" }}>
        <p>Alan Vo &lt;alanvo@gmail.com&gt; | AI &amp; Machine Learning</p>
      </footer>
    </div>
  );
}

function LoginPage() {
  const { login, loading: authLoading } = useAuth();

  const handleLogin = async () => {
    const redirectUri = `${window.location.origin}/auth/callback`;
    await login(redirectUri);
  };

  return (
    <div className="container" style={{ maxWidth: "400px", margin: "4rem auto", textAlign: "center" }}>
      <h1>Sign in to vector-engine</h1>
      <p style={{ color: "#718096", marginBottom: "2rem" }}>
        Use your Keycloak account to access the vector engine dashboard.
      </p>
      <button
        onClick={handleLogin}
        disabled={authLoading}
        className="btn-primary"
        style={{
          padding: "0.75rem 1.5rem",
          fontSize: "1rem",
          backgroundColor: "#3182ce",
          color: "white",
          border: "none",
          borderRadius: "4px",
          cursor: authLoading ? "not-allowed" : "pointer",
          opacity: authLoading ? 0.7 : 1,
        }}
      >
        {authLoading ? "Redirecting..." : "Sign in with Keycloak"}
      </button>
    </div>
  );
}

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="container" style={{ textAlign: "center", padding: "4rem" }}>
        <p className="loading">Loading...</p>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

function App() {
  const { user, logout } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/auth/callback" element={<AuthCallback />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <div className="container">
              <header style={{ marginBottom: "2rem", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <h1>vector-engine-alan-vo</h1>
                  <p style={{ color: "#718096" }}>Vector embedding and similarity search engine for AI/ML applications</p>
                </div>
                {user && (
                  <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
                    <span style={{ color: "#4a5568" }}>
                      Signed in as {user.username || user.email}
                    </span>
                    <button
                      onClick={logout}
                      className="btn-secondary"
                      style={{
                        padding: "0.5rem 1rem",
                        backgroundColor: "#e53e3e",
                        color: "white",
                        border: "none",
                        borderRadius: "4px",
                        cursor: "pointer",
                      }}
                    >
                      Sign out
                    </button>
                  </div>
                )}
              </header>

              <HealthDashboard />
            </div>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

export default App;