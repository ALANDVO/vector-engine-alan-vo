import { useState, useEffect } from "react";
import { fetchHealth, fetchDbHealth, type HealthResponse, type DbHealthResponse } from "./api/client";

function App() {
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
        <p>Alan Vo <alanvo@gmail.com> | AI & Machine Learning</p>
      </footer>
    </div>
  );
}

export default App;