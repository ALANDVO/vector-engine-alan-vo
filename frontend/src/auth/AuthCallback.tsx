/**
 * Auth callback component to handle OIDC redirect from Keycloak.
 */
import { useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { useAuth } from "./AuthContext";
import { type TokenResponse } from "../api/client";

export function AuthCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { setTokens, clearAuth } = useAuth();

  useEffect(() => {
    const accessToken = searchParams.get("access_token");
    const tokenType = searchParams.get("token_type");
    const expiresIn = searchParams.get("expires_in");
    const refreshToken = searchParams.get("refresh_token");
    const error = searchParams.get("error");

    if (error) {
      clearAuth();
      navigate("/", { replace: true });
      return;
    }

    if (accessToken && tokenType && expiresIn) {
      const tokens: TokenResponse = {
        access_token: accessToken,
        token_type: tokenType,
        expires_in: parseInt(expiresIn, 10),
        refresh_token: refreshToken || undefined,
      };
      setTokens(tokens);
      navigate("/", { replace: true });
    } else {
      // No tokens in URL, might be initial load or error
      navigate("/", { replace: true });
    }
  }, [searchParams, navigate, setTokens, clearAuth]);

  return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh" }}>
      <div className="card" style={{ textAlign: "center" }}>
        <h2>Completing sign in...</h2>
        <p style={{ color: "#718096" }}>Please wait while we process your authentication.</p>
      </div>
    </div>
  );
}
