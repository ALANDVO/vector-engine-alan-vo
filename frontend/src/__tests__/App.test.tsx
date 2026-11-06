/// <reference types="@testing-library/jest-dom" />
import { render, screen, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "../auth/AuthContext";
import App from "../App";

function renderApp() {
  return render(
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  );
}

describe("App", () => {
  it("renders login page when not authenticated", () => {
    renderApp();
    expect(screen.getByText(/Sign in to vector-engine/i)).toBeInTheDocument();
    expect(screen.getByText(/Use your Keycloak account/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Sign in with Keycloak/i })).toBeInTheDocument();
  });

  it("renders login button", () => {
    renderApp();
    const button = screen.getByRole("button", { name: /Sign in with Keycloak/i });
    expect(button).toBeInTheDocument();
    expect(button).not.toBeDisabled();
  });

  it("has correct title in login page", () => {
    renderApp();
    expect(screen.getByText(/vector-engine/i)).toBeInTheDocument();
  });
});